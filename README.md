# Global Cone Mapping & Sensor Fusion — Phase 2

## Overview

This project implements a streaming-style global cone mapping system for autonomous BAJA applications.

Phase 2 extends the Phase 1 offline global cone mapping pipeline into a sequential streaming architecture with:

- Incremental cone association
- Online position estimation
- Per-cone uncertainty tracking
- Existence probability
- Ghost cone handling
- Prediction through missed detections
- Fault and noise testing
- Multiple-condition validation
- Update latency benchmarking
- Bounded active cone states

The system replays recorded telemetry and perception logs sequentially to simulate streaming sensor processing.

## Features

- 180° backward-mounted sensor correction
- Timestamp-based telemetry synchronization
- Vehicle-frame to global-frame coordinate transformation
- Incremental nearest-neighbor cone association
- Confidence-aware online position updates
- Per-cone position uncertainty
- Cone existence probability
- Promotion and demotion lifecycle
- Ghost detection handling
- Prediction through temporary detection gaps
- Configurable association and lifecycle parameters
- Bounded active state memory
- Fault/noise injection testing
- Multiple-condition testing
- Update latency measurement
- Final global cone map generation

## Phase 2 Pipeline

```text
Telemetry + Perception Logs
            ↓
Timestamp Synchronization
            ↓
Backward Sensor Correction
            ↓
Global Coordinate Transformation
            ↓
Streaming Cone Association
            ↓
Online Position Update
            ↓
Uncertainty + Existence Probability
            ↓
Promotion / Demotion
            ↓
Prediction Through Gaps
            ↓
Final Live Cone Map
```

## Project Structure

```text
Global_Cone_Mapping_Phase2/
│
├── src/
│   ├── __init__.py
│   ├── coordinate_transform.py
│   └── cone_tracker.py
│
├── config/
│   └── config.json
│
├── data/
│   ├── perception_log.csv
│   └── telemetry_log(1).csv
│
├── outputs/
│   ├── phase2_live_cone_map.csv
│   ├── phase2_live_cone_map.png
│   ├── phase2_metrics.csv
│   ├── multiple_log_results.csv
│   └── phase1_vs_phase2.csv
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

## Requirements

- Python 3.10+
- NumPy
- Pandas
- Matplotlib

Install the required packages using:

```bash
pip install -r requirements.txt
```

## Input Data

The system uses two recorded sensor logs.

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

The perception sensor is mounted facing backwards relative to the vehicle.

The system therefore applies a 180° sensor-frame correction before transforming detections into the global coordinate frame.

## Running the Streaming Pipeline

From the project root:

```bash
python main.py
```

The program sequentially processes the perception observations and updates the active cone states.

The final results are saved automatically in the `outputs` folder.

## Phase 2 Results

The complete recorded dataset contains:

- Telemetry samples: **1200**
- Perception observations: **9774**
- Final confirmed cones: **72**
- Peak active cone states: **76**
- New cone states created: **139**
- Successful associations: **9635**
- Association rate: **98.58%**
- Promotions: **72**
- Demotions: **66**

The final map contains **72 confirmed cones**.

The Phase 2 streaming pipeline therefore preserves the same final cone count obtained by the Phase 1 offline pipeline while processing observations sequentially.

## Streaming Performance

The latest streaming benchmark produced:

| Metric | Result |
|---|---:|
| Mean update latency | 0.1362 ms |
| P95 update latency | 0.1674 ms |
| Maximum retained latency | 7.5783 ms |

The latency is measured for individual cone-map updates during recorded-data replay.

The benchmark excludes individual samples above 10 ms from the reported latency statistics in order to reduce the effect of host operating-system scheduling spikes.

This filtering affects only the reported latency benchmark and does not affect the mapping results.

The measured latency represents a desktop Python replay benchmark and should not be interpreted as a guaranteed Jetson deployment latency.

## Fault and Noise Testing

A fault-injection test was performed by introducing:

- Low-confidence detections
- Position perturbations
- Combined confidence and position noise

The original perception dataset was restored after testing.

The fault test retained:

- **72 confirmed cones**
- **1 rejected/demoted state**

This demonstrates that the streaming tracker can maintain the final cone map under injected sensor disturbances.

## Multiple-Condition Validation

The system was tested under multiple simulated perception conditions.

| Test Condition | Observations | Confirmed Cones | Ghosts | Association Rate | Mean Latency (ms) | P95 (ms) |
|---|---:|---:|---:|---:|---:|---:|
| Original | 9774 | 72 | 1 | 98.58% | 0.1409 | 0.2514 |
| Low Confidence | 9774 | 72 | 1 | 98.58% | 0.1380 | 0.2137 |
| Position Noise | 9774 | 72 | 1 | 98.58% | 0.1398 | 0.2215 |
| Combined Noise | 9774 | 72 | 1 | 98.58% | 0.1366 | 0.1965 |

All tested conditions retained **72 confirmed cones**.

## Running Fault Testing

Run:

```bash
python tests/fault_test.py
```

The test temporarily modifies the perception data, runs the streaming pipeline, evaluates the result, and restores the original dataset.

## Running Multiple-Condition Testing

Run:

```bash
python tests/multiple_log_test.py
```

The results are saved to:

```text
outputs/multiple_log_results.csv
```

## Latency Benchmark

Run:

```bash
python benchmarks/latency_benchmark.py
```

This reads the latest metrics from:

```text
outputs/phase2_metrics.csv
```

and displays the measured streaming update latency.

## Phase 1 → Phase 2 Comparison

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
| Mean update latency | N/A | 0.1362 ms |
| P95 update latency | N/A | 0.1674 ms |
| Maximum retained latency | N/A | 7.5783 ms |

Phase 2 changes the processing architecture from an offline clustering workflow to a sequential tracking workflow while preserving the final 72-cone map.

## Output Files

### `phase2_live_cone_map.csv`

Contains the final confirmed cone states including:

- Cone ID
- Tracker ID
- Cone type
- Global X/Y position
- Observation count
- Confidence
- Existence probability
- Position uncertainty
- Cone status
- Missed updates
- Predicted updates

### `phase2_live_cone_map.png`

Visualization of the final streaming global cone map with numbered confirmed cones.

### `phase2_metrics.csv`

Contains the main Phase 2 performance metrics including:

- Observation count
- Active cones
- Confirmed cones
- Association rate
- Peak active states
- Promotions
- Demotions
- Update latency

### `multiple_log_results.csv`

Contains results from the multiple-condition validation experiments.

### `phase1_vs_phase2.csv`

Contains the Phase 1 and Phase 2 comparison metrics.

## Configuration

The main tracking parameters are stored in:

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

This allows the streaming tracker to be tuned without modifying the core tracking code.

## Technical Approach

### Coordinate Transformation

The perception sensor is backward-facing, so the sensor coordinates are first rotated by 180° into the vehicle frame.

The corrected vehicle-frame coordinates are then transformed using the vehicle position and yaw obtained from synchronized telemetry.

### Incremental Association

Each incoming cone observation is compared against existing cone states of the same cone type.

The nearest valid state is selected when the distance is within the configured association gate.

If no suitable state exists, a new cone state is created.

### Online Position Estimation

When an observation is associated with an existing cone, its position is updated online using a confidence-aware Kalman-style weighted update.

Higher-confidence measurements receive greater influence on the estimated position.

### Uncertainty Tracking

Every cone state maintains a position variance.

The uncertainty is updated as new measurements arrive and increases during prediction-only updates.

The final uncertainty is reported as:

```text
uncertainty_m = sqrt(position_variance)
```

### Cone Lifecycle

Each cone maintains an existence probability.

Repeated successful observations increase its existence probability.

During missed detections, the probability decays.

Cone states can therefore transition through:

```text
TENTATIVE → CONFIRMED
TENTATIVE → DEMOTED
```

This provides online ghost handling instead of relying only on final offline filtering.

### Prediction Through Detection Gaps

When a cone is temporarily not detected, its state is retained and its uncertainty is increased.

A larger reassociation gate is used when attempting to reconnect with a cone after missed updates.

### Bounded Memory

The tracker limits the number of active cone states using:

```text
max_active_cones
```

This prevents unlimited state growth during long-running operation.

## Validation Summary

Phase 2 was evaluated using the original recorded dataset and additional fault/noise conditions.

The streaming system consistently produced:

- 72 confirmed cones
- 98.58% association rate
- Sub-millisecond mean update latency
- Stable results under low-confidence and position-noise conditions
- Bounded active state memory
- Online uncertainty estimation
- Online ghost lifecycle management

## Limitations

The current implementation uses recorded logs replayed sequentially to simulate streaming sensor processing.

The latency benchmark was performed on a desktop Python environment.

For real autonomous vehicle deployment, further validation would be required on the target embedded platform, including Jetson-class hardware, real sensor drivers, communication delays, and real-time scheduling behavior.

The current association method is nearest-neighbor based and can be further extended with more advanced multi-target data association methods if required.

## Conclusion

Phase 2 successfully converts the Phase 1 offline cone mapping approach into a streaming-style global cone tracking pipeline.

The system performs sequential sensor fusion, incremental cone association, online position estimation, uncertainty tracking, ghost lifecycle management, prediction through detection gaps, and bounded state management.

The final evaluation retained **72 confirmed cones** with a **98.58% association rate** while achieving a measured mean update latency of **0.1362 ms** during recorded-data replay.

Fault and multiple-condition testing also retained all 72 confirmed cones, demonstrating stable behavior under simulated sensor disturbances.

## References

1. M. Ester, H.-P. Kriegel, J. Sander, and X. Xu, "A Density-Based Algorithm for Discovering Clusters in Large Spatial Databases with Noise," KDD, 1996.

2. R. E. Kalman, "A New Approach to Linear Filtering and Prediction Problems," Journal of Basic Engineering, 1960.

3. Team Asterix — Global Cone Mapping & Sensor Fusion project dataset and implementation artifacts.
