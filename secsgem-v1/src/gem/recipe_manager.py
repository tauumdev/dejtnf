
import logging
import os
import xml.etree.ElementTree as ET

logger = logging.getLogger("app_logger")

path = "files/recipes"


def get_version_receipe(ppbody: str):
    """
    Get version of recipe
    Args:
    - recipe: str
    """
    try:
        _hml = ET.fromstring(ppbody.decode("utf-8"))
        _version = _html.
    except Exception as e:
        logger.warning(f"Error in get_version_receipe: {e}")
        return None


def get_recipes(equipment_name: str, recipe_name: str = None):
    """
    Get recipe store
    Args:
    - equipment_name: str
    - recipe_name: str if not None, get data recipe by name else get all recipes in equipment
    """

    try:
        equipment_path = os.path.join(path, equipment_name + "/" + "current")
        if not os.path.exists(equipment_path):
            return {"error": "Equipment not found"}
        if recipe_name is not None:
            with open(os.path.join(equipment_path, recipe_name), "r") as f:
                return {"recipe_name": recipe_name, "recipe_data": f.read()}
        return [f for f in os.listdir(equipment_path) if os.path.isfile(os.path.join(equipment_path, f))]
    except Exception as e:
        logger.warning(f"Error in get_recipe_store: {e}")
        return {"error": "Error in get_recipe_store"}


def save_recipe(equipment_name: str, recipe_name: str, recipe_data: str):
    """
    Save recipe store
    """
    try:
        equipment_path = os.path.join(path, equipment_name + "/" + "upload")
        if not os.path.exists(equipment_path):
            os.makedirs(equipment_path)
        with open(os.path.join(equipment_path, recipe_name), "w") as f:
            f.write(recipe_data)
        return True
    except Exception as e:
        print(f"Error in save_recipe_store: {e}")
        return False
