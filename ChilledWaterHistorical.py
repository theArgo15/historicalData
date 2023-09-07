import pandas as pd
import numpy as np
from pathlib import Path
import os
import sys

# Power by Heater in kW
otherHeatDutyCycle = 0.5
# new platen heaters 4.32kW for qty 6 rods. old 2.5kW
PlatenHeaterPower = [2.5, 4.32]
# IR lamps are 3kW at 400V. We run at 480V so we limit to 72% duty cycle therfore 100% duty cycle is 4.167kW
Zone1PartHeaterPower = 4.167 * 3
Zone2PartHeaterPower = 4.167 * 3
Zone3PartHeaterPower = 4.167 * 1
Zone4PartHeaterPower = 4.167 * 2
ImageHeaterPower = 4.167 * 6
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
        "AirTunnelPct",
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
                    "AirTunnelPct",
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
                        newColumns["AirTunnelPct"].mean(),
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
                    "AirTunnelPct",
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
# Q = mdot c delta T calculation with mdot being a fraction of flow based on the manual flow meters. We are assuming this distribution is similar for all machines. c is 4.2 J/g degC
c = 4.2

DeltaTMeanValues["ImageHeaterPowerRemoved(kW)"] = (
    0.04
    * DeltaTMeanValues["MassFlow"]
    * c
    * DeltaTMeanValues["ImageHeaterDelta"]
    / 1000
)
DeltaTMeanValues["TransfusePowerRemoved(kW)"] = (
    0.04 * DeltaTMeanValues["MassFlow"] * c * DeltaTMeanValues["TransfuseDelta"] / 1000
)
DeltaTMeanValues["WebFramePowerRemoved(kW)"] = (
    0.05 * DeltaTMeanValues["MassFlow"] * c * DeltaTMeanValues["WebFrameDelta"] / 1000
)
DeltaTMeanValues["XStagePowerRemoved(kW)"] = (
    0.05 * DeltaTMeanValues["MassFlow"] * c * DeltaTMeanValues["XStageDelta"] / 1000
)
DeltaTMeanValues["AirTunnelPowerRemoved(kW)"] = (
    0.36 * DeltaTMeanValues["MassFlow"] * c * DeltaTMeanValues["AirTunnelDelta"] / 1000
)
DeltaTMeanValues["BTMPowerRemoved(kW)"] = (
    0.46 * DeltaTMeanValues["MassFlow"] * c * DeltaTMeanValues["BTMDelta"] / 1000
)

DeltaTMeanValues["AveragePowerRemoved(kW)"] = (
    DeltaTMeanValues["MassFlow"]
    * 4.2
    * DeltaTMeanValues["AverageTemperatureDelta(C)"]
    / 1000
)
# logic for old vs new platen heaters
if Machine == "SVP0" or Machine == "SVP1":
    PlatenHeaterPower = PlatenHeaterPower[0]
else:
    PlatenHeaterPower = PlatenHeaterPower[1]

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

DeltaTMeanValues["Percent Heat Removed By Chillers"] = (
    DeltaTMeanValues["AveragePowerRemoved(kW)"]
    / DeltaTMeanValues["AveragePowerAdded(kW)"]
    * 100
)


DeltaTMeanValues.to_csv(f"{Machine} DeltaTMeanValues.csv", index=False)
print(counter)
