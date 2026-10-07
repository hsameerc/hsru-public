import os
import sys
import time

# Import our ctypes wrapper
from hsru_edge import HSRUEdgeEngine

def load_csv_stream(path, sensor_dim):
    """Simple parser for the demo flight CSV"""
    stream = []
    if not os.path.exists(path):
        return stream
        
    with open(path, 'r') as f:
        for line in f:
            parts = line.strip().split(',')
            if len(parts) == sensor_dim:
                try:
                    stream.append([float(x) for x in parts])
                except ValueError:
                    pass
    return stream

def main():
    print("==========================================")
    print("   HSRU EDGE: DRONE ANOMALY DETECTOR    ")
    print("        (Python CTypes Wrapper)           ")
    print("==========================================")
    
    # 1. Hyperparameters (Will be replaced by exporter)
    sensor_dim = 20
    hidden_size = 128
    num_layers = 3
    
    lib_path = os.path.join("..", "lib", "libhsru_drone.so")
    weights_path = os.path.join("..", "weights", "drone_weights.bin")
    stream_path = os.path.join("..", "data", "demo_flight.csv")
    
    # 2. Initialize Engine
    try:
        # Assuming the first authorized hardware ID
        hwid = "MAC:00-11-22-33-44-55"
        engine = HSRUEdgeEngine(lib_path, weights_path, num_layers, hidden_size, sensor_dim, hwid=hwid)
        print(f"Loaded Brain Weights from {weights_path}")
    except Exception as e:
        print(f"Error initializing engine: {e}")
        return
        
    # 3. Load Flight Data
    live_stream = load_csv_stream(stream_path, sensor_dim)
    if not live_stream:
        print(f"Error: Cannot load live telemetry from {stream_path}")
        return
        
    print("READY\n")
    
    # 4. Fly the Drone! (1-Hour Simulation)
    # Warm-up phase: run the engine for a few frames to get past the cold-start
    # where hidden state = 0 causes huge initial MSE that would corrupt the calibration.
    WARMUP_FRAMES = 10
    predicted_sensors = [0.0] * sensor_dim
    for warm_row in live_stream[:WARMUP_FRAMES]:
        predicted_sensors = engine.step(warm_row)
    
    # Use a clean 4900-frame demo set to avoid end-of-flight noise
    live_stream = live_stream[WARMUP_FRAMES:WARMUP_FRAMES+4900]

    # Six Sigma Calibration Phase (Dynamically set threshold based on healthy baseline)
    calibration_frames = 500
    baseline_mses = []
    anomaly_threshold = 9999999.0
    consecutive_anomalies = 0
    ANOMALY_STRIKES = 5  # Require 5 consecutive high-MSE frames before flagging
    
    # Inject 2 catastrophic mechanical failures as 20-frame bursts.
    anomaly_injection_starts = {2000, 4000}
    ANOMALY_BURST_LEN = 20
    
    for t, actual_sensors in enumerate(live_stream):
        
        # Isolate the anomaly injection for visualization, but don't poison the RNN
        injected_sensors = list(actual_sensors)
        
        # Inject if we are within a burst window
        in_burst = any(start <= t < start + ANOMALY_BURST_LEN for start in anomaly_injection_starts)
        if in_burst:
            for i in range(sensor_dim):
                injected_sensors[i] += 5000.0  # Massive 5000G spike to simulate catastrophic failure
                
        # Calculate MSE against the PREVIOUS prediction using the INJECTED sensors
        worst_sensor_idx = -1
        worst_sensor_sq_err = -1.0
        sum_sq_err = 0.0
        for i in range(sensor_dim):
            sq_err = (injected_sensors[i] - predicted_sensors[i])**2
            sum_sq_err += sq_err
            if sq_err > worst_sensor_sq_err:
                worst_sensor_sq_err = sq_err
                worst_sensor_idx = i
                
        mse_error = sum_sq_err / sensor_dim
        # --- SIX SIGMA DYNAMIC CALIBRATION ---
        if t < calibration_frames:
            baseline_mses.append(mse_error)
        elif t == calibration_frames:
            import math
            mean_mse = sum(baseline_mses) / len(baseline_mses)
            variance = sum((x - mean_mse)**2 for x in baseline_mses) / len(baseline_mses)
            std_mse = math.sqrt(variance)
            anomaly_threshold = mean_mse + 6.0 * std_mse
            print(f"CALIBRATION COMPLETE. Six Sigma Threshold Locked at: {anomaly_threshold:.5f}")
            
        # Print Telemetry (T, AccelZ, PredictedAccelZ, MSE)
        print(f"TELEMETRY,{t},{injected_sensors[5]:.5f},{predicted_sensors[5]:.5f},{mse_error:.5f}")
        
        # Trigger Parachute Logic — requires ANOMALY_STRIKES consecutive frames over threshold
        if t > calibration_frames and mse_error > anomaly_threshold:
            consecutive_anomalies += 1
            if consecutive_anomalies >= ANOMALY_STRIKES:
                print(f"ANOMALY,{t},{mse_error:.5f}")
                
                failed_sensors = []
                for i in range(sensor_dim):
                    sq_err = (injected_sensors[i] - predicted_sensors[i])**2
                    if sq_err > anomaly_threshold:
                        failed_sensors.append((i, sq_err))
                
                failed_sensors.sort(key=lambda x: x[1], reverse=True)
                
                if failed_sensors:
                    total_err = sum(err for _, err in failed_sensors)
                    cause_str = " | ".join([f"S{i} ({err/total_err*100:.1f}%)" for i, err in failed_sensors])
                    print(f"ROOT CAUSE ISOLATED: {cause_str}")
                else:
                    print(f"ROOT CAUSE ISOLATED: Multiple cascading failures.")
                    
        else:
            consecutive_anomalies = 0
            # Do NOT break. We want to prove the drone can re-stabilize and catch the next one.
            
        # Predict the next millisecond using the TRUE uncorrupted sensors
        predicted_sensors = engine.step(actual_sensors)

if __name__ == "__main__":
    main()
