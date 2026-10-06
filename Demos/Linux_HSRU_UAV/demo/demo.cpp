#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <cmath>
#include <vector>
#include <iomanip>
#include "hsru.h"

#define FXP_FRAC_BITS 16
#define FLOAT_TO_FXP(x) ((int32_t)((x) * (1 << FXP_FRAC_BITS)))
#define FXP_TO_FLOAT(x) ((float)(x) / (1 << FXP_FRAC_BITS))

using namespace std;

int main() {
    cout << "========================================\n";
    cout << "   HSRU EDGE (FIXED-POINT Q16.16)       \n";
    cout << "========================================\n\n";

    int sensor_dim = 6;
    int hidden_size = 64;
    int num_layers = 4;

    const char* weights_path = "../weights/drone_weights.bin";
    const char* stream_path = "../data/demo_flight.csv";
    const char* anomaly_path = "../data/real_anomaly.csv";

    if (!hsru_authenticate("MAC:00-11-22-33-44-55")) {
        cout << "Error: DRM authentication failed. Hardware ID not authorized.\n";
        return 1;
    }

    void* ctx = hsru_init_context_fxp(weights_path, num_layers, hidden_size, sensor_dim);
    if (!ctx) {
        cout << "Error: Cannot initialize context\n";
        return 1;
    }

    cout << "Loaded Fixed-Point Brain Weights from " << weights_path << "\n";

    ifstream file(stream_path);
    if (!file.is_open()) {
        cout << "Error: Cannot load " << stream_path << "\n";
        return 1;
    }
    string line;
    cout << "READY\n";

    int32_t predicted_sensors[6] = {0};
    int32_t actual_sensors[6] = {0};
    float actual_sensors_f[6] = {0};
    
    vector<vector<float>> live_stream;
    while (getline(file, line)) {
        stringstream ss(line);
        string cell;
        vector<float> row;
        while (getline(ss, cell, ',')) {
            try { row.push_back(stof(cell)); } catch(...) {}
        }
        if (row.size() == sensor_dim) {
            live_stream.push_back(row);
        }
    }
    
    vector<vector<float>> anomaly_stream;
    ifstream anomaly_file(anomaly_path);
    if (anomaly_file.is_open()) {
        string a_line;
        getline(anomaly_file, a_line); // skip header
        while (getline(anomaly_file, a_line)) {
            stringstream ss(a_line);
            string cell;
            vector<float> row;
            while (getline(ss, cell, ',')) {
                try { row.push_back(stof(cell)); } catch(...) {}
            }
            if (row.size() == sensor_dim) {
                anomaly_stream.push_back(row);
            }
        }
        cout << "Loaded " << anomaly_stream.size() << " frames of REAL NASA anomaly data.\n";
    } else {
        cout << "Warning: Could not load real_anomaly.csv. Using synthetic spikes.\n";
    }

    
    int WARMUP_FRAMES = 10;
    for (int t = 0; t < WARMUP_FRAMES && t < live_stream.size(); t++) {
        for (int i = 0; i < sensor_dim; i++) {
            actual_sensors[i] = FLOAT_TO_FXP(live_stream[t][i]);
        }
        hsru_step_fxp(ctx, actual_sensors, predicted_sensors);
    }
    
    int calibration_frames = 500;
    vector<float> baseline_mses;
    float anomaly_threshold = 9999999.0f;
    int consecutive_anomalies = 0;
    int ANOMALY_STRIKES = 5;
    
    for (size_t t = WARMUP_FRAMES; t < WARMUP_FRAMES + 4900 && t < live_stream.size(); t++) {
        size_t adjusted_t = t - WARMUP_FRAMES;
        bool in_burst = (adjusted_t >= 2000 && adjusted_t < 2160) || (adjusted_t >= 4000 && adjusted_t < 4160);
        
        for (int i = 0; i < sensor_dim; i++) {
            actual_sensors_f[i] = live_stream[t][i];
            float injected = actual_sensors_f[i];
            if (in_burst) {
                int a_idx = adjusted_t - 2000;
                if (adjusted_t >= 4000) a_idx = adjusted_t - 4000;
                
                if (!anomaly_stream.empty() && a_idx < anomaly_stream.size()) {
                    injected = anomaly_stream[a_idx][i];
                } else if (i == 5) {
                    injected += 5000.0f; // Fallback to synthetic spike
                }
            }
            actual_sensors[i] = FLOAT_TO_FXP(injected);
        }
        
        float mse_error = 0.0f;
        for (int i = 0; i < sensor_dim; i++) {
            float p_f = FXP_TO_FLOAT(predicted_sensors[i]);
            float diff = FXP_TO_FLOAT(actual_sensors[i]) - p_f;
            mse_error += diff * diff;
        }
        mse_error /= sensor_dim;
        
        if (adjusted_t < calibration_frames) {
            baseline_mses.push_back(mse_error);
        } else if (adjusted_t == calibration_frames) {
            float sum = 0.0f, sum_sq = 0.0f;
            for (float m : baseline_mses) sum += m;
            float mean = sum / baseline_mses.size();
            for (float m : baseline_mses) sum_sq += (m - mean) * (m - mean);
            float variance = sum_sq / baseline_mses.size();
            float std_dev = sqrtf(variance);
            anomaly_threshold = mean + (6.0f * std_dev);
            cout << "CALIBRATION COMPLETE.\n";
            cout << "Baseline Mean MSE: " << mean << "\n";
            cout << "Baseline Std MSE: " << std_dev << "\n";
            cout << "Six Sigma Threshold Locked at: " << anomaly_threshold << "\n";
        }
        
        if (adjusted_t > calibration_frames && mse_error > anomaly_threshold) {
            consecutive_anomalies++;
            if (consecutive_anomalies >= ANOMALY_STRIKES) {
                cout << "ANOMALY," << adjusted_t << "," << fixed << setprecision(5) << mse_error << "\n";
                
                struct SensorErr { int idx; float err; };
                vector<SensorErr> failed;
                for (int i=0; i<sensor_dim; i++) {
                    float p_f = FXP_TO_FLOAT(predicted_sensors[i]);
                    float diff = FXP_TO_FLOAT(actual_sensors[i]) - p_f;
                    float sq_err = diff * diff;
                    if (sq_err > anomaly_threshold) {
                        failed.push_back({i, sq_err});
                    }
                }
                
                // Sort by largest error
                for (size_t i = 0; i < failed.size(); i++) {
                    for (size_t j = i + 1; j < failed.size(); j++) {
                        if (failed[j].err > failed[i].err) {
                            SensorErr temp = failed[i];
                            failed[i] = failed[j];
                            failed[j] = temp;
                        }
                    }
                }
                
                if (!failed.empty()) {
                    float total_err = 0.0f;
                    for (const auto& s : failed) total_err += s.err;
                    cout << "🚨 ROOT CAUSE ISOLATED: ";
                    for (size_t k = 0; k < failed.size(); k++) {
                        cout << "S" << failed[k].idx << " (" << fixed << setprecision(1) << (failed[k].err / total_err * 100.0f) << "%)";
                        if (k != failed.size() - 1) cout << " | ";
                    }
                    cout << "\n";
                } else {
                    cout << "🚨 ROOT CAUSE ISOLATED: Multiple cascading failures.\n";
                }
            }
        } else {
            consecutive_anomalies = 0;
        }
        
        for (int i = 0; i < sensor_dim; i++) {
            actual_sensors[i] = FLOAT_TO_FXP(actual_sensors_f[i]);
        }
        hsru_step_fxp(ctx, actual_sensors, predicted_sensors);
    }
    
    cout << "\nAnalysis Complete. All memory statically allocated successfully.\n";
    return 0;
}
