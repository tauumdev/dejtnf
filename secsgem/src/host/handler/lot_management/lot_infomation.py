import json
import logging
import os
from typing import Dict, List, Optional, Union
from urllib.parse import quote, urlencode

import requests
from dotenv import load_dotenv
# from config.app_config import
logger = logging.getLogger("app_logger")


class LotInformation:
    """
    Class to handle Lot Information
    Args:
        lot_id: Lot ID
    """

    def __init__(self, lot_id: str):
        self.lot_id = lot_id
        self.status = False
        self.message = None
        self.lot_data = None
        self.field_by_name = {}
        self.field_by_desc = {}
        self._load_data_from_api()

    def _load_data_from_api(self):
        """
        Load Lot Information data from API
        """
        # API_SERVER = localhost
        # API_PORT = 3000
        # API_ENDPOINT = api

        load_dotenv()
        api_server = os.getenv("API_SERVER")
        api_port = os.getenv("API_PORT")
        api_endpoint = os.getenv("API_ENDPOINT")

        try:
            # create url
            api_url = f"http://{api_server}:{api_port}/{api_endpoint}/lotinfo/{self.lot_id}"
            # print(api_url)
            response = requests.get(
                api_url,
                timeout=10,
                headers={'Accept': 'application/json'}
            )
            response.raise_for_status()

            # Validate response format
            self.lot_data = response.json()

            if self.lot_data and isinstance(self.lot_data, dict):
                self.status = self.lot_data.get("Status", False)
                self.message = self.lot_data.get("Message", None)
                if not self.status:
                    logger.error(
                        "Failed to retrieve Lot:%s, Information: %s", self.message, self.message)
                    self.lot_data = None
                    return
                output_info = self.lot_data.get("OutputLotInfo", [])
                for field in output_info:
                    self.field_by_name[field["FieldName"]] = field["Value"]
                    if "Description" in field:
                        self.field_by_desc[field["Description"]] = field
            else:
                logger.error("Failed to load Lot Information: %s",)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            # print(f"Error: {str(e)}")
            logger.error("Failed to load Lot Information: %s", str(e))

    def _load_data_from_file(self):
        """
        Load Lot Information data from file
        """
        lot_info_api = self._LotInfoAPI()
        try:
            self.lot_data = lot_info_api.get_lot_info([self.lot_id])
            if self.lot_data and isinstance(self.lot_data, list):
                self.status = self.lot_data[0].get("Status", False)
                self.message = self.lot_data[0].get("Message", None)
                if not self.status:
                    logger.error(
                        "Failed to retrieve Lot:%s, Information: %s", self.message, self.message)
                    self.lot_data = None
                    return
                output_info = self.lot_data[0].get("OutputLotInfo", [])
                for field in output_info:
                    self.field_by_name[field["FieldName"]] = field["Value"]
                    if "Description" in field:
                        self.field_by_desc[field["Description"]] = field

        except (FileNotFoundError, json.JSONDecodeError) as e:
            # print(f"Error: {str(e)}")
            logger.error("Failed to load Lot Information: %s", str(e))

    def get_field_value(self, field_names: Union[str, List[str]]) -> Dict:
        """
        Get field values with API caching
        Args:
            field_names: Single field name or list of field names
        """
        if not self.status:
            return {"status": False, "message": self.message, "data": None}

        field_names = [field_names] if isinstance(
            field_names, str) else field_names
        result = {name: self.field_by_name.get(
            name, "Not found") for name in field_names}

        return {"status": True, "message": "Success", "data": result}

    def get_field_by_description(self, descriptions: Union[str, List[str]]) -> Dict:
        """
        Get fields by description with API fallback
        Args:
            descriptions: Single description or list of descriptions
        """
        if not self.status:
            return {"status": False, "message": self.message, "data": None}

        descriptions = [descriptions] if isinstance(
            descriptions, str) else descriptions
        result = {desc: self.field_by_desc.get(
            desc, "Not found") for desc in descriptions}

        return {"status": True, "message": "Success", "data": result}

    class _LotInfoAPI:
        """
        Initialize API client for Lot Information
        Args:
            base_url: Base API URL (e.g., "http://utlwebprd1/OEEwebAPI")
            log_id: System log ID
            en_number: Equipment number
            token: API token (default: OEE_WEB_API)
        """

        def __init__(
            self,
            base_url: str = "http://utlwebprd1/OEEwebAPI",
            log_id: str = "1231562",
            en_number: str = "226383",
            token: str = "OEE_WEB_API"
        ):

            self.base_url = base_url.rstrip('/')
            self.log_id = log_id
            self.en_number = en_number
            self.token = token
            self.timeout = 10  # seconds

        def _build_url(self, lot_ids: List[str]) -> str:
            """
            Construct the API URL with proper encoding
            Args:
                lot_ids: List of Lot IDs to query
            Returns:
                Properly encoded API URL
            """
            # Create busItem parameter structure
            bus_item = [{"LotID": lot_id} for lot_id in lot_ids]

            # Build query parameters
            params = {
                "logID": self.log_id,
                "enNumber": self.en_number,
                "token": self.token,
                "busItem": json.dumps(bus_item)
            }

            # URL encode with proper handling
            encoded_params = urlencode(
                params, safe=":/[]{}',", quote_via=quote)

            return f"{self.base_url}/DataForOEE/LotInfo/GetLotInfo?{encoded_params}"

        def get_lot_info(
            self,
            lot_ids: List[str],
            max_retries: int = 3
        ) -> Optional[Dict]:
            """
            Get lot information from API
            Args:
                lot_ids: List of Lot IDs to retrieve
                max_retries: Number of retry attempts
            Returns:
                JSON response data or None on failure
            """
            url = self._build_url(lot_ids)
            for attempt in range(max_retries):
                try:
                    response = requests.get(
                        url,
                        timeout=self.timeout,
                        headers={'Accept': 'application/json'}
                    )

                    response.raise_for_status()

                    # Validate response format
                    data = response.json()
                    # for lot in data:
                    if not isinstance(data, list):
                        raise ValueError("Unexpected response format")
                    return data

                except requests.exceptions.RequestException as e:
                    print(
                        f"API request failed(attempt {attempt+1}/{max_retries}): {str(e)}")
                    if attempt == max_retries - 1:
                        return None

                except json.JSONDecodeError:
                    print("Failed to parse JSON response")
                    return None

            return None

        def get_single_lot_info(self, lot_id: str) -> Optional[Dict]:
            """
            Convenience method for single Lot ID queries
            """
            return self.get_lot_info([lot_id])


# if __name__ == "__main__":
#     # Example usage
#     lot_info = LotInformation("ONCPS0453.2")

#     result_by_field = lot_info.get_field_value(
#         [
#             "LOT PARAMETERS",
#             "SASSYPACKAGE",
#             "QTY",
#             "LOT_STATUS",
#             "ADEVICENAME",
#             "ON_OPERATION",
#             "LOCATION_CODE",
#             "PROCEDURE_CODE"
#         ])
#     print(result_by_field)

#     result_by_description = lot_info.get_field_by_description(
#         ["Lot Qty", "LOT_STATUS"])
#     print(result_by_description)
