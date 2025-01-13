import json
import logging

logger = logging.getLogger("config_loader")


def load_config(file_path: str, required_keys: list[str]) -> dict:
    """
    Load and validate a JSON configuration file.

    Args:
        file_path (str): Path to the configuration file.
        required_keys (list[str]): List of keys that must be present in the configuration.

    Returns:
        dict: The loaded configuration.

    Raises:
        FileNotFoundError: If the configuration file is not found.
        ValueError: If the JSON is invalid or required keys are missing.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError("Config file not found:%s", file_path)
    except json.JSONDecodeError as e:
        raise ValueError("Failed to parse JSON in %s:%s", file_path, e)

    for key in required_keys:
        if key not in config:
            raise ValueError(
                "Missing required config key in %s:%s", file_path, key)
    return config
