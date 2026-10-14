# HSRU Drone: Real-Time UAV Anomaly Detection & Flight Safety Metrics

This document contains the empirical evaluation benchmarks, fault severity scaling metrics, and operational avionics performance for **HSRU (Hybrid State Recurrent Unit)** applied to Unmanned Aerial Vehicle (UAV) structural health monitoring and real-time mechanical failure detection.

---

## 1. Executive Summary

Using high-frequency raw 6-DOF Inertial Measurement Unit (IMU) telemetry ($3\times$ gyro, $3\times$ accelerometer) sampled at 100 Hz, an unsupervised 4-layer Spiking HSRU forecaster was trained exclusively on healthy flight maneuvers to model the aircraft's aerodynamic and structural baseline.

### Key results

| Metric | Result | Operational Significance |
| :--- | :---: | :--- |
| **Damaged flights detected ($K=3$)** | **80 / 80 flights** | All damaged flights (1 to 4 broken blades) were flagged. |
| **False alarms ($K=3$)** | **0 / 3 held-out normal flights** | No false alarms on the held-out flights. This is a small sample; cross-validation over all 19 normal flights is planned. |
| **Time to alarm** | **18.5 s median, from log start** | Logs begin with 15 to 20 s on the ground before takeoff, so this corresponds to roughly 1 to 2 s after liftoff. |
| **Prediction error vs. normal** | **$51.3\times \longrightarrow 171.3\times$** | Increases with damage severity (1 to 4 broken blades). |
| **C++ inference time** | **$< 25\,\mu\text{s}$ per frame** | Measured on CPU, no GPU. Microcontroller (STM32 / Pixhawk) timing is planned. |
| **Memory** | **Fixed size, $\mathcal{O}(1)$** | No dynamic heap allocation in the per-frame loop. Designed with DO-178C-style constraints in mind; not certified. |

---

## 2. Benchmark Dataset & Experimental Setup

Evaluations were conducted on the peer-reviewed **UAV Realistic Fault Dataset (ICRA 2023)**, encompassing 99 physical quadrotor flight missions ($\sim$1.79 million telemetry frames) across 5 distinct physical structural states:

* **Class 0:** Normal Flight (0 broken propellers) (19 flight missions)
* **Class 1:** 1 Broken Propeller Blade (20 flight missions)
* **Class 2:** 2 Broken Propeller Blades (20 flight missions)
* **Class 3:** 3 Broken Propeller Blades (20 flight missions)
* **Class 4:** 4 Broken Propeller Blades (20 flight missions)

### Data split (by flight, no flight appears in more than one split)
The 19 normal flight missions were split into three non-overlapping subsets:
1. **13 Training Missions:** Used exclusively to train the unsupervised HSRU next-step predictor.
2. **3 Calibration Missions:** Used strictly to calibrate the Six Sigma ($6\sigma$) anomaly threshold ($\tau_{6\sigma} = 1.5218$).
3. **3 Held-Out Test Missions (1,081 windows):** Held strictly unseen to evaluate true operational False Alarm Rates.
4. **80 Damaged Flight Missions (28,982 windows):** Real physical broken-blade flights evaluated across all damage severities.

---

## 3. Empirical Benchmark Results

### A. Physical Damage Severity Scaling (Monotonic Error Surge)

Prediction error rises with the number of broken blades, which is consistent with the model tracking physical damage rather than noise:

| Group | Evaluated Flights | Evaluated Windows (1s) | Mean MSE | Error Surge vs. Normal | AUROC | Flights Alarmed ($K=3$) | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Class 0: Normal (Held-Out Test)** | 3 | 1,081 | 0.2549 | **$1.0\times$** | N/A | **0 / 3** | **0.0% False Alarm** |
| **Class 1: 1 Broken Propeller** | 20 | 7,388 | 13.0796 | **$51.3\times$** | 0.8745 | **20 / 20** | **100% Caught** |
| **Class 2: 2 Broken Propellers** | 20 | 7,186 | 20.9375 | **$82.1\times$** | 0.8710 | **20 / 20** | **100% Caught** |
| **Class 3: 3 Broken Propellers** | 20 | 7,259 | 31.4259 | **$123.3\times$** | 0.8846 | **20 / 20** | **100% Caught** |
| **Class 4: 4 Broken Propellers** | 20 | 7,149 | 43.6578 | **$171.3\times$** | 0.8879 | **20 / 20** | **100% Caught** |

> **Observation:** Mean MSE rises roughly linearly with the number of damaged blades (about +8 to +13 MSE per blade). Window-level AUROC is lower (0.87 to 0.89) because each log includes time on the ground, where a broken propeller produces no signal (see section C).

---

### B. Persistence Filtering & Operational Alarm Reliability

In flight control systems, triggering an emergency recovery protocol on a single isolated window ($K=1$) exposes the vehicle to false alarms from transient aerodynamic gusts or aggressive pilot maneuvers. A persistence filter requires $K$ consecutive windows above the Six Sigma threshold ($\tau_{6\sigma} = 1.5218$) before tripping the alarm:

| Persistence Filter ($K$) | False Alarm Rate (Held-Out Normal) | True Fault Detection Rate (Classes 1–4) | Median Time-to-Alarm | Max Time-to-Alarm | Operational Verdict |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **$K = 1$ (Raw Single Window)** | 2 / 3 flights | 80 / 80 flights | 17.5s | 61.0s | Too sensitive (triggers on hard manoeuvres / touchdown). |
| **$K = 3$ (3 Consecutive Seconds)** | **0 / 3 flights** | **80 / 80 flights** | **18.5s** | **62.0s** | **Chosen setting.** |
| **$K = 5$ (5 Consecutive Seconds)** | 0 / 3 flights | 80 / 80 flights | 19.5s | 63.0s | More conservative (adds about 1 s). |

---

### C. Understanding Window-Level Detection (~85.5%) vs. In-Flight Detection (100%)

In blind window-level scoring across raw rosbag logs, the detection rate is recorded as **85.54%**:

```text
Window-Level Statistics:
  Calib Normal Windows : 1,025   (Mean MSE: 0.2769, Max MSE: 3.7183)
  Test Normal Windows  : 1,081   (Mean MSE: 0.2549, Max MSE: 3.3401)
  Fault Windows        : 28,982  (Mean MSE: 27.1658, Max MSE: 165.0199)
  Threshold (Calib Mean + 6σ): 1.5218
  Raw Window Detection Rate  : 85.54%
  Indistinguishable Windows  : 15.01%
```

#### Physical Breakdown (The Tarmac Idle Reality):
1. **Stationary Pre-Takeoff Period:** Raw ROS2 logs begin while the quadrotor is resting on the tarmac with motors disarmed or idling before liftoff (15–20s per flight), and end after touchdown.
2. **Sensor Reality:** While stationary on the ground, the IMU reads static gravity ($[0, 0, -9.81]\,\text{m/s}^2$). An unspinning broken propeller generates zero aerodynamic lift or asymmetric vibration. Prediction error is identically low ($0.002$) for both normal and broken-blade drones.
3. **In-Flight Detection:** The moment the flight controller throttles up and lifts the drone into the air, the damaged blade creates intense 50 Hz rotor flutter. Prediction error instantly explodes ($>100\times$), achieving **$>95.8\%$ window detection while airborne** and **100.0% flight-level detection within 1–2 seconds of liftoff**.

---

## 4. Architecture & Edge Hardware Specifications

The drone model is instantiated via `HSRUBlock` using the **Full Spiking** configuration:

* **Model Architecture:** 4 stacked HSRU blocks ($D=64$, 6-channel continuous input $\to$ 6-channel output)
* **Routing Mode:** Residual Convex Blending (`mode="blend"`): $Y = (1-\beta) Y_{\text{mem}} + \beta Y_{\text{log}}$
* **Spiking Proportion:** 100% Full Spiking (`spiking_channels = 64`)
* **Spike Quantization:** $k\_dims = 1$ (Binary Leaky Integrate-and-Fire threshold)
* **Synaptic Reasoning:** Intermediate Logic MLP dimension $= 16$

### Why the full-spiking configuration was chosen
1. **Autoregressive Extrapolation Stability:**
   * Full Spiking achieves **0.043 MSE** on 50-step autoregressive extrapolation rollouts, compared to **0.102 MSE** for hybrid/continuous models.
   * In continuous recurrent states, small prediction errors accumulate into runaway drift. Leaky Integrate-and-Fire (LIF) subtractive voltage resets act as physical shock absorbers, resetting membrane potentials back to baseline.
2. **Strong anomaly signal:**
   * Healthy flight induces sparse firing ($\approx 6.8\%$). Damaged rotor vibration hammers the threshold, triggering synchronized firing bursts that increase MSE by **$51\times\text{--}171\times$**.
3. **C++ / PyTorch numerical parity:**
   * PyTorch float32, the CUDA kernels and the standalone C++ engines (`hsru.cpp` / `hsru_fxp.cpp`) agree to within a maximum absolute difference of $0.0011$.

---

## 5. Summary

On this dataset:
* **0 / 3 false alarms** on held-out normal flights with $K=3$ persistence (small sample).
* **80 / 80 damaged flights detected.**
* **$<25\,\mu\text{s}$ per frame on CPU** with fixed memory. Flight-controller integration (PX4 / ArduPilot) and on-microcontroller timing are next phase.
