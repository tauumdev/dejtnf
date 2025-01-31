
import json
import requests
from typing import Optional, Union, List, Dict
from urllib.parse import urlencode, quote


class LotInformation:
    """
    Class to handle Lot Information
    Args:
        lot_id: Lot ID
    """

    def __init__(self, lot_id: str):
        self.lot_id = lot_id
        self.lot_data = None
        self.field_by_name = {}
        self.field_by_desc = {}
        # self._load_data()
        self._load_data_api()

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
            base_url: str,
            log_id: str,
            en_number: str,
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

    def _load_data_api(self):
        api_client = self._LotInfoAPI(
            base_url="http://utlwebprd1/OEEwebAPI",
            log_id="1231562",
            en_number="226383"
        )
        try:
            self.lot_data = api_client.get_lot_info([self.lot_id])

            if self.lot_data and isinstance(self.lot_data, list):
                output_info = self.lot_data[0].get("OutputLotInfo", [])
                for field in output_info:
                    self.field_by_name[field["FieldName"]] = field["Value"]
                    if "Description" in field:
                        self.field_by_desc[field["Description"]] = field

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error: {str(e)}")

    def _load_data(self):
        print("Loading data from API")
        try:
            with open('files/lotdetail.json', 'r', encoding='utf-8') as file:
                self.lot_data = json.load(file)
                if self.lot_data and isinstance(self.lot_data, list):
                    output_info = self.lot_data[0].get("OutputLotInfo", [])
                    for field in output_info:
                        self.field_by_name[field["FieldName"]] = field["Value"]
                        if "Description" in field:
                            self.field_by_desc[field["Description"]] = field
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error: {str(e)}")

    def get_field_value(self, field_names: Union[str, List[str]]) -> Dict:
        """
        Get field values with API caching
        Args:
            field_names: Single field name or list of field names
        """
        if not self.lot_data:
            return {"status": False, "message": "Data not loaded", "data": None}

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
        if not self.lot_data:
            return {"status": False, "message": "Data not loaded", "data": None}

        descriptions = [descriptions] if isinstance(
            descriptions, str) else descriptions
        result = {desc: self.field_by_desc.get(
            desc, "Not found") for desc in descriptions}

        return {"status": True, "message": "Success", "data": result}


# if __name__ == "__main__":

#     print("Lot Information")

#     lot_info = LotInformation("RNMFS0030.1")
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

#     lot_info = LotInformation("RNMFS0030.1")
#     result_by_description = lot_info.get_field_by_description(
#         ["Lot Qty", "LOT_STATUS"])
#     print(result_by_description)
