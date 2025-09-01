import os
import requests
import pandas as pd
from math import radians, cos, sin, asin, sqrt
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('GOOGLE_API_KEY')
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

def fetch_places(keyword, fields):
    url = (
        f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?keyword={keyword}&location={LOCATION}&radius={RADIUS}&key={API_KEY}'
    )
    response = requests.get(url)
    results = response.json().get('results', [])
    data = []
    for place in results:
        loc = place.get('geometry', {}).get('location', {})
        lat2 = loc.get('lat')
        lon2 = loc.get('lng')
        distance = haversine(lat1, lon1, lat2, lon2) if lat2 and lon2 else None
        distance_km = round(distance / 1000, 2) if distance else None
        entry = {}
        for field in fields:
            if field == 'Distance (KM)':
                entry[field] = distance_km
            elif field == 'Area Name':
                entry[field] = place.get('name')
            elif field == 'Institution Name':
                entry[field] = place.get('name')
            elif field == 'Address':
                entry[field] = place.get('vicinity')
            elif field == 'Rating':
                entry[field] = place.get('rating')
            elif field == '#User Ratings':
                entry[field] = place.get('user_ratings_total')
        data.append(entry)
    return pd.DataFrame(data)

# 1. Dance classes
dance_fields = ['Name', 'Address', 'Rating', '#User Ratings', 'Distance (KM)']
df_dance = fetch_places('dance classes', dance_fields)
df_dance = df_dance.sort_values(by='Distance (KM)', ascending=True)
df_dance.to_excel('dance_classes_nearby.xlsx', index=False)

# 2. Major areas
area_fields = ['Area Name', 'Distance (KM)']
df_areas = fetch_places('area', area_fields)
df_areas = df_areas.sort_values(by='Distance (KM)', ascending=True)
df_areas.to_excel('nearby_areas.xlsx', index=False)

# 3. Education institutions
edu_fields = ['Institution Name', 'Address', 'Distance (KM)']
df_edu = fetch_places('school', edu_fields)
df_edu = df_edu.sort_values(by='Distance (KM)', ascending=True)
df_edu.to_excel('nearby_education_institutions.xlsx', index=False)