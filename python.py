import os
import requests
import pandas as pd
from math import radians, cos, sin, asin, sqrt
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('GOOGLE_API_KEY')
SEARCH_QUERY = 'dance classes'
LOCATION = '12.849455,80.141448'
RADIUS = 10000  # in meters

def haversine(lat1, lon1, lat2, lon2):
    # Calculate the great circle distance between two points on the earth (in meters)
    R = 6371000  # Radius of earth in meters
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

lat1, lon1 = map(float, LOCATION.split(','))

URL = (
    f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?keyword={SEARCH_QUERY}&location={LOCATION}&radius={RADIUS}&key={API_KEY}'
)
response = requests.get(URL)
results = response.json().get('results', [])

data = []
for place in results:
    loc = place.get('geometry', {}).get('location', {})
    lat2 = loc.get('lat')
    lon2 = loc.get('lng')
    distance = haversine(lat1, lon1, lat2, lon2) if lat2 and lon2 else None
    distance_km = round(distance / 1000, 2) if distance else None  # Convert to KM and round to 2 decimals
    data.append({
        'Name': place.get('name'),
        'Address': place.get('vicinity'),
        'Rating': place.get('rating'),
        '#User Ratings': place.get('user_ratings_total'),
        'Distance (KM)': distance_km
    })

df = pd.DataFrame(data)
df = df.sort_values(by='Distance (KM)', ascending=True)  # Sort by distance, nearest first
df.to_excel('dance_classes_nearby.xlsx', index=False)