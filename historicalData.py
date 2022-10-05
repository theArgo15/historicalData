import pandas as pd
import numpy as np
from pathlib import Path
import os
import sys

# historicalData.py svp0 or svp2 or svp3
Machine = (sys.argv[1]).upper()
print(Machine)
p = Path(f"C:/Users/TonyWitt/OneDrive - Evolve/{Machine}/{Machine}_Job_Data")

EPTempMaxValues = pd.DataFrame(
    columns=[
        "System",
        "JobId",
        "Num Layers",
        "Max EP Temp",
        "Max ECS Supply Temp",
        "Max ECS Return Temp",
        "Mean Ambient Temp",
    ]
)

# add room reference data
roomData = pd.read_csv(
    "RIC_ROOM_REFERENCE-TempRH--.csv",
    skiprows=range(1, 140000),
    parse_dates=["Date/Time"],
)
roomData["roomTime"] = roomData["Date/Time"].astype("int64") // 1e9
roomData["roomTemp"] = (roomData["Temperature (F)"] - 32) * (5 / 9)


counter = 0
for job in os.listdir(p):
    try:
        newColumns = pd.read_excel(
            p / job, usecols=["Layer", "ECSSupplyTemp", "ECSReturnTemp", "EPTemp"]
        )
        print(f"Saving {job}")
        jobStartTime = int(job[:10])
        jobFinishTime = 10800 + jobStartTime
        roomDataDuringJob = roomData.query(
            f"{jobFinishTime} > roomTime > {jobStartTime}"
        )

        newRow = pd.DataFrame(
            [
                [
                    Machine,
                    job[:10],
                    newColumns["Layer"].max(),
                    newColumns["ECSSupplyTemp"].max(),
                    newColumns["ECSReturnTemp"].max(),
                    newColumns["EPTemp"].max(),
                    roomDataDuringJob["roomTemp"].mean(),
                ]
            ],
            columns=[
                "System",
                "JobId",
                "Num Layers",
                "Max ECS Supply Temp",
                "Max ECS Return Temp",
                "Max EP Temp",
                "Mean Ambient Temp",
            ],
        )
        EPTempMaxValues = pd.concat([EPTempMaxValues, newRow])

    except ValueError:
        counter += 1
        print(counter)

EPTempMaxValues.to_csv(f"{Machine} EPTempMaxValues.csv", index=False)
print(counter)
