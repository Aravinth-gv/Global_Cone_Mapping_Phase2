import os
import sys
import subprocess
import pandas as pd

BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR=os.path.join(BASE_DIR,"data")
OUTPUT_DIR=os.path.join(BASE_DIR,"outputs")
PERCEPTION_FILE=os.path.join(DATA_DIR,"perception_log.csv")
BACKUP_FILE=os.path.join(DATA_DIR,"perception_log_backup.csv")

perception=pd.read_csv(PERCEPTION_FILE)
perception.to_csv(BACKUP_FILE,index=False)

print("================================")
print("PHASE 2 FAULT / NOISE TEST")
print("================================")
print(f"Original observations: {len(perception)}")

noisy=perception.copy()

noisy.loc[::50,"confidence"]=0.25
noisy.loc[::75,"rel_x_sensor"]+=0.5
noisy.loc[::100,"rel_y_sensor"]-=0.5

noisy.to_csv(PERCEPTION_FILE,index=False)

print("Injected:")
print("- Low-confidence detections")
print("- X-position noise")
print("- Y-position noise")
print()
print("Running streaming pipeline...")
print()

result=subprocess.run(
    [sys.executable,os.path.join(BASE_DIR,"main.py")],
    capture_output=True,
    text=True
)

print(result.stdout)

if result.stderr:
    print("ERROR:")
    print(result.stderr)

original=pd.read_csv(BACKUP_FILE)
final=pd.read_csv(os.path.join(OUTPUT_DIR,"phase2_live_cone_map.csv"))

confirmed=(final["status"]=="CONFIRMED").sum()
ghosts=(final["status"]=="DEMOTED").sum()

print("================================")
print("FAULT TEST RESULT")
print("================================")
print(f"Original cones expected: 72")
print(f"Confirmed cones after noise: {confirmed}")
print(f"Rejected/demoted states: {ghosts}")

perception.to_csv(PERCEPTION_FILE,index=False)

print()
print("Original dataset restored.")
print("================================")