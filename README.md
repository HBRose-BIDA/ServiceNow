# ServiceNow Incident Management Automation

A comprehensive Python application for automating ServiceNow incident management, featuring real-time monitoring, predictive analytics, and automated dashboard generation.

## Features

- **Incident Tracking** – Real-time synchronization with ServiceNow incidents
- **Predictive Analytics** – ML-powered urgency prediction model for intelligent incident prioritization
- **Automated Dashboards** – HTML-based incident visualization and status reporting
- **Event-Driven Watcher** – Continuous monitoring with automatic trigger processing
- **Presentation Generation** – Automated PowerPoint deck creation for incident summaries

## Project Structure

```
├── ml/                          # Machine Learning module
│   ├── train_model.py          # Model training pipeline
│   ├── predictor.py            # Inference engine
│   ├── generate_training_data.py
│   ├── urgency_model.json      # Trained model weights
│   └── data/
│       └── synthetic_incidents.jsonl
├── trigger/                     # Event-driven processing
│   ├── watcher.py              # File system watcher
│   ├── queue.json              # Event queue
│   ├── inbox/                  # Incoming events
│   ├── processed/              # Completed events
│   └── failed/                 # Failed processes
├── archive/                     # Legacy code & modules
│   └── legacy/
│       ├── Assign_Incident.py
│       ├── Get_Incident.py
│       └── SN_Table.py
├── build_deck.py               # PowerPoint generation
├── build_smart_model.py        # Model builder utility
├── create_inbox_record.py      # Event creation
├── show_incidents.py           # Incident display
├── dashboard.py                # Dashboard generator
└── config.template.json        # Configuration template
```

## Getting Started

### Prerequisites

- Python 3.8+
- ServiceNow instance with API access
- Required dependencies (see below)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/servicenow-automation.git
   cd servicenow-automation
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate  # macOS/Linux
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure your ServiceNow credentials:
   ```bash
   cp config.template.json config.json
   # Edit config.json with your ServiceNow instance details
   ```

### Usage

#### View Incidents
```bash
python show_incidents.py
```

#### Generate Dashboard
```bash
python dashboard.py
```

#### Create Presentation
```bash
python build_deck.py
```

#### Start Event Watcher
```bash
python trigger/watcher.py
```

#### Train ML Model
```bash
python ml/train_model.py
```

## Key Components

### ML Module (`ml/`)
Implements a predictive model for incident urgency classification:
- **Training**: Uses synthetic incident data to train urgency predictor
- **Inference**: Real-time urgency prediction for new incidents
- **Model Storage**: Binary model saved as JSON

### Event Watcher (`trigger/watcher.py`)
- Monitors inbox directory for new events
- Processes incidents through the pipeline
- Moves completed events to processed folder
- Handles errors and failed events gracefully

### Dashboard (`dashboard.py`)
Generates HTML visualizations showing:
- Incident status distribution
- Priority breakdown
- Time-to-resolution metrics

### Presentation Builder (`build_deck.py`)
Automated PowerPoint generation with:
- Incident summaries
- Performance metrics
- Executive summaries

## Configuration

Copy `config.template.json` to `config.json` and update with your ServiceNow credentials:
```json
{
  "instance_url": "https://your-instance.service-now.com/api/now/table/incident",
  "user": "your_username",
  "password": "your_api_token"
}
```

⚠️ **Never commit `config.json` to version control.** It contains sensitive credentials.

## Development

### Code Organization
- Modular design with separate concerns (ML, triggering, UI)
- RESTful API integration with ServiceNow
- Event-driven architecture for scalability

### Best Practices
- Configuration templates for sensitive data
- Separate module for ML operations
- Automated processing pipelines

## License

This project is provided as-is for portfolio purposes.

## Contact

[Your Name] – [Your Email/LinkedIn]

---

**Note**: This is a portfolio project demonstrating incident management automation, machine learning integration, and API-driven workflows.
