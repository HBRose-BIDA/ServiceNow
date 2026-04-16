import requests
import json
from pathlib import Path
from datetime import datetime, timezone


def load_config():
    config_path = Path(__file__).with_name("config.json")
    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)

# Configuration
config = load_config()
INSTANCE_URL = config["instance_url"]
USER = config["user"]
PWD = config["password"]
TRACKER_PATH = Path(__file__).with_name("incident_tracker.json")

# The Incident Data
# You can dynamically populate these variables from your in-house error logs
payload = {
    "short_description": "Critical Error: In-house Analytics Engine",
    "description": "System generated error: Connection timeout in data pipeline.",
    "urgency": "1", # 1: High, 2: Medium, 3: Low
    "impact": "1",  # 1: High, 2: Medium, 3: Low
    "comments": "This incident was created automatically by the Python monitoring script."
}


def save_incident_record(incident_number, sys_id, short_description):
    record = {
        "incident_number": incident_number,
        "sys_id": sys_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "short_description": short_description
    }

    tracker_data = {
        "latest_incident": record,
        "incidents": [record]
    }

    if TRACKER_PATH.exists():
        try:
            with TRACKER_PATH.open("r", encoding="utf-8") as f:
                existing = json.load(f)

            incidents = existing.get("incidents", [])
            incidents.append(record)
            tracker_data = {
                "latest_incident": record,
                "incidents": incidents
            }
        except (json.JSONDecodeError, AttributeError):
            # If the tracker file is corrupted or not a JSON object, start clean.
            tracker_data = {
                "latest_incident": record,
                "incidents": [record]
            }

    with TRACKER_PATH.open("w", encoding="utf-8") as f:
        json.dump(tracker_data, f, indent=2)

def create_incident(payload_override=None):
    # Set proper headers for the ServiceNow API
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    incident_payload = payload_override or payload

    try:
        # Perform the POST request
        response = requests.post(
            INSTANCE_URL, 
            auth=(USER, PWD), 
            headers=headers, 
            data=json.dumps(incident_payload)
        )

        # Check for success (201 Created)
        if response.status_code == 201:
            data = response.json()
            incident_number = data['result']['number']
            sys_id = data['result']['sys_id']
            short_description = incident_payload.get("short_description", "")
            save_incident_record(incident_number, sys_id, short_description)
            print(f"Success! Incident {incident_number} created.")
            print(f"Internal Sys ID: {sys_id}")
            print(f"Saved to tracker: {TRACKER_PATH}")
            return {
                "ok": True,
                "incident_number": incident_number,
                "sys_id": sys_id,
                "result": data.get("result", {})
            }
        else:
            print(f"Failed to create incident. Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            return {
                "ok": False,
                "status_code": response.status_code,
                "error": response.text
            }

    except Exception as e:
        print(f"An error occurred: {e}")
        return {
            "ok": False,
            "error": str(e)
        }

if __name__ == "__main__":
    create_incident()