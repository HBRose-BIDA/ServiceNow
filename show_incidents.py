import json
import pathlib
import requests

CONFIG_PATH = pathlib.Path("config.json")
QUEUE_PATH  = pathlib.Path("trigger") / "queue.json"

# State codes ServiceNow uses for incidents
STATE_LABELS = {
    "1": "New",
    "2": "In Progress",
    "3": "On Hold",
    "6": "Resolved",
    "7": "Closed",
    "8": "Canceled",
}


def load_config():
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def load_queue():
    return json.loads(QUEUE_PATH.read_text(encoding="utf-8"))


def fetch_incident(instance_url, user, password, incident_number):
    url = (
        instance_url
        + f"?sysparm_query=number={incident_number}"
        + "&sysparm_fields=number,state,short_description,sys_created_on,assigned_to"
        + "&sysparm_limit=1"
        + "&sysparm_display_value=true"
    )
    try:
        response = requests.get(
            url,
            auth=(user, password),
            headers={"Accept": "application/json"},
            timeout=15,
        )
        result = response.json().get("result", [])
        return result[0] if result else {}
    except Exception as error:
        return {"error": str(error)}


def display_row(queue_item, sn_data):
    number      = queue_item.get("incident", "")
    file_name   = queue_item.get("file", "")
    logged_time = queue_item.get("time_utc", "")[:19].replace("T", " ")

    if "error" in sn_data:
        print(f"  {number}  |  {logged_time}  |  ERROR: {sn_data['error']}")
        return

    short_desc  = sn_data.get("short_description", "")
    state_code  = sn_data.get("state", "")
    state_label = STATE_LABELS.get(str(state_code), state_code)
    created_on  = sn_data.get("sys_created_on", "")[:16]
    assigned    = sn_data.get("assigned_to", "") or "Unassigned"

    print(f"  Incident : {number}")
    print(f"  Status   : {state_label}")
    print(f"  Created  : {created_on}")
    print(f"  Assigned : {assigned}")
    print(f"  Subject  : {short_desc}")
    print(f"  Source   : {file_name}")
    print()


def main():
    config = load_config()
    queue  = load_queue()

    if not queue:
        print("No incidents in queue yet.")
        return

    print(f"\n{'='*50}")
    print(f"  ServiceNow Incident Queue  ({len(queue)} records)")
    print(f"{'='*50}\n")

    for item in reversed(queue):
        incident_number = item.get("incident", "")
        if incident_number:
            sn_data = fetch_incident(
                config["instance_url"],
                config["user"],
                config["password"],
                incident_number,
            )
        else:
            sn_data = {}
        display_row(item, sn_data)

    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
