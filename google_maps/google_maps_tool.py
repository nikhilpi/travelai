from langchain.tools.base import BaseTool
from .google_maps_api import GoogleMapsAPIWrapper
import json
from typing import Dict

class TravelTimeInfo(BaseTool):
    """Tool that adds the capability to calculate travel time and distance using the Google Maps API."""

    name = "Travel Time Info"
    description = (
        "A wrapper around Google Maps API. "
        "Useful for calculating travel time using a mode of transportation between two addresses. "
        "Input should be a string seperated starting with the mode of transportation (\"driving\", \"transit\", \"walking\", \"bicycling\") followed by ':' "
        "the origin and destination addresses seperated by '<>'. "
        "For example: 'driving: New York City <> Los Angeles' " 
        "If you don't know the mode of transportation, you should ask the user for it."
    )
    api_wrapper: GoogleMapsAPIWrapper

    def _run(self, query: str) -> str:
        """Use the tool."""
        mode = str(query.split(":")[0].strip(" ").strip("'"))
        locations = query.split(":")[1].split("<>")

        return str(self.api_wrapper.run(locations[0], locations[1], mode=mode))

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("TravelTimeInfo does not support async")

    def _json_parse(self, query: str) -> Dict:
        """Parse the query as a json object."""
        try:
            query = json.loads(query)
        except json.JSONDecodeError:
            raise ValueError("Invalid json object")

        return query
     