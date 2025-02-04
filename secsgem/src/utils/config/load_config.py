import logging
import json
import os

logger = logging.getLogger("app_logger")


def load_equipments_config(path: str):
    """
    Load the equipments configuration from the configuration file.
    """
    try:
        with open(path, "r", encoding="utf-8") as file:
            equipments = json.load(file)
            return equipments.get("equipments", [])
    except FileNotFoundError:
        logger.error("File not found: %s", path)
        logger.info("Creating a new configuration file. at %s", path)

        os.makedirs(os.path.dirname(path), exist_ok=True)
        return {"equipments": []}
    except json.JSONDecodeError:
        logger.error("Invalid JSON format in the file: %s", path)
        return {"equipments": []}
    except Exception as e:
        logger.error("Failed to load configuration file: %s", e)
        return {"equipments": []}
