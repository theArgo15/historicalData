import pandas as pd
import numpy as np
from pathlib import Path
import os
import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime
import plotutils


# historicalData.py svp0 or svp2 or svp3
def airTunnelPressurePlot(fig, df):
    # Line below is because I dont know how to make my IDE realize that fig is a figure. Comment out before use
    # fig, ax = plt.subplots()
    bulkSetPoint = df.at[0, "PartBulkTempSetPoint"]
    fig.text(0.05, 0.05, f"Bulk Setpoint: {bulkSetPoint}C", fontsize=10)
    # plot pressures
    ax = fig.add_axes(plotutils.rect)

    ax.plot(
        "TransferCycleCount",
        "AirTunnelPressure1",
        data=df,
        label="Supply Side",
        color=plotutils.evolve_blue,
    )
    ax.plot(
        "TransferCycleCount",
        "AirTunnelPressure2",
        data=df,
        label="Return Side",
        color=plotutils.evolve_green,
    )

    # format air tunnel pressures

    # This is one way to format graph
    # ax.set_xlabel("Transfer Cycle Count")
    # ax.set_ylabel("Pressure (Pa)")
    # ax.set_title(f"{machineName} {jobStartDate}")
    # ax.legend(loc="upper left")

    # this is another that seems simpler to me
    # supported kwargs https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set.html
    ax.set(
        xlabel="Transfer Cycle Count",
        ylabel="Pressure (Pa)",
        title="Air Tunnel Pressure",
    )
    ax.set_xlim(xmin=0)
    ax.set_ylim(ymin=0)
    ax.legend(loc="upper left")

    # plot air tunnel RPM
    ax2 = ax.twinx()
    ax2.plot(
        "TransferCycleCount",
        "AirTunnelActualRPM",
        data=df,
        label="Air Tunnel RPM",
        color="r",
    )

    # format air tunnel RPM
    ax2.set_ylabel("RPM")
    ax2.set_ylim(0, 3500)
    plotutils.ref_line(ax2, 3600 * 0.8, label="80% Full load RPM")
    ax2.legend(loc="upper right")
    plotutils.format_twin_axes(ax, ax2, "k", "r")
    return fig


def airTunnelTempPlot(fig, df):
    bulkSetPoint = df.at[0, "PartBulkTempSetPoint"]
    # fig, ax = plt.subplots()
    ax = fig.add_axes(plotutils.rect)
    fig.text(
        0.05,
        0.05,
        f"Bulk Setpoint: {bulkSetPoint}",
        fontsize=10,
    )

    # plot air tunnel temps
    ax.plot(
        "TransferCycleCount",
        "AirTunnelTemp1",
        data=df,
        label="Supply Side",
        color=plotutils.evolve_blue,
    )
    ax.plot(
        "TransferCycleCount",
        "AirTunnelTemp2",
        data=df,
        label="Return Side",
        color=plotutils.evolve_green,
    )
    ax2 = ax.twinx()
    ax2.plot(
        "TransferCycleCount",
        "AirTunnelActualRPM",
        data=df,
        label="Air Tunnel RPM",
        color="r",
    )

    # format plots
    ax2.set_ylabel("RPM")
    ax2.set_ylim(0, 3500)
    plotutils.format_twin_axes(ax, ax2, "k", "r")
    plotutils.ref_line(ax2, 3600 * 0.8, label="80% Full load RPM")
    ax2.legend()

    ax.set_xlabel("Transfer Cycle Count")
    ax.set_ylabel("Temperature (\xb0C)")
    ax.set_title("Air Tunnel Temperatures")
    ax.legend(loc="upper left")
    ax.set_ylim(10, 40)
    ax.set_xlim(xmin=0)
    return fig


def chilledWaterPlot(fig, df):
    bulkSetPoint = df.at[0, "PartBulkTempSetPoint"]
    # fig, ax = plt.subplots()
    fig.text(0.05, 0.05, f"Bulk Set Point: {bulkSetPoint}", fontsize=10)
    ax = fig.add_axes(plotutils.rect)
    ax.plot(
        "TransferCycleCount",
        "WaterTempBuildManagementSupply",
        data=df,
        label="Supply",
        color="k",
        lw=3,
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
    ax.set_ylabel("Temperature (\xb0C)")
    ax.legend(loc="upper left")
    ax.set_ylim(0, 45)
    return fig


if __name__ == "__main__":
    machineName = (sys.argv[1]).upper()
    print(machineName)
    p = Path(
        f"C:/Users/TonyWitt/OneDrive - Evolve/{machineName}/{machineName}_Job_Data"
    )
    # documentName =f"{machineName}AirTunnelPressures.pdf"
    documentName = f"{machineName}AirTunnelTemps.pdf"
    # documentName =f"{machineName}ChilledWaterTemps.pdf"
    with PdfPages(documentName) as pp:
        for job in os.listdir(p):
            jobStartTime = int(job[:10])
            jobStartDate = datetime.fromtimestamp(jobStartTime)
            # grab data after date in epoch time
            if jobStartTime > 1672531200:
                df = pd.read_excel(p / job)
                print(f"Appending {job}")
                emptyFig = plotutils.new_page(
                    "", jobStartTime, jobStartDate, machineName
                )
                # fig = airTunnelPressurePlot(emptyFig, df)
                fig = airTunnelTempPlot(emptyFig, df)
                # fig = chilledWaterPlot(emptyFig, df)
                pp.savefig(fig)
                plt.close(fig)
    print(documentName)
