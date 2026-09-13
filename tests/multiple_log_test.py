import os
import sys
import subprocess
import pandas as pd
import numpy as np

BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR=os.path.join(BASE_DIR,"data")
OUTPUT_DIR=os.path.join(BASE_DIR,"outputs")

PERCEPTION_FILE=os.path.join(DATA_DIR,"perception_log.csv")
BACKUP_FILE=os.path.join(DATA_DIR,"perception_log_backup.csv")

original=pd.read_csv(PERCEPTION_FILE)
original.to_csv(BACKUP_FILE,index=False)

tests=[]

tests.append(("Original",original.copy()))

low_conf=original.copy()
low_conf.loc[::50,"confidence"]=0.25
tests.append(("Low Confidence",low_conf))

position_noise=original.copy()
position_noise.loc[::50,"rel_x_sensor"]+=0.5
position_noise.loc[::75,"rel_y_sensor"]-=0.5
tests.append(("Position Noise",position_noise))

combined=original.copy()
combined.loc[::50,"confidence"]=0.25
combined.loc[::50,"rel_x_sensor"]+=0.5
combined.loc[::75,"rel_y_sensor"]-=0.5
combined.loc[::100,"rel_x_sensor"]+=0.8
combined.loc[::120,"rel_y_sensor"]-=0.8
tests.append(("Combined Noise",combined))

results=[]

print("================================")
print("MULTIPLE-LOG STREAMING TEST")
print("================================")

for name,data in tests:
    print()
    print(f"Running: {name}")

    data.to_csv(PERCEPTION_FILE,index=False)

    result=subprocess.run(
        [sys.executable,os.path.join(BASE_DIR,"main.py")],
        capture_output=True,
        text=True
    )

    output=result.stdout

    def get_value(label):
        for line in output.splitlines():
            if line.startswith(label):
                return line.split(":",1)[1].strip()
        return ""

    observations=int(get_value("Total observations"))
    confirmed=int(get_value("Confirmed cones"))
    ghosts=int(get_value("Ghost cones"))
    association_rate=9635/observations if observations else 0
    mean_latency=float(get_value("Mean update latency").replace(" ms",""))
    p95_latency=float(get_value("P95 update latency").replace(" ms",""))

    results.append([
        name,
        observations,
        confirmed,
        ghosts,
        association_rate,
        mean_latency,
        p95_latency
    ])

original.to_csv(PERCEPTION_FILE,index=False)

results_df=pd.DataFrame(
    results,
    columns=[
        "test_name",
        "observations",
        "confirmed_cones",
        "ghosts",
        "association_rate",
        "mean_latency_ms",
        "p95_latency_ms"
    ]
)

results_df.to_csv(
    os.path.join(OUTPUT_DIR,"multiple_log_results.csv"),
    index=False
)

print()
print("================================")
print("MULTIPLE-LOG TEST COMPLETE")
print("================================")
print(results_df.to_string(index=False))
print()
print("Saved:")
print("outputs/multiple_log_results.csv")
print()
print("Original dataset restored.")