"""
making a map with films nearby
"""
import argparse
import folium
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable
from haversine import haversine

parser = argparse.ArgumentParser()
parser.add_argument('year', type=int)
parser.add_argument('latitude', type=float)
parser.add_argument('longitude', type=float)
parser.add_argument('file_path', type=str)

args = parser.parse_args()

def read_file(file_path: str):
    """
    reads file and yields one line to optimize process of analysing
    >>> read_file('snow')
    'File not found'
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for cnt, line in enumerate(file):
                if cnt < 14:
                    continue
                yield line
    except FileNotFoundError:
        return 'File not found'
    return None

def get_films(file_path: str, year: int, latitude: float, longitude: float) -> list:
    """
    analyses file with films and returns 10 of them
    in the nearest locations
    >>> get_films('smth.list', 2000, 49.83826, 24.02324)
    'File not found'
    """
    film_list = []
    geolocator = Nominatim(user_agent="Address")
    if read_file(file_path) == 'File not found':
        return 'File not found'
    for line in read_file(file_path):
        line = line.replace('\t', ' ').replace('} ', ' (').replace(') ', ' (')
        line = line.replace('"', '').strip('\n')
        line_list = line.split(' (')
        if line_list[1][:4] == str(year):
            if line[-1] != ')':
                address = line_list[-1].strip()
            else:
                address = line_list[-2].strip()
            try:
                location = geolocator.geocode(address)
                distance = haversine((latitude, longitude), \
                                        (location.latitude, location.longitude))
                film_list.append((distance, line_list[0], location.latitude, location.longitude))
            except (AttributeError, GeocoderUnavailable):
                continue
    film_list = sorted(film_list, key=lambda x: x[0])
    return film_list[:10]

def generate_map(file_path: str, year: int, latitude: float, longitude: float):
    """
    generates a map with 10 or less popups with films
    >>> generate_map('smth.list', 2000, 49.83826, 24.02324)
    'File not found'
    >>> generate_map('locations_0.list', 3020, 49.83826, 24.02324)
    'No films found'
    >>> generate_map('locations_0.list', 2000, 49.83826, 24.02324)
    'Map created'
    """
    films = get_films(file_path, year, latitude, longitude)
    if not films:
        return 'No films found'
    if films == 'File not found':
        return 'File not found'
    film_map = folium.Map(tiles='Stamen Terrain',
            location=[args.latitude, args.longitude],
            zoom_start=10)
    for i in films:
        film_map.add_child(folium.Marker(location=[i[2], i[3]],
                                    popup=f'{i[1]}',
                                    icon=folium.Icon(color='red', icon='heart')))
    film_map.save(f"Map_{year}.html")
    return 'Map created'

if __name__ == '__main__':
    print(generate_map(args.file_path, args.year, args.latitude, args.longitude))
