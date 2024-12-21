# MQTT GEM Host Application

This project is an MQTT-enabled GEM host application that allows for the management of equipment through a command-line interface. It integrates MQTT functionality to facilitate communication between devices.

## Project Structure

```
mqtt-gemhost-app
├── src
│   ├── main.py          # Main entry point of the application
│   ├── mqtt_handler.py   # Handles MQTT connections and messaging
│   └── config
│       └── config.json   # Configuration settings for the application
├── requirements.txt      # Project dependencies
└── README.md             # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd mqtt-gemhost-app
   ```

2. **Install dependencies:**
   Ensure you have Python installed, then run:
   ```
   pip install -r requirements.txt
   ```

3. **Configure the application:**
   Edit the `src/config/config.json` file to set up your equipment details and MQTT broker settings.

4. **Run the application:**
   Execute the main script:
   ```
   python src/main.py
   ```

## Usage

- Use the command-line interface to manage equipment.
- Available commands:
  - `enable <equipment_name>`: Enable a specific equipment.
  - `disable <equipment_name>`: Disable a specific equipment.
  - `list`: List all equipment and their status.
  - `exit`: Exit the application.

## MQTT Integration

This application uses the `paho-mqtt` library to handle MQTT connections. The `mqtt_handler.py` file contains the logic for connecting to the MQTT broker, publishing messages, and subscribing to topics.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.