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
    fig, ax = plt.subplots()
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


if __name__ == "__main__":
    Machine = (sys.argv[1]).upper()
    print(Machine)
    p = Path(f"C:/Users/TonyWitt/OneDrive - Evolve/{Machine}/{Machine}_Job_Data")

    with PdfPages(f"{Machine}AirTunnelPressures.pdf") as pp:
        for job in os.listdir(p):
            jobStartTime = int(job[:10])
            jobStartDate = datetime.fromtimestamp(jobStartTime)
            # grab data after date in epoch time
            if jobStartTime > 1663171587:
                df = pd.read_excel(p / job)
                print(f"Saving {job}")
                fig = airTunnelPlot(df)
                pp.savefig(fig)
                plt.close(fig)
            else:
                pass
