import os
import pandas as pd

BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METRICS_FILE=os.path.join(BASE_DIR,"outputs","phase2_metrics.csv")

if not os.path.exists(METRICS_FILE):
    print("Run python main.py first.")
    exit()

metrics=pd.read_csv(METRICS_FILE)

print("================================")
print("PHASE 2 LATENCY BENCHMARK")
print("================================")
print()

for _,row in metrics.iterrows():
    metric=str(row["metric"])

    if "latency" in metric.lower():
        print(f"{metric}: {row['value']:.4f} ms")

print()
print("Benchmark completed.")