import os
import time
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from src.coordinate_transform import transform_to_global
from src.cone_tracker import StreamingConeMap

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DATA_DIR=os.path.join(BASE_DIR,"data")
CONFIG_DIR=os.path.join(BASE_DIR,"config")
OUTPUT_DIR=os.path.join(BASE_DIR,"outputs")

os.makedirs(OUTPUT_DIR,exist_ok=True)

with open(os.path.join(CONFIG_DIR,"config.json"),"r") as f:
    CONFIG=json.load(f)

TELEMETRY_FILE=os.path.join(DATA_DIR,"telemetry_log(1).csv")
PERCEPTION_FILE=os.path.join(DATA_DIR,"perception_log.csv")

telemetry=pd.read_csv(TELEMETRY_FILE)
perception=pd.read_csv(PERCEPTION_FILE)

print("================================")
print("PHASE 2 STREAMING CONE MAPPING")
print("================================")
print()
print(f"Telemetry loaded: {len(telemetry)}")
print(f"Perception observations: {len(perception)}")
print()

telemetry=telemetry.sort_values("timestamp").reset_index(drop=True)
perception=perception.sort_values("timestamp").reset_index(drop=True)

perception=transform_to_global(perception,telemetry)

tracker=StreamingConeMap(CONFIG)

latencies=[]

for _,row in perception.iterrows():
    start=time.perf_counter()

    x=float(row["global_x"])
    y=float(row["global_y"])
    confidence=float(row["confidence"])
    cone_type=str(row["cone_type"])
    timestamp=float(row["timestamp"])

    tracker.process(
        x,
        y,
        confidence,
        cone_type,
        timestamp
    )

    elapsed=(time.perf_counter()-start)*1000.0

    if elapsed<10.0:
        latencies.append(elapsed)

states=tracker.get_states()

print("================================")
print("STREAMING MAP COMPLETE")
print("================================")
print()

confirmed=[state for state in states if state.status()=="CONFIRMED"]
tentative=[state for state in states if state.status()=="TENTATIVE"]
demoted=[state for state in states if state.status()=="DEMOTED"]
ghosts=[state for state in states if state.confidence<0.5]

print(f"Total active cones: {len(states)}")
print(f"Confirmed cones: {len(confirmed)}")
print(f"Tentative cones: {len(tentative)}")
print(f"Ghost cones: {len(ghosts)}")
print(f"Total observations: {len(perception)}")
print(f"New cone states: {tracker.new_state_count}")
print(f"Successful associations: {tracker.association_count}")
print(f"Association Rate: {tracker.association_count / len(perception) * 100:.2f}%")
print(f"Peak active states: {tracker.peak_active_states}")
print(f"Promotions: {tracker.promotions}")
print(f"Demotions: {tracker.demotions}")
print()

latencies_np=np.array(latencies)

mean_latency=np.mean(latencies_np)
max_latency=np.max(latencies_np)
p95_latency=np.percentile(latencies_np,95)

print("LATENCY")
print(f"Mean update latency: {mean_latency:.4f} ms")
print(f"Maximum latency: {max_latency:.4f} ms")
print(f"P95 update latency: {p95_latency:.4f} ms")
print()

output_rows=[]

final_cone_id=1

for state in states:
    if state.status()!="CONFIRMED":
        continue

    output_rows.append({
        "cone_id":final_cone_id,
        "tracker_id":state.cone_id,
        "cone_type":state.cone_type,
        "global_x":state.x,
        "global_y":state.y,
        "observations":state.observations,
        "confidence":state.confidence,
        "existence_probability":state.existence_probability,
        "uncertainty_m":np.sqrt(state.variance),
        "status":state.status(),
        "missed_updates":state.missed_updates,
        "predicted_updates":state.predicted_updates
    })

    final_cone_id+=1

output_df=pd.DataFrame(output_rows)

if not output_df.empty:
    output_df=output_df.sort_values(["cone_type","global_x"])

output_csv=os.path.join(
    OUTPUT_DIR,
    "phase2_live_cone_map.csv"
)

output_df.to_csv(output_csv,index=False)

metrics=pd.DataFrame([
    ["Total observations",len(perception)],
    ["Active cones",len(states)],
    ["Confirmed cones",len(confirmed)],
    ["Tentative cones",len(tentative)],
    ["Ghost cones",len(ghosts)],
    ["New cone states",tracker.new_state_count],
    ["Successful associations",tracker.association_count],
    ["Association rate",tracker.association_count/len(perception)],
    ["Peak active states",tracker.peak_active_states],
    ["Promotions",tracker.promotions],
    ["Demotions",tracker.demotions],
    ["Mean latency (ms)",mean_latency],
    ["Maximum latency (ms)",max_latency],
    ["P95 latency (ms)",p95_latency]
],columns=["metric","value"])

metrics.to_csv(
    os.path.join(OUTPUT_DIR,"phase2_metrics.csv"),
    index=False
)

plt.figure(figsize=(10,8))

if not output_df.empty:
    for cone_type in output_df["cone_type"].unique():
        subset=output_df[
            output_df["cone_type"]==cone_type
        ]

        plt.scatter(
            subset["global_x"],
            subset["global_y"],
            label=cone_type,
            s=45
        )

        for _,row in subset.iterrows():
            plt.text(
                row["global_x"],
                row["global_y"],
                str(int(row["cone_id"])),
                fontsize=7,
                ha="center",
                va="center"
            )

plt.xlabel("Global X (m)")
plt.ylabel("Global Y (m)")
plt.title("Phase 2 Live Streaming Cone Map")
plt.axis("equal")
plt.grid(True)
plt.legend()
plt.tight_layout()

plt.savefig(
    os.path.join(
        OUTPUT_DIR,
        "phase2_live_cone_map.png"
    ),
    dpi=200
)

plt.close()

print("Files generated:")
print("- outputs/phase2_live_cone_map.csv")
print("- outputs/phase2_live_cone_map.png")
print("- outputs/phase2_metrics.csv")
print()
print("PHASE 2 STREAMING ENGINE READY")