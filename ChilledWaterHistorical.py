import pandas as pd
import numpy as np
from pathlib import Path
import os
import sys

# Power by Heater in kW
otherHeatDutyCycle = 0.5
# new platen heaters 3kW old ???
PlatenHeaterPower = 0
Zone1PartHeaterPower = 9
Zone2PartHeaterPower = 9
Zone3PartHeaterPower = 3
Zone4PartHeaterPower = 6
ImageHeaterPower = 18
OtherHeatPower = 19 * otherHeatDutyCycle

# ChilledWaterHistorical.py svp0 or svp2 or svp3 etc.
Machine = (sys.argv[1]).upper()
p = Path(f"C:/Users/TonyWitt/OneDrive - Evolve/{Machine}/{Machine}_Job_Data")
# error counter
counter = 0
# initialize empty df
DeltaTMeanValues = pd.DataFrame(
    columns=[
        "System",
        "JobId",
        "Num Layers",
        "TransfuseDelta",
        "ImageHeaterDelta",
        "WebFrameDelta",
        "XStageDelta",
        "BTMDelta",
        "AirTunnelDelta",
        "MassFlow",
    ]
)
# this reads in job data we care about and summarizes it in a single row added to a second data frame
for job in os.listdir(p):
    # change this epoch time based on jobs we care about
    if int(job[:10]) > 1668002471:
        try:
            newColumns = pd.read_excel(
                p / job,
                usecols=[
                    "Layer",
                    "WaterTempBuildManagementSupply",
                    "WaterTempPostTransfusePlateReturn",
                    "WaterTempImageHeaterPlateReturn",
                    "WaterTempWebFramePlateReturn",
                    "WaterTempXStagePlateReturn",
                    "WaterTempBuildManagementReturn",
                    "WaterTempAirTunnelReturn",
                    "ChilledWaterFlowRate",
                    "PartBulkTempSetPoint",
                    "PlatenCLCDutyCycle",
                    "PartHeatDutyCycleZ1",
                    "PartHeatDutyCycleZ2",
                    "PartHeatDutyCycleZ3",
                    "PartHeatDutyCycleZ4",
                    "ImageHeatDutyCycle",
                ],
            )
            # Replace negative values of PlatenCLC control with 0. We only care about the heater being on
            newColumns.loc[
                newColumns["PlatenCLCDutyCycle"] < 0, "PlatenCLCDutyCycle"
            ] = 0
            # make delta t columns
            newColumns["TransfuseDelta"] = (
                newColumns["WaterTempPostTransfusePlateReturn"]
                - newColumns["WaterTempBuildManagementSupply"]
            )
            newColumns["ImageHeaterDelta"] = (
                newColumns["WaterTempImageHeaterPlateReturn"]
                - newColumns["WaterTempBuildManagementSupply"]
            )
            newColumns["WebFrameDelta"] = (
                newColumns["WaterTempWebFramePlateReturn"]
                - newColumns["WaterTempBuildManagementSupply"]
            )
            newColumns["XStageDelta"] = (
                newColumns["WaterTempXStagePlateReturn"]
                - newColumns["WaterTempBuildManagementSupply"]
            )
            newColumns["BTMDelta"] = (
                newColumns["WaterTempBuildManagementReturn"]
                - newColumns["WaterTempBuildManagementSupply"]
            )
            newColumns["AirTunnelDelta"] = (
                newColumns["WaterTempAirTunnelReturn"]
                - newColumns["WaterTempBuildManagementSupply"]
            )
            print(f"Saving {job}")

            # single row df
            newRow = pd.DataFrame(
                [
                    [
                        Machine,
                        job[:10],
                        newColumns["Layer"].max(),
                        newColumns["TransfuseDelta"].mean(),
                        newColumns["ImageHeaterDelta"].mean(),
                        newColumns["WebFrameDelta"].mean(),
                        newColumns["XStageDelta"].mean(),
                        newColumns["BTMDelta"].mean(),
                        newColumns["AirTunnelDelta"].mean(),
                        # mass flow rate in g/s
                        newColumns["ChilledWaterFlowRate"].mean() * 1000 / 60,
                        newColumns["PartBulkTempSetPoint"].mean(),
                        newColumns["PlatenCLCDutyCycle"].mean(),
                        newColumns["PartHeatDutyCycleZ1"].mean(),
                        newColumns["PartHeatDutyCycleZ2"].mean(),
                        newColumns["PartHeatDutyCycleZ3"].mean(),
                        newColumns["PartHeatDutyCycleZ4"].mean(),
                        newColumns["ImageHeatDutyCycle"].mean(),
                    ]
                ],
                columns=[
                    "System",
                    "JobId",
                    "Num Layers",
                    "TransfuseDelta",
                    "ImageHeaterDelta",
                    "WebFrameDelta",
                    "XStageDelta",
                    "BTMDelta",
                    "AirTunnelDelta",
                    "MassFlow",
                    "PartBulkTempSetPoint",
                    "PlatenCLCDutyCycle",
                    "PartHeatDutyCycleZ1",
                    "PartHeatDutyCycleZ2",
                    "PartHeatDutyCycleZ3",
                    "PartHeatDutyCycleZ4",
                    "ImageHeatDutyCycle",
                ],
            )
            DeltaTMeanValues = pd.concat([DeltaTMeanValues, newRow])

        except ValueError:
            counter += 1
            print(f"{job} did not record flow rate")

# Image heater 4%, Transfuse belt 4%, Web frame 5%, X stage 5%, Air tunnel 36%, BTM 46%
DeltaTMeanValues["AverageTemperatureDelta(C)"] = (
    0.04 * DeltaTMeanValues["ImageHeaterDelta"]
    + 0.04 * DeltaTMeanValues["TransfuseDelta"]
    + 0.05 * DeltaTMeanValues["WebFrameDelta"]
    + 0.05 * DeltaTMeanValues["XStageDelta"]
    + 0.36 * DeltaTMeanValues["AirTunnelDelta"]
    + 0.46 * DeltaTMeanValues["BTMDelta"]
)
# Q = mdot c delta T calculation with mdot being a fraction of flow based on the manual flow meters. We are assuming this distribution is similar for all machines c is 4.2 J
DeltaTMeanValues["AveragePowerRemoved(kW)"] = (
    DeltaTMeanValues["MassFlow"]
    * 4.2
    * DeltaTMeanValues["AverageTemperatureDelta(C)"]
    / 1000
)
# Heat power calculated by heater power duty cycle plus various component estimate. duty cycle in percent, so divide by 100
DeltaTMeanValues["AveragePowerAdded(kW)"] = (
    PlatenHeaterPower * DeltaTMeanValues["PlatenCLCDutyCycle"] / 100
    + Zone1PartHeaterPower * DeltaTMeanValues["PartHeatDutyCycleZ1"] / 100
    + Zone2PartHeaterPower * DeltaTMeanValues["PartHeatDutyCycleZ2"] / 100
    + Zone3PartHeaterPower * DeltaTMeanValues["PartHeatDutyCycleZ3"] / 100
    + Zone4PartHeaterPower * DeltaTMeanValues["PartHeatDutyCycleZ4"] / 100
    + ImageHeaterPower * DeltaTMeanValues["ImageHeatDutyCycle"] / 100
    + OtherHeatPower
)
DeltaTMeanValues.to_csv(f"{Machine} DeltaTMeanValues.csv", index=False)
print(counter)
