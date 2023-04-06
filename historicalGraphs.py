import pandas as pd
import numpy as np
from pathlib import Path
import os
import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime


# historicalData.py svp0 or svp2 or svp3
def airTunnelPlot(df):
    bulkSetPoint = df.at[0, "PartBulkTempSetPoint"]
    fig, ax = plt.subplots()
    fig.text(
        0.05,
        0.94,
        f"Date: {jobStartDate} \nJobID: {jobStartTime} ({Machine}) \nBulk Setpoint: {bulkSetPoint}",
        fontsize=10,
    )

    ax.plot("TransferCycleCount", "AirTunnelPressure1", data=df, label="Supply Side")
    ax.plot("TransferCycleCount", "AirTunnelPressure2", data=df, label="Return Side")
    ax2 = ax.twinx()
    ax2.plot(
        "TransferCycleCount",
        "AirTunnelActualRPM",
        data=df,
        label="Air Tunnel RPM",
        color="r",
    )
    ax2.set_ylabel("RPM")
    ax2.set_ylim(0, 3500)
    ax2.legend()

    ax.set_xlabel("Transfer Cycle Count")
    ax.set_ylabel("Pressure (MPa)")
    ax.set_title(f"{Machine} {jobStartDate}")
    ax.legend(loc="upper left")
    return fig


def airTunnelTempPlot(df):
    bulkSetPoint = df.at[0, "PartBulkTempSetPoint"]
    fig, ax = plt.subplots()
    fig.text(
        0.05,
        0.94,
        f"Date: {jobStartDate} \nJobID: {jobStartTime} ({Machine}) \nBulk Setpoint: {bulkSetPoint}",
        fontsize=10,
    )

    ax.plot("TransferCycleCount", "AirTunnelTemp1", data=df, label="Supply Side")
    ax.plot("TransferCycleCount", "AirTunnelTemp2", data=df, label="Return Side")
    ax2 = ax.twinx()
    ax2.plot(
        "TransferCycleCount",
        "AirTunnelActualRPM",
        data=df,
        label="Air Tunnel RPM",
        color="r",
    )
    ax2.set_ylabel("RPM")
    ax2.set_ylim(0, 3500)
    ax2.legend()

    ax.set_xlabel("Transfer Cycle Count")
    ax.set_ylabel("Temperature ($^\circ$C)")
    ax.set_title(f"{Machine} {jobStartDate}")
    ax.legend(loc="upper left")
    ax.set_ylim(10, 40)
    return fig


def chilledWaterPlot(df):
    bulkSetPoint = df.at[0, "PartBulkTempSetPoint"]
    fig, ax = plt.subplots()
    fig.text(
        0.05,
        0.94,
        f"Date: {jobStartDate} \nJobID: {jobStartTime} ({Machine}) \nBulk Setpoint: {bulkSetPoint}",
        fontsize=10,
    )
    ax.plot(
        "TransferCycleCount", "WaterTempBuildManagementSupply", data=df, label="Supply"
    )
    ax.plot(
        "TransferCycleCount",
        "WaterTempPostTransfusePlateReturn",
        data=df,
        label="Post Transfuse Plate",
    )
    ax.plot(
        "TransferCycleCount",
        "WaterTempImageHeaterPlateReturn",
        data=df,
        label="Image Heater Plate",
    )
    ax.plot(
        "TransferCycleCount",
        "WaterTempWebFramePlateReturn",
        data=df,
        label="Web Frame Plate",
    )
    ax.plot(
        "TransferCycleCount",
        "WaterTempXStagePlateReturn",
        data=df,
        label="X-Stage Plate",
    )
    ax.plot(
        "TransferCycleCount",
        "WaterTempBuildManagementReturn",
        data=df,
        label="Build Area Heat Exchanger",
    )
    ax.plot(
        "TransferCycleCount",
        "WaterTempAirTunnelReturn",
        data=df,
        label="Air Tunnel Heat Exchanger",
    )

    ax.set_xlabel("Transfer Cycle Count")
    ax.set_ylabel("Temperature ($^\circ$C)")
    ax.set_title(f"{Machine} {jobStartDate}")
    ax.legend(loc="upper left")
    ax.set_ylim(0, 45)
    return fig


if __name__ == "__main__":
    Machine = (sys.argv[1]).upper()
    print(Machine)
    p = Path(f"C:/Users/TonyWitt/OneDrive - Evolve/{Machine}/{Machine}_Job_Data")

    # with PdfPages(f"{Machine}AirTunnelPressures.pdf") as pp:
    # with PdfPages(f"{Machine}ChilledWaterTemps.pdf") as pp:
    with PdfPages(f"{Machine}AirTunnelTemps.pdf") as pp:
        for job in os.listdir(p):
            jobStartTime = int(job[:10])
            jobStartDate = datetime.fromtimestamp(jobStartTime)
            # grab data after date in epoch time
            if jobStartTime > 1669931795:
                df = pd.read_excel(p / job)
                print(f"Appending {job}")
                # fig = airTunnelPlot(df)
                # fig = chilledWaterPlot(df)
                fig = airTunnelTempPlot(df)
                pp.savefig(fig)
                plt.close(fig)
            else:
                pass
