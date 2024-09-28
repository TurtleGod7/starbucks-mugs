#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import geocoder
import json
from time import sleep
import os
import json
import folium
import base64
import argparse
import copy
from re import sub
from re import search

USERAGENTEMAIL = os.environ.get("")

def modify_and_encode_svg(svg_path, new_color):
    with open(svg_path, 'r') as file:
        svg_content = file.read()
    encoded_svg = svg_content
    modified_svg_content = encoded_svg.replace('#000000', f'{new_color}')
    svg_base64 =  base64.b64encode(modified_svg_content.encode('utf-8')).decode()
    data_uri = f"data:image/svg+xml;base64,{svg_base64}"
    return data_uri

def visualize(data_path, output_path="index.html"):
    f = open(data_path, 'r')
    data = json.load(f)
    m = folium.Map(location=[34.0549076, -118.242643], zoom_start=4)
    owned_count = 0
    total_count = len(data.keys())
    print("got total count", total_count)
    for c, d in data.items():
        tooltip = c
        if d.get('owned') is True:
            owned_count += 1
        if 'latlong' not in d:
            print("can't find latlong")
            continue

        imgPath = d.get('img', "")
        url = d.get('url', "")
        description = d.get('description', "")
        markerData = f'<img src="{imgPath}" width="200"><br><a href="{url}">Link</a><br>{description}'
        iframe = folium.IFrame(markerData, width=250, height=300)
        popup = folium.Popup(iframe, max_width=300)
        color = 'green' if d['owned'] is True else 'orange'
        icon_image = modify_and_encode_svg('./assets/icon.svg', color)
        icon = folium.CustomIcon(icon_image, icon_size=(30, 30))  # Adjust size as needed
        folium.Marker(
                location=d["latlong"],
                popup=popup,
                icon=icon,
                fill_opacity=0.6,
                tooltip=tooltip
        ).add_to(m)

    footer_html = f"<div style='position: fixed; bottom: 10px; height: 20px; background-color: white; z-index:9999; font-size:16px;'>Credit to <a href='https://starbucks-mugs.com/category/been-there/'>starbucks-mugs.com</a> for the initial seed data. See scripts at my <a href='https://github.com/TurtleGod7/starbucks-mugs'>Github</a></div>"
    legend_html = "<div style='position: fixed; top: 40px; left: 50px;  padding: 10px 10px 10px 10px;  height: 80px; background-color: white; z-index:9999; font-size:16px;'>Legend<br/><svg height='10' width='10'><circle cx='5' cy='5' r='5' fill='green' /></svg> Owned &nbsp;<br/><svg height='10' width='10'><circle cx='5' cy='5' r='5' fill='orange' /></svg> Not Owned</div>"

    header_html = f"<div style='position: fixed; top: 10px; left: 50px; width: 300px; height: 20px; background-color: white; z-index:9999; font-size:16px;'><b>Owned: {owned_count} / Total: {total_count}</b></div>"
    m.get_root().html.add_child(folium.Element(header_html))
    m.get_root().html.add_child(folium.Element(legend_html))
    m.get_root().html.add_child(folium.Element(footer_html))

    m.save(output_path)

def read_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def update(new, old):
    ret = {}

    for key, oldEntry in old.items():
        newEntry = new.get(key)
        if newEntry is None:
            ret[key] = oldEntry
            continue

    for key, newEntry in new.items():
        oldEntry = old.get(key)
        ret[key] = newEntry # add new values

    return ret

def modify_and_encode_svg(svg_path, new_color):
    with open(svg_path, 'r') as file:
        svg_content = file.read()
    encoded_svg = svg_content
    modified_svg_content = encoded_svg.replace('#000000', f'{new_color}')
    svg_base64 =  base64.b64encode(modified_svg_content.encode('utf-8')).decode()
    data_uri = f"data:image/svg+xml;base64,{svg_base64}"
    return data_uri


def fetch_complete_list():
    # Web scraper for all series
    webpages = {
        'https://starbucks-mugs.com/category/been-there/' : 38,
        'https://starbucks-mugs.com/category/discovery/' : 3,
        'https://starbucks-mugs.com/category/you-are-here/' : 53
    }
    all_titles = []
    for webpage, page in webpages.items():
        for page in range(1, page + 1):
            url = webpage if page == 1 else f'{webpage}page/{page}/'
            titles = fetch_url(url)
            all_titles.extend(titles)
    return all_titles

def fetch_url(url):
    titles = []
    resp = requests.get(url)
    if resp.status_code != 200:
        raise Exception("Failed to fetch page")
    soup = BeautifulSoup(resp.text, 'html.parser')
    for entry in soup.find_all(class_='mug'):
        title = entry.find_all(class_='entry-title post-title')
        imgs = entry.find_all('img')
        ee = entry.find_all(class_='entry')
        if title is None or len(title) == 0:
            print("skip entry without title", entry)
            continue
        
        try: # Cleans title to enable owned_mugs.txt to reflect in the final_data.json
            new_title = title[0].text.replace("– ", "")
        except Exception as e:
            print("Failed to clean Title Key", new_title)
            print(e)
        
        try: # Cleans the key to be able to recieve latlong from API
            new_key = title[0].text.split("–")[1]
            check = search(r'\(([^)]+)\)', new_key)
            if check: new_key = check.group(1)
            new_key = sub(r'\d+\s*\w*', '', new_key)
            new_key = new_key.strip()
        except Exception as e:
            print("Failed to clean Locational Key", new_key)
            print(e)
        
        row = {
            'title': new_title,
            'locationkey' : new_key,
            'url': entry.find('a')['href'],
            'img': imgs[0]['src'],
            'description': ee[0].text
        }
        titles.append(row)
    return titles

def read_owned():
    with open('./data/owned_mugs.txt', 'r') as file:
        owned = file.readlines()
    for str in owned:
        str.replace("– ", "")
    return [line.strip() for line in owned]

def read_latlong_overrides():
    with open('./data/latlong_overrides.json', 'r') as file:
        overrides = json.load(file)
        return overrides

'''Original Code:
def get_latlong(address, api_key=''):
    base_url = 'https://maps.googleapis.com/maps/api/geocode/json'
    endpoint = f"{base_url}address={address}&key={api_key}"
    print("trying to fetch latlong for", endpoint)
    params = {'sensor': 'false', 'address': address, 'key': api_key}
    resp = requests.get(base_url, params=params)
    if resp.status_code != 200:
        print(f"Failed to fetch latlong for {address}. Status code: {resp.status_code}")
        raise Exception(f"Failed to fetch latlong for {address}. Status code: {resp.status_code}")
    data = resp.json()
    if data['status'] != 'OK':
        print(f"Failed to fetch latlong for {address}. Status: {data['status']}")
        raise Exception(f"Failed to fetch latlong for {address}. Status: {data['status']}")
    lat = data['results'][0]['geometry']['location']['lat']
    lng = data['results'][0]['geometry']['location']['lng']
    sleep(1) # for rate limiting
    return [lat, lng]
'''

def get_latlong(address):
    base_url = 'https://nominatim.openstreetmap.org/search'
    headers = {'User-Agent': 'starbucks-mugs/0.2 ('+ USERAGENTEMAIL +')'} # Required by OSM in their terms of use
    params = {'q': address, 'format': 'json', 'limit': 1}
    endpoint = f"{base_url}q={params}"
    print("trying to fetch latlong for", endpoint)
    resp = requests.get(base_url, params=params, headers=headers)
    if resp.status_code != 200:
        print(f"Failed to fetch latlong for {address}. Status code: {resp.status_code}")
        raise Exception(f"Failed to fetch latlong for {address}. Status code: {resp.status_code}")
    data = resp.json()
    if not data:
        print(f"Failed to fetch latlong for {address}.")
        raise Exception(f"Failed to fetch latlong for {address}.")
    lat = float(data[0]['lat'])
    lng = float(data[0]['lon'])
    sleep(1) # for rate limiting
    return [lat, lng]

def prepare(previous_data_path, output_file_path):

    owned_mugs = read_owned()
    latlong_overrides = read_latlong_overrides()
    all_titles = fetch_complete_list()
    data = {}
    previous_data = {}

    if previous_data_path:
        previous_data = read_json(previous_data_path)
        data = copy.deepcopy(previous_data)

    def insert_owned_mugs(data):
        # update the titles of ownership
        for title in all_titles:
            data[title['title']] = {
                'owned': title['title'] in owned_mugs,
                **title
            }
            for m in owned_mugs:
                if m not in data:
                    data[m] = {
                        'owned': True
                    }
        return data

    def clean_keys(data):
        updated = {}
        for k, v in data.items():
            print(k)
            if "– " in k:
                try:
                    new_key = k.replace("– ", "")
                    updated[new_key] = v
                except Exception as e:
                    print("Failed to clean key 1", k)
                    print(e)
            else:
                try:
                    new_key = k.replace("â€“ ", "")
                    updated[new_key] = v
                except Exception as e:
                    print("Failed to clean key 2", k)
                    print(e)
        return updated

    def get_addresses(data, cache=[]):
        for key, entry in data.items():
            location_key = entry.get('locationkey')
            if location_key == "":
                for i in range(1):
                    try:
                        location_key = entry["title"].text.split("–")[1]
                        check = search(r'\(([^)]+)\)', location_key)
                        if check: location_key = check.group(1)
                        location_key = sub(r'\d+\s*\w*', '', location_key)
                        location_key = location_key.strip()
                    except:
                        entry['title'] = key
            try:
                if location_key in latlong_overrides:
                    entry['latlong'] = latlong_overrides[location_key]
                    print("using override for", location_key)
                else:
                    if location_key in cache: # Code that checks cache to reducing querying the api
                        for k in data.items:
                            if location_key == k['locationkey']:
                                try:
                                    entry['latlong'] = k['latlong']
                                except Exception as e:
                                    print(f"Couldn't retrieve cached data because of Exception: {e}\nReverting back to querying the API")
                                    break
                    else:
                        cache.append(location_key)
                    
                    entry['latlong'] = get_latlong(location_key)
            except Exception as e:
                print(f"Failed to get latlong for {location_key}")
                print(e)
        return data
    
    # Cleaning normal keys for new naming scheme
    data = insert_owned_mugs(data)
    data = clean_keys(data)
    data = get_addresses(data)
    data = update(previous_data, data)
    # Gets latlong using the previous name which was used for this
    
    
    with open(output_file_path, 'w') as file:
        json.dump(data, file, indent=4)

def backup(input_file, output_file):
    data = read_json(input_file)
    with open(output_file, 'w') as file:
        json.dump(data, file, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CLI for data manipulation tasks")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Backup command
    backup_parser = subparsers.add_parser("backup", help="Backup old file")
    backup_parser.add_argument("--input", default="final_data.json", help="Input file (default: final_data.json)")
    backup_parser.add_argument("--output", default="old_data.json", help="Output file (default: old_data.json)")

    # Prepare command
    prepare_parser = subparsers.add_parser("prepare", help="Prepare data")
    prepare_parser.add_argument("--output", required=True, help="Output file")
    prepare_parser.add_argument("--previous", required=False, help="Previous Data File", default="final_data.json")

    # Visualize command
    visualize_parser = subparsers.add_parser("visualize", help="Visualize data")
    visualize_parser.add_argument("--input", default="final_data.json", help="Input file (default: final_data.json)")
    visualize_parser.add_argument("--output", default="index.html", help="Output file (default: index.html)")

    update_parser = subparsers.add_parser("update", help="update data")
    update_parser.add_argument("--backup_path", default="data/final_data.json.bak", help="backup file")
    update_parser.add_argument("--output", required=False, help="Output file", default="index.html")
    update_parser.add_argument("--previous", required=False, help="Previous Data File", default="data/final_data.json")
    args = parser.parse_args()

    if args.command == "backup":
        backup(args.input, args.output)
    elif args.command == "prepare":
        prepare(args.previous, args.output)
    elif args.command == "visualize":
        visualize(args.input, args.output)
    elif args.command == "update":
        # backup old data with .bak
        backup(args.previous, args.backup_path)
        # preapare new file. overwriting the new one
        prepare(args.previous, args.previous)
        # create the html
        visualize(args.previous, args.output)
