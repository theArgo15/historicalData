import pandas as pd
import numpy as np
from pathlib import Path
import os
import sys

# historicalData.py svp0 or svp2 or svp3
Machine = (sys.argv[1]).upper()
print(Machine)
p = Path(f"C:/Users/TonyWitt/OneDrive - Evolve/{Machine}/{Machine}_Job_Data")

EPDewPointValues = pd.DataFrame(
    columns=[
        "System",
        "JobId",
        "Num Layers",
        "Max EP Temp",
        "Max EP Humidity",
        "Max ECS Supply Temp",
        "Max ECS Supply Humidity",
        "Max ECS Return Temp",
        "Max ECS Return Humidity",
        "Mean Ambient Temp",
        "Mean Ambient Humidity",
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
roomData["roomHumidity"] = roomData["Moisture (%)"]


counter = 0
for job in os.listdir(p):
    try:
        newColumns = pd.read_excel(
            p / job,
            usecols=[
                "Layer",
                "ECSSupplyTemp",
                "ECSReturnTemp",
                "EPTemp",
                "ECSSupplyHumidity",
                "ECSReturnHumidity",
                "EPHumidity",
            ],
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
                    newColumns["ECSSupplyHumidity"].max(),
                    newColumns["ECSReturnHumidity"].max(),
                    newColumns["EPHumidity"].max(),
                    newColumns["ECSSupplyHumidity"].min(),
                    newColumns["ECSReturnHumidity"].min(),
                    newColumns["EPHumidity"].min(),
                    roomDataDuringJob["roomTemp"].mean(),
                    roomDataDuringJob["roomHumidity"].mean(),
                ]
            ],
            columns=[
                "System",
                "JobId",
                "Num Layers",
                "Max ECS Supply Temp",
                "Max ECS Return Temp",
                "Max EP Temp",
                "Max ECS Supply Humidity",
                "Max ECS Return Humidity",
                "Max EP Humidity",
                "Min ECS Supply Humidity",
                "Min ECS Return Humidity",
                "Min EP Humidity",
                "Mean Ambient Temp",
                "Mean Ambient Humidity",
            ],
        )
        EPDewPointValues = pd.concat([EPDewPointValues, newRow])

    except ValueError:
        counter += 1
        print(counter)

EPDewPointValues.to_csv(f"{Machine} EPDewPointValues.csv", index=False)
print(counter)
