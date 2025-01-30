import requests
from typing import Union, List, Dict, Optional
from functools import lru_cache
import time


class LotInformationAPI:
    def __init__(
        self,
        lot_id: str,
        api_url: str,
        api_key: Optional[str] = None,
        cache_ttl: int = 300
    ):
        self.lot_id = lot_id
        self.api_url = api_url
        self.api_key = api_key
        self.cache_ttl = cache_ttl
        self.last_fetch_time = 0
        self.field_by_name = {}
        self.field_by_desc = {}
        self.lot_data = None

    def _get_headers(self) -> Dict:
        """Generate request headers with authentication"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid"""
        return time.time() - self.last_fetch_time < self.cache_ttl

    def fetch_data(self, force_refresh: bool = False) -> bool:
        """Fetch data from API with caching and retry logic"""
        if not force_refresh and self._is_cache_valid() and self.lot_data:
            return True

        try:
            response = requests.get(
                f"{self.api_url}/lots/{self.lot_id}",
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()

            self.lot_data = response.json()
            self._process_data()
            self.last_fetch_time = time.time()
            return True

        except requests.exceptions.RequestException as e:
            print(f"API Error: {str(e)}")
            return False

    def _process_data(self):
        """Process API response into lookup dictionaries"""
        if self.lot_data and isinstance(self.lot_data, dict):
            output_info = self.lot_data.get("OutputLotInfo", [])
            self.field_by_name.clear()
            self.field_by_desc.clear()

            for field in output_info:
                self.field_by_name[field["FieldName"]] = field["Value"]
                if "Description" in field:
                    self.field_by_desc[field["Description"]] = field

    # @lru_cache(maxsize=128)
    def get_field_value(self, field_names: Union[str, List[str]]) -> Dict:
        """
        Get field values with API caching
        Args:
            field_names: Single field name or list of field names
        """
        if not self.fetch_data():
            return {"status": False, "message": "API fetch failed", "data": None}

        fields = [field_names] if isinstance(field_names, str) else field_names
        result = {name: self.field_by_name.get(name, None) for name in fields}

        return {
            "status": True,
            "message": "Success",
            "data": result
        }

    def get_field_by_description(self, descriptions: Union[str, List[str]]) -> Dict:
        """
        Get fields by description with API fallback
        Args:
            descriptions: Single description or list of descriptions
        """
        if not self.fetch_data():
            return {"status": False, "message": "API fetch failed", "data": None}

        descs = [descriptions] if isinstance(
            descriptions, str) else descriptions
        result = {desc: self.field_by_desc.get(desc, None) for desc in descs}

        return {
            "status": True,
            "message": "Success",
            "data": result
        }

    # Additional API methods
    def update_lot_info(self, payload: Dict) -> bool:
        """Update lot information through API"""
        try:
            response = requests.patch(
                f"{self.api_url}/lots/{self.lot_id}",
                json=payload,
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            self.fetch_data(force_refresh=True)  # Invalidate cache
            return True
        except requests.exceptions.RequestException as e:
            print(f"Update failed: {str(e)}")
            return False


if __name__ == "__main__":
    # Example usage
    API_ENDPOINT = "https://google.com"
    API_KEY = "your_api_key_here"

    lot_api = LotInformationAPI(
        lot_id="LOT-001",
        api_url=API_ENDPOINT,
        api_key=API_KEY
    )

    # Get field values
    result = lot_api.get_field_value(["LOT_STATUS", "QTY"])
    print(result)

    # Get by description
    desc_result = lot_api.get_field_by_description(["Lot Quantity"])
    print(desc_result)

    # Force refresh
    lot_api.fetch_data(force_refresh=True)
