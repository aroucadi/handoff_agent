import subprocess
import json

def fetch_logs():
    # Fetch logs using subprocess to avoid powershell quoting issues
    cmd = [
        "gcloud.cmd", "logging", "read",
        'resource.type="cloud_run_revision" AND resource.labels.service_name="synapse-api" AND textPayload:"b1628f05"',
        "--limit=50", "--format=json", "--project=synapse-488201"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        logs = json.loads(result.stdout)
        for log in logs:
            if "textPayload" in log:
                print(f"[{log['timestamp']}] {log['textPayload']}")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")

if __name__ == "__main__":
    fetch_logs()
