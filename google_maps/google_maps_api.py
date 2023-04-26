from typing import Any, Dict, Optional

from pydantic import BaseModel, Extra, root_validator

from langchain.utils import get_from_dict_or_env
import googlemaps

class GoogleMapsAPIWrapper(BaseModel):
    """Wrapper for Google Maps API."""
    maps_api: Any  #: :meta private:
    google_api_key: Optional[str] = None

    class Config:
        """Configuration for this pydantic object."""
        extra = Extra.forbid

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that api key and python package exists in environment."""
        google_api_key = get_from_dict_or_env(
            values, "GOOGLE_MAPS_API_KEY", "GOOGLE_MAPS_API_KEY"
        )
        values["google_api_key"] = google_api_key

        try:
            maps_api = googlemaps.Client(key=google_api_key)
        except ImportError:
            raise ImportError(
                "googlemaps library is not installed. "
                "Please install it with `pip install googlemaps`"
            )

        values["maps_api"] = maps_api

        return values

    def get_travel_time_info(self, origin: str, destination: str, mode: str = "driving") -> Dict:
        """Return travel time and other relevant information between origin and destination."""

        if mode not in ["driving", "transit", "walking", "bicycling"]:
            raise ValueError("Invalid mode of transportation")

        directions = self.maps_api.directions(origin, destination, mode=mode)

        if directions:
            route = directions[0]
            leg = route["legs"][0]
            duration = leg["duration"]["value"]
            distance = leg["distance"]["value"]
            start_address = leg["start_address"]
            end_address = leg["end_address"]

            return {
                "origin": start_address,
                "destination": end_address,
                "travel_time_seconds": duration,
                "distance_meters": distance,
                "mode": mode,
            }
        else:
            return {"Error": "Directions not found"}

    def run(self, origin: str, destination: str, mode: str = "driving") -> str:
        """Calculate travel time between origin and destination using the specified mode."""
        print(mode)
        if mode not in ["driving", "transit", "walking", "bicycling"]:
            raise ValueError("Invalid mode of transportation")

        directions = self.maps_api.directions(origin, destination, mode=mode)

        if directions:
            route = directions[0]
            leg = route["legs"][0]
            duration = leg["duration"]["value"]
            return f"Travel time between {origin} and {destination}: {duration} seconds"
        else:
            return f"Error: Directions not found"