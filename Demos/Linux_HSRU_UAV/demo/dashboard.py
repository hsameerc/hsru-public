import subprocess
import json
import webbrowser
import os
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def run_demo_and_collect():
    print("\nInitializing AHSRU Edge Diagnostics...")
    print("Running inference engine (demo.py)...\n")
    
    # Run the demo script and capture stdout
    proc = subprocess.Popen([sys.executable, "demo.py"], stdout=subprocess.PIPE, text=True, encoding="utf-8")
    
    time_steps = []
    actuals = []
    predicteds = []
    mses = []
    anomaly_times = []
    anomaly_causes = {}
    six_sigma_threshold = "CALCULATING..."
    
    for line in proc.stdout:
        line = line.strip()
        print(line) # Echo to terminal
        if line.startswith("TELEMETRY"):
            parts = line.split(',')
            if len(parts) == 5:
                time_steps.append(int(parts[1]))
                actuals.append(float(parts[2]))
                predicteds.append(float(parts[3]))
                mses.append(float(parts[4]))
        elif line.startswith("ANOMALY"):
            parts = line.split(',')
            if len(parts) >= 3:
                anomaly_times.append(int(parts[1]))
        elif line.startswith("🚨 ROOT CAUSE ISOLATED:"):
            if anomaly_times:
                last_time = anomaly_times[-1]
                anomaly_causes[str(last_time)] = line
        elif line.startswith("CALIBRATION COMPLETE"):
            # Example: CALIBRATION COMPLETE. Six Sigma Threshold Locked at: 1234.56
            parts = line.split(":")
            if len(parts) == 2:
                six_sigma_threshold = parts[1].strip()
                
    proc.wait()
    
    return {
        "time": time_steps,
        "actual": actuals,
        "predicted": predicteds,
        "mse": mses,
        "anomaly_times": anomaly_times,
        "anomaly_causes": anomaly_causes,
        "six_sigma_threshold": six_sigma_threshold
    }

def generate_html(data):
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AHSRU Edge Telemetry Station</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #000000;
            --panel: #0a0a0c;
            --border: #1a1a1f;
            --accent: #00ffcc;
            --danger: #ff2a55;
            --text-main: #ffffff;
            --text-muted: #666666;
        }}
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'JetBrains Mono', monospace;
        }}
        
        body {{
            background-color: var(--bg);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            padding: 20px 40px;
        }}
        
        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 30px;
        }}
        
        header h1 {{
            font-size: 1.2rem;
            font-weight: 800;
            letter-spacing: 2px;
            color: var(--text-main);
            text-transform: uppercase;
        }}

        header h1 span {{ color: var(--text-muted); font-weight: 300; }}
        
        .live-badge {{
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 0.8rem;
            color: var(--accent);
            font-weight: 700;
            letter-spacing: 1px;
        }}

        .pulse {{
            width: 8px;
            height: 8px;
            background-color: var(--accent);
            border-radius: 50%;
            animation: blink 1s infinite;
        }}

        @keyframes blink {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.3; }}
        }}

        .dashboard-grid {{
            display: grid;
            grid-template-columns: 300px 1fr;
            gap: 30px;
            flex: 1;
        }}

        .sidebar {{
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}

        .hud-panel {{
            background: var(--panel);
            border: 1px solid var(--border);
            padding: 20px;
            display: flex;
            flex-direction: column;
        }}

        .hud-label {{
            font-size: 0.7rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 8px;
        }}

        .hud-value {{
            font-size: 2rem;
            font-weight: 300;
        }}

        .hud-value span.unit {{
            font-size: 0.9rem;
            color: var(--text-muted);
            margin-left: 5px;
        }}

        .hud-value.danger {{ color: var(--danger); }}

        #anomaly-card {{ display: none; border-color: var(--danger); background: rgba(255,42,85,0.05); }}

        .terminal-panel {{
            flex: 1;
            background: #050505;
            border: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            min-height: 250px;
        }}

        .terminal-header {{
            background: var(--border);
            padding: 5px 10px;
            font-size: 0.65rem;
            text-transform: uppercase;
            color: var(--text-muted);
            letter-spacing: 1px;
        }}

        .terminal-content {{
            padding: 10px;
            flex: 1;
            overflow-y: auto;
            max-height: 300px;
            font-size: 0.75rem;
        }}

        .terminal-content::-webkit-scrollbar {{ width: 4px; }}
        .terminal-content::-webkit-scrollbar-thumb {{ background: var(--border); }}

        .log-entry {{
            color: var(--text-muted);
            margin-bottom: 4px;
            line-height: 1.4;
        }}

        .log-entry.critical {{
            color: var(--danger);
        }}

        .log-entry span.time {{ color: #ffffff; }}

        .main-panel {{
            display: flex;
            flex-direction: column;
            border: 1px solid var(--border);
            background: var(--panel);
        }}

        .chart-container {{
            flex: 1;
            position: relative;
            min-height: 600px; /* Forces static height before Chart load to prevent UI jump */
            padding: 20px;
        }}
    </style>
</head>
<body>

    <header>
        <h1>AHSRU <span>// EDGE TELEMETRY</span></h1>
        <div class="live-badge">
            <div class="pulse"></div>
            LIVE DATA STREAM
        </div>
    </header>

    <div class="dashboard-grid">
        
        <div class="sidebar">
            <div class="hud-panel">
                <div class="hud-label">Flight Timestep</div>
                <div class="hud-value" id="stat-time">0<span class="unit">ms</span></div>
            </div>

            <div class="hud-panel">
                <div class="hud-label">Six Sigma Threshold</div>
                <div class="hud-value" id="stat-loss">...</div>
            </div>

            <div class="hud-panel" id="anomaly-card">
                <div class="hud-label" style="color: var(--danger);">Critical Anomaly</div>
                <div class="hud-value danger" id="stat-anomaly">DETECTED</div>
            </div>

            <div class="terminal-panel">
                <div class="terminal-header">System Event Log</div>
                <div class="terminal-content" id="anomaly-log-container">
                    <div class="log-entry">> Initializing neural inference engine...</div>
                    <div class="log-entry">> Connected to sensor stream.</div>
                </div>
            </div>
        </div>
        
        <div class="main-panel">
            <div class="chart-container">
                <canvas id="telemetryChart"></canvas>
            </div>
        </div>
        
    </div>

    <script>
        const fullData = {json.dumps(data)};
        
        if (fullData.six_sigma_threshold) {{
            document.getElementById('stat-loss').innerText = fullData.six_sigma_threshold;
        }}
        
        const ctx = document.getElementById('telemetryChart').getContext('2d');
        
        let liveAnomalies = [];
        let currentIndex = 0;
        
        const verticalLinePlugin = {{
            id: 'verticalLine',
            beforeDraw: chart => {{
                if (liveAnomalies.length > 0) {{
                    const ctx = chart.ctx;
                    liveAnomalies.forEach(anomaly_t => {{
                        const visibleIndex = chart.data.labels.indexOf(anomaly_t);
                        if (visibleIndex !== -1) {{
                            const x = chart.scales.x.getPixelForTick(visibleIndex);
                            const topY = chart.scales.y.top;
                            const bottomY = chart.scales.y.bottom;
                            
                            ctx.save();
                            ctx.beginPath();
                            ctx.moveTo(x, topY);
                            ctx.lineTo(x, bottomY);
                            ctx.lineWidth = 1;
                            ctx.strokeStyle = '#ff2a55';
                            ctx.stroke();
                            
                            ctx.fillStyle = '#ff2a55';
                            ctx.textAlign = 'center';
                            ctx.font = '10px JetBrains Mono';
                            ctx.fillText('DEPLOY', x, topY - 5);
                            ctx.restore();
                        }}
                    }});
                }}
            }}
        }};

        const chart = new Chart(ctx, {{
            type: 'line',
            plugins: [verticalLinePlugin],
            data: {{
                labels: [],
                datasets: [
                    {{
                        label: 'Predicted',
                        data: [],
                        borderColor: '#00ffcc',
                        borderWidth: 1,
                        pointRadius: 0,
                        tension: 0.1,
                        yAxisID: 'y'
                    }},
                    {{
                        label: 'Actual',
                        data: [],
                        borderColor: '#666666',
                        borderWidth: 1,
                        borderDash: [3, 3],
                        pointRadius: 0,
                        tension: 0.1,
                        yAxisID: 'y'
                    }},
                    {{
                        label: 'MSE Loss',
                        data: [],
                        borderColor: '#ff2a55',
                        backgroundColor: 'rgba(255, 42, 85, 0.05)',
                        borderWidth: 1,
                        pointRadius: 0,
                        fill: true,
                        tension: 0.1,
                        yAxisID: 'y1'
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false, // Prevents canvas from altering container height
                animation: false,
                interaction: {{ mode: 'index', intersect: false }},
                plugins: {{
                    legend: {{ labels: {{ color: '#888888', font: {{ family: 'JetBrains Mono', size: 10 }} }} }}
                }},
                scales: {{
                    x: {{
                        grid: {{ color: '#111111' }},
                        ticks: {{ color: '#666666', font: {{ family: 'JetBrains Mono', size: 10 }} }}
                    }},
                    y: {{
                        type: 'linear',
                        display: true,
                        position: 'left',
                        grid: {{ color: '#111111' }},
                        ticks: {{ color: '#00ffcc', font: {{ family: 'JetBrains Mono', size: 10 }} }}
                    }},
                    y1: {{
                        type: 'linear',
                        display: true,
                        position: 'right',
                        grid: {{ drawOnChartArea: false }},
                        ticks: {{ color: '#ff2a55', font: {{ family: 'JetBrains Mono', size: 10 }} }},
                        suggestedMax: 10000000 
                    }}
                }}
            }}
        }});
        
        const chunkSize = 5; // Slowed down from 50 to simulate realistic 300Hz real-time telemetry
        const maxPoints = 2000; 
        
        function animateLiveFlight() {{
            if (currentIndex >= fullData.time.length) {{
                document.getElementById('stat-time').innerHTML = "DONE<span class='unit'></span>";
                return;
            }}
            
            const endIdx = Math.min(currentIndex + chunkSize, fullData.time.length);
            
            for (let i = currentIndex; i < endIdx; i++) {{
                chart.data.labels.push(fullData.time[i]);
                chart.data.datasets[0].data.push(fullData.predicted[i]);
                chart.data.datasets[1].data.push(fullData.actual[i]);
                chart.data.datasets[2].data.push(fullData.mse[i]);
            }}
            
            if (chart.data.labels.length > maxPoints) {{
                const excess = chart.data.labels.length - maxPoints;
                chart.data.labels.splice(0, excess);
                chart.data.datasets[0].data.splice(0, excess);
                chart.data.datasets[1].data.splice(0, excess);
                chart.data.datasets[2].data.splice(0, excess);
            }}
            
            const currentTime = fullData.time[endIdx-1];
            document.getElementById('stat-time').innerHTML = currentTime + "<span class='unit'>ms</span>";
            
            if (fullData.anomaly_times) {{
                const passedAnomalies = fullData.anomaly_times.filter(t => t <= currentTime);
                if (passedAnomalies.length > liveAnomalies.length) {{
                    const newAnomalies = passedAnomalies.slice(liveAnomalies.length);
                    liveAnomalies = passedAnomalies;
                    
                    document.getElementById('anomaly-card').style.display = 'flex';
                    document.getElementById('stat-anomaly').innerText = `${{passedAnomalies.length}} CAPTURED`;
                    
                    const logContainer = document.getElementById('anomaly-log-container');
                    newAnomalies.forEach(anomalyTime => {{
                        const logEntry = document.createElement('div');
                        logEntry.className = 'log-entry critical';
                        const cause = fullData.anomaly_causes[anomalyTime.toString()];
                        const causeText = cause ? `<br/>&nbsp;&nbsp;${{cause}}` : '';
                        logEntry.innerHTML = `> <b>CRITICAL ANOMALY</b> <span class="time">[@${{anomalyTime}}ms]</span>${{causeText}}`;
                        logContainer.prepend(logEntry);
                    }});
                }}
            }}
            
            chart.update();
            currentIndex = endIdx;
            
            requestAnimationFrame(animateLiveFlight);
        }}
        
        animateLiveFlight();
    </script>
</body>
</html>"""
    return html_content

def main():
    data = run_demo_and_collect()
    
    if len(data['time']) == 0:
        print(f"Error: No telemetry data was collected. Did demo.py run successfully?")
        return
        
    html = generate_html(data)
    
    out_file = os.path.abspath("diagnostic_dashboard.html")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html)
        
    print(f"\nDiagnostic Dashboard generated at: {out_file}")
    
    try:
        print("Opening in default browser...")
        webbrowser.open(f"file://{out_file}")
    except:
        print("Please open the HTML file manually in your browser.")

if __name__ == "__main__":
    main()
