# DEJ/TNF Equipment Management System

## Overview
System for managing DEJ/TNF equipment communication using SECS/GEM protocol with MQTT integration and web-based control interface.

## Project Structure
```
### Plan
1. Create main project overview
2. Document project structure
3. Detail setup instructions
4. Explain MQTT integration
5. Add configuration details

```markdown


# DEJ/TNF Equipment Management System

## Overview
System for managing DEJ/TNF equipment communication using SECS/GEM protocol with MQTT integration and web-based control interface.

## Project Structure
```
dejtnf/
├── frontend/               # Next.js web application
│   ├── src/               # Source code
│   │   ├── app/          # App router pages
│   │   ├── components/   # React components
│   │   └── utils/        # Utility functions
│   └── public/           # Static assets
├── secsgem/              # SECS/GEM implementation
│   ├── src/             # Source code
│   │   ├── cli/         # CLI tools
│   │   ├── config/      # Configuration
│   │   ├── gem/         # SECS/GEM protocols
│   │   ├── handler/     # Event handlers
│   │   └── mqtt/        # MQTT client
│   ├── files/           # Equipment files
│   └── logs/            # Log files
```

## Features
- SECS/GEM equipment communication
- Real-time MQTT monitoring
- Web-based control interface
- Equipment state management
- Recipe management
- Event/alarm handling

## Setup Instructions

### Frontend Setup
```bash
cd frontend
npm install
# Create .env.local file with:
NEXT_PUBLIC_MQTT_HOST=localhost
NEXT_PUBLIC_MQTT_PORT=8081
NEXT_PUBLIC_MQTT_USER=your_username
NEXT_PUBLIC_MQTT_PASS=your_password
npm run dev
```

### SECS/GEM Setup
```bash
cd secsgem
pip install -r requirements.txt
# Configure mqtt.json and equipments.json in src/config/
python main.py
```

## MQTT Topics Structure

### Equipment Status
```
equipment_status/
├── communication_state/<machine>
├── control_state/<machine>
├── event/<machine>
└── alarm/<machine>
```

### Equipment Control
```
equipment_control/
├── enable/<machine>
└── disable/<machine>
```

## Configuration

### Equipment Configuration (equipments.json)
```json
{
    "equipments": [
        {
            "equipment_name": "TNF-61",
            "equipment_model": "FCL",
            "address": "192.168.226.161",
            "port": 5000,
            "session_id": 61,
            "active": true,
            "enable": true
        }
    ]
}
```

### MQTT Configuration (mqtt.json)
```json
{
    "host": "localhost",
    "port": 1883,
    "username": "your_username",
    "password": "your_password"
}
```

## License
MIT License
```