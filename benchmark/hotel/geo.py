import stateflow
from dataclasses import dataclass
import json
from typing import List
from math import radians, cos, sin, asin, sqrt

@dataclass
class GeoPoint:

    hotelId: str
    lat: float
    lon: float

@stateflow.stateflow
class Geo:

    geo_data = ""

    MAX_SEARCH_RESULTS = 5
    MAX_SEARCH_RADIUS = 10

    def __init__(self, geo_id: str):
        self.geo_id: str = geo_id
        self.geo_points: List[GeoPoint] = []

        self._load_data()

    def _load_data(self):
        data = json.load(open('data/geo.json'))
        for d in data:
            self.geo_points.append(GeoPoint(d["hotelId"], float(d["lat"]), float(d["lon"])))

        for hotel_id in range(6, 80):
            lat = 37.7835 + float(hotel_id)/500.0 * 3
            lon = -122.41 + float(hotel_id)/500.0 * 4

            self.geo_points.append(GeoPoint(hotel_id, lat, lon))

    def _dist(self, lat1, long1, lat2, long2):
        """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees)

        Taken from: https://medium.com/analytics-vidhya/finding-nearest-pair-of-latitude-and-longitude-match-using-python-ce50d62af546
        """
        # convert decimal degrees to radians
        lat1, long1, lat2, long2 = map(radians, [lat1, long1, lat2, long2])
        # haversine formula
        dlon = long2 - long1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        # Radius of earth in kilometers is 6371
        km = 6371 * c
        return km

    def nearby(self, lat: str, lon: str) -> List[str]:
        all_distances = [(point.hotelId, self._dist(point.lat, point.lon, float(lat), float(lon))) for point in self.geo_points]
        all_distances.sort(key=lambda x: x[1], reverse=False)

        limit_distances = all_distances[0:self.MAX_SEARCH_RESULTS]
        return list([x[0] for x in limit_distances])

    def __key__(self):
        return self.geo_id
