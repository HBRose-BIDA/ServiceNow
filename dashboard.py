import json
import pathlib
import webbrowser
import requests
from datetime import datetime, timezone

CONFIG_PATH   = pathlib.Path("config.json")
QUEUE_PATH    = pathlib.Path("trigger") / "queue.json"
DASHBOARD_PATH = pathlib.Path("dashboard.html")

STATE_LABELS = {
    "1": "New",
    "2": "In Progress",
    "3": "On Hold",
    "6": "Resolved",
    "7": "Closed",
    "8": "Canceled",
}

STATUS_COLORS = {
    "New":         "#1b6ca8",
    "In Progress": "#e67e22",
    "On Hold":     "#8e44ad",
    "Resolved":    "#27ae60",
    "Closed":      "#555555",
    "Canceled":    "#c0392b",
}


def load_config():
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def load_queue():
    return json.loads(QUEUE_PATH.read_text(encoding="utf-8"))


def fetch_incident(instance_url, user, password, incident_number):
    url = (
        instance_url
        + f"?sysparm_query=number={incident_number}"
        + "&sysparm_fields=number,state,short_description,description,sys_created_on,assigned_to"
        + "&sysparm_limit=1"
        + "&sysparm_display_value=true"
    )
    try:
        r = requests.get(url, auth=(user, password),
                         headers={"Accept": "application/json"}, timeout=15)
        result = r.json().get("result", [])
        return result[0] if result else {}
    except Exception as e:
        return {"error": str(e)}


def esc(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_rows(queue, config):
    rows = []
    for item in reversed(queue):
        number = item.get("incident", "")
        file_name = item.get("file", "")
        logged_time = item.get("time_utc", "")[:19].replace("T", " ")
        smart_pred = str(item.get("predicted_urgency", ""))
        smart_conf = item.get("prediction_confidence", "")
        smart_action = str(item.get("smart_action", ""))

        if number:
            sn = fetch_incident(config["instance_url"], config["user"], config["password"], number)
        else:
            sn = {}

        if "error" in sn:
            rows.append(f"""
            <tr>
              <td>{esc(number)}</td>
              <td colspan="4" style="color:red">Error fetching from ServiceNow: {esc(sn['error'])}</td>
              <td>{esc(logged_time)}</td>
            </tr>""")
            continue

        state_code  = str(sn.get("state", ""))
        state_label = STATE_LABELS.get(state_code, state_code or "Unknown")
        color       = STATUS_COLORS.get(state_label, "#333")
        short_desc  = sn.get("short_description", "")
        created_on  = sn.get("sys_created_on", "")[:16]
        assigned    = sn.get("assigned_to", "") or "Unassigned"

        rows.append(f"""
            <tr>
              <td><strong>{esc(number)}</strong></td>
              <td>{esc(short_desc)}</td>
              <td><span style="color:{color};font-weight:bold">{esc(state_label)}</span></td>
              <td>{esc(smart_pred or "-")}</td>
              <td>{esc(str(smart_conf) if smart_conf != "" else "-")}</td>
              <td>{esc(smart_action or "-")}</td>
              <td>{esc(assigned)}</td>
              <td>{esc(created_on)}</td>
              <td>{esc(logged_time)}</td>
            </tr>""")

    if not rows:
        rows.append("<tr><td colspan='9'>No incidents yet.</td></tr>")

    return "\n".join(rows)


def build_html(rows, total):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>ServiceNow Incident Dashboard</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 30px; background: #f4f4f4; }}
    h1 {{ color: #1b3a5c; }}
    p {{ color: #555; margin-top: 0; }}
    table {{ width: 100%; border-collapse: collapse; background: white; }}
    th {{ background: #1b3a5c; color: white; padding: 10px; text-align: left; }}
    td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
    tr:hover td {{ background: #f0f7ff; }}
  </style>
</head>
<body>
  <h1>ServiceNow Incident Dashboard</h1>
  <p>Total: {total} &nbsp;|&nbsp; Last refreshed: {now} &nbsp;|&nbsp; Run dashboard.py to refresh.</p>
  <table>
    <thead>
      <tr>
        <th>Incident #</th>
        <th>Description</th>
        <th>Status</th>
        <th>Predicted Urgency</th>
        <th>Confidence</th>
        <th>Smart Action</th>
        <th>Assigned To</th>
        <th>Created (SN)</th>
        <th>Logged (Local)</th>
      </tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>
</body>
</html>
"""


def main():
    config = load_config()
    queue  = load_queue()

    print(f"Fetching status for {len(queue)} incident(s) from ServiceNow...")
    rows = build_rows(queue, config)
    html = build_html(rows, len(queue))

    DASHBOARD_PATH.write_text(html, encoding="utf-8")
    print(f"Dashboard written to: {DASHBOARD_PATH.resolve()}")

    webbrowser.open(DASHBOARD_PATH.resolve().as_uri())


if __name__ == "__main__":
    main()
