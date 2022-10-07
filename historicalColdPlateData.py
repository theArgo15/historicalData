import pandas as pd
import numpy as np
from pathlib import Path
import os
import matplotlib.pyplot as plt
import seaborn

Machine = "SVP2"
p = Path(f"C:/Users/TonyWitt/OneDrive - Evolve/{Machine}/{Machine}_Job_Data")

# create empty df with column names
amalgamatedColdPlateData = pd.DataFrame(
    columns=[
        "System",
        "JobID",
        "TransferCycleCount",
        "Layer",
        "IDriveTorque",
        "TDriveTorque",
        "WaterTempBuildManagementSupply",
        "WaterTempPostTransfusePlateReturn",
        "WaterTempImageHeaterPlateReturn",
        "WaterTempWebFramePlateReturn",
        "WaterTempXStagePlateReturn",
        "WaterTempBuildManagementReturn",
        "WaterTempAirTunnelReturn",
    ]
)
# loop through each job and create df with interested columns
for job in os.listdir(p):
    print(f"Saving {job}")
    try:
        newColumns = pd.read_excel(
            p / job,
            usecols=[
                "TransferCycleCount",
                "Layer",
                "IDriveTorque",
                "TDriveTorque",
                "WaterTempBuildManagementSupply",
                "WaterTempPostTransfusePlateReturn",
                "WaterTempImageHeaterPlateReturn",
                "WaterTempWebFramePlateReturn",
                "WaterTempXStagePlateReturn",
                "WaterTempBuildManagementReturn",
                "WaterTempAirTunnelReturn",
            ],
        )
        newColumns["System"] = "SVP2"
        newColumns["JobID"] = job[:10]

        # put new data into big df
        amalgamatedColdPlateData = pd.concat([amalgamatedColdPlateData, newColumns])
    # if file does not have the specified column, it throws this error
    except ValueError:
        print("ValueError")
# save to csv
amalgamatedColdPlateData.to_csv(f"{Machine} ColdPlateData.csv", index=False)
