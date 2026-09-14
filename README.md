# Global Cone Mapping & Sensor Fusion — Phase 2

## 1. Overview

This project implements a streaming-style global cone mapping system for autonomous BAJA applications.

Phase 2 extends the Phase 1 offline mapping pipeline into a sequential streaming pipeline with incremental cone association, online position estimation, uncertainty tracking, cone existence probability, ghost handling, prediction through observation gaps, and fault/noise validation.

The system replays timestamped telemetry and perception observations sequentially while maintaining an evolving global cone map.

## 2. Features

- Global coordinate transformation
- 180° backward-mounted sensor correction
- Timestamp-based telemetry synchronization
- Incremental nearest-neighbor cone association
- Online confidence-weighted position estimation
- Per-cone position uncertainty
- Cone existence probability
- Tentative, confirmed, and ghost states
- Ghost promotion and demotion
- Prediction through temporary observation gaps
- Reassociation after missed updates
- Bounded active cone memory
- Streaming update latency measurement
- Fault and noise testing
- Multiple-condition validation
- Phase 1 vs Phase 2 comparison
- Automatic map and metric generation

## 3. Phase 2 Pipeline

```text
Telemetry + Perception Logs
            |
            v
Timestamp Synchronization
            |
            v
Backward Sensor Correction
            |
            v
Global Coordinate Transformation
            |
            v
Incremental Cone Association
            |
            v
Online Position + Uncertainty Update
            |
            v
Existence Probability Update
            |
            +------------------+
            |                  |
            v                  v
       Confirmed Cone      Ghost/Tentative
            |                  |
            +--------+---------+
                     |
                     v
             Live Global Cone Map
                     |
                     v
          Metrics + Validation Outputs
```

## 4. Project Structure

```text
Global_Cone_Mapping_Phase2/
│
├── src/
│   ├── __init__.py
│   ├── cone_tracker.py
│   └── coordinate_transform.py
│
├── config/
│   └── config.json
│
├── data/
│   ├── perception_log.csv
│   └── telemetry_log(1).csv
│
├── outputs/
│   ├── multiple_log_results.csv
│   ├── phase1_vs_phase2.csv
│   ├── phase2_live_cone_map.csv
│   ├── phase2_live_cone_map.png
│   └── phase2_metrics.csv
│
├── tests/
│   ├── fault_test.py
│   └── multiple_log_test.py
│
├── benchmarks/
│   └── latency_benchmark.py
│
├── main.py
├── requirements.txt
└── README.md
```

## 5. Requirements

- Python 3.10+
- pandas
- numpy
- matplotlib

Install dependencies using:

```bash
pip install -r requirements.txt
```

## 6. Input Data

The system uses two recorded logs.

### Telemetry

```text
timestamp
x
y
yaw_rad
speed_mps
steering_rad
yaw_rate_rps
```

### Perception

```text
timestamp
cone_type
rel_x_sensor
rel_y_sensor
confidence
label
```

The perception log contains 9,774 observations.

## 7. Running the Streaming Pipeline

From the project root:

```bash
python main.py
```

The program sequentially processes the perception observations and maintains the streaming cone states.

The final outputs are written to the `outputs/` directory.

## 8. Phase 2 Results

The latest streaming replay produced:

| Metric | Result |
|---|---:|
| Total observations | 9,774 |
| Active cones | 73 |
| Confirmed cones | 72 |
| Tentative cones | 0 |
| Ghost cones | 1 |
| New cone states | 139 |
| Successful associations | 9,635 |
| Association rate | 98.58% |
| Peak active states | 76 |
| Promotions | 72 |
| Demotions | 66 |

The final streaming map contains **72 confirmed cones**.

## 9. Streaming Performance

The latest benchmark produced:

| Latency Metric | Result |
|---|---:|
| Mean update latency | 0.141659 ms |
| P95 update latency | 0.214405 ms |
| Maximum retained latency | 1.9402 ms |

The latency benchmark excludes individual samples above 10 ms from the reported statistics to reduce distortion from host operating-system scheduling spikes.

This filtering affects only the reported latency benchmark and does not remove observations from the mapping pipeline.

The measured latency is a desktop Python replay benchmark and should not be interpreted as a guaranteed Jetson deployment latency.

## 10. Fault and Noise Testing

The fault test introduces controlled disturbances into the perception data, including:

- Reduced detection confidence
- Position perturbations
- Combined confidence and position noise

The streaming pipeline was tested while maintaining the original dataset after each experiment.

The fault testing demonstrated that the system continued to produce the expected confirmed cone map under the tested disturbances.

## 11. Multiple-Condition Validation

Four replay conditions were evaluated:

| Test Condition | Observations | Confirmed | Ghosts | Association Rate | Mean Latency (ms) | P95 (ms) |
|---|---:|---:|---:|---:|---:|---:|
| Original | 9,774 | 72 | 1 | 98.58% | 0.1426 | 0.2463 |
| Low Confidence | 9,774 | 72 | 1 | 98.58% | 0.1474 | 0.2544 |
| Position Noise | 9,774 | 72 | 1 | 98.58% | 0.1420 | 0.2453 |
| Combined Noise | 9,774 | 72 | 1 | 98.58% | 0.1417 | 0.2144 |

All four tested conditions retained **72 confirmed cones**.

## 12. Running Fault Testing

Run:

```bash
python tests/fault_test.py
```

The script:

1. Creates a temporary modified perception dataset.
2. Injects controlled confidence and position disturbances.
3. Runs the Phase 2 streaming pipeline.
4. Reports mapping and latency results.
5. Restores the original perception dataset.

## 13. Running Multiple-Condition Testing

Run:

```bash
python tests/multiple_log_test.py
```

The script evaluates:

```text
Original
Low Confidence
Position Noise
Combined Noise
```

The results are saved to:

```text
outputs/multiple_log_results.csv
```

## 14. Latency Benchmark

Run:

```bash
python benchmarks/latency_benchmark.py
```

The benchmark reads:

```text
outputs/phase2_metrics.csv
```

and reports the measured streaming update latency.

Latest benchmark:

```text
Mean latency: 0.141659 ms
P95 latency: 0.214405 ms
Maximum retained latency: 1.9402 ms
```

## 15. Phase 1 → Phase 2 Comparison

| Metric | Phase 1 | Phase 2 |
|---|---|---|
| Final confirmed cones | 72 | 72 |
| Processing mode | Offline | Sequential replay / streaming-style processing |
| Cone association | DBSCAN clustering | Incremental nearest-neighbor association |
| Position estimation | Weighted centroid | Online weighted update |
| Per-cone uncertainty | No | Yes |
| Existence probability | No | Yes |
| Ghost handling | Offline filtering | Online lifecycle management |
| Prediction | No | Yes |
| Fault/noise testing | No | Yes |
| Multiple-condition testing | No | Yes |
| Association rate | N/A | 98.58% |
| Mean update latency | N/A | 0.141659 ms |
| P95 update latency | N/A | 0.214405 ms |
| Maximum retained latency | N/A | 1.9402 ms |

Phase 2 therefore changes the mapping architecture from offline clustering to sequential state-based tracking while maintaining the same final confirmed cone count on the tested dataset.

## 16. Output Files

### `phase2_live_cone_map.csv`

Contains the final confirmed cone states, including estimated positions and tracking information.

### `phase2_live_cone_map.png`

Visualization of the final streaming global cone map.

### `phase2_metrics.csv`

Contains the final streaming performance and tracking metrics.

### `multiple_log_results.csv`

Contains results from the multiple-condition validation experiments.

### `phase1_vs_phase2.csv`

Contains the comparison between the Phase 1 and Phase 2 approaches.

## 17. Configuration

Streaming parameters are stored in:

```text
config/config.json
```

Important parameters include:

```text
association_gate_m
initial_position_variance
process_noise
measurement_noise
promotion_threshold
demotion_threshold
ghost_decay
max_missed_updates
prediction_enabled
reassociation_gate_m
min_confirmed_observations
max_active_cones
```

This separates algorithm configuration from the tracking implementation and allows parameters to be modified without changing the core source code.

## 18. Technical Approach

### 18.1 Timestamp Synchronization

Telemetry position and yaw are interpolated to the timestamp of each perception observation.

This allows each cone detection to be transformed using the vehicle pose corresponding to its observation time.

### 18.2 Backward Sensor Correction

The perception sensor is mounted facing backward relative to the vehicle frame.

Therefore, the sensor coordinates are first reversed:

```text
vehicle_frame_x = -rel_x_sensor
vehicle_frame_y = -rel_y_sensor
```

The corrected coordinates are then rotated using the vehicle yaw and translated using the vehicle position.

### 18.3 Incremental Association

Each incoming cone observation is compared with existing cone states of the same cone type.

A nearest-neighbor association is accepted when the distance is within the configured association gate.

A larger reassociation gate is used when a cone state has missed previous updates.

### 18.4 Online Position Estimation

Matched observations update the cone state using a Kalman-like confidence-aware position update.

The position variance is also updated during the process.

Higher-confidence observations contribute more reliably to the position estimate.

### 18.5 Cone Lifecycle

Each cone state contains:

- Position
- Position variance
- Observation count
- Average confidence
- Existence probability
- Missed-update count
- Prediction count
- Confirmation state

A cone becomes confirmed after satisfying the configured observation and existence thresholds.

### 18.6 Prediction

When prediction is enabled, active states are propagated through observation gaps.

Prediction increases uncertainty and reduces existence probability gradually.

This allows temporary missed detections without immediately creating duplicate cone states.

### 18.7 Bounded Memory

The tracker limits the number of active cone states using:

```text
max_active_cones
```

This is intended to keep the state size bounded for real-time deployment.

## 19. Validation Summary

The Phase 2 pipeline successfully processed all 9,774 perception observations.

Key results:

- 72 confirmed cones
- 98.58% association rate
- 73 active states at the end of replay
- 76 peak active states
- 139 new cone states created during replay
- 72 promotions
- 66 demotions
- 0 tentative states at the end
- 1 remaining ghost state
- All tested noise conditions retained 72 confirmed cones

The system therefore demonstrates stable sequential cone tracking on the provided recorded dataset.

## 20. Limitations

The current implementation is evaluated using recorded logs replayed sequentially.

The measured latency represents Python execution on the development computer and is not a direct measurement of a deployed autonomous vehicle or Jetson platform.

The association system uses nearest-neighbor matching rather than a more advanced global assignment or probabilistic multi-hypothesis tracker.

The current evaluation is based on the available recorded dataset and controlled fault/noise experiments.

## 21. Conclusion

Phase 2 converts the Phase 1 global cone mapping approach into a streaming-style tracking system.

The system performs incremental cone association, online position estimation, uncertainty tracking, existence management, prediction, and ghost handling while maintaining a bounded set of active cone states.

On the tested dataset, the pipeline produced 72 confirmed cones with a 98.58% association rate.

Fault and multiple-condition testing also retained 72 confirmed cones across the evaluated conditions.

The architecture provides a foundation for further deployment-oriented optimization and integration with autonomous BAJA perception systems.

## 22. References

1. Ester, M., Kriegel, H.-P., Sander, J., & Xu, X. (1996). A Density-Based Algorithm for Discovering Clusters in Large Spatial Databases with Noise. KDD.
2. Kalman, R. E. (1960). A New Approach to Linear Filtering and Prediction Problems. Journal of Basic Engineering.
3. Project dataset and experimental results used for the Global Cone Mapping & Sensor Fusion project.
4. Phase 1 and Phase 2 implementation artifacts from the project repository.
