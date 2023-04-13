import json 
import requests
import numpy as np
from matplotlib import pyplot as plt


def get_sample_games(key):
    
    url = "https://api.pubg.com/shards/steam/samples"
    headers = {
        "accept": "application/vnd.api+json",
         "Authorization": f"Bearer {key}"
    }

    response = requests.get(url, headers=headers)

    return response.json()

def get_match(key, match_id):
    url = f"https://api.pubg.com/shards/steam/matches/{match_id}"
    headers = {
        "accept": "application/vnd.api+json",
         "Authorization": f"Bearer {key}"
    }
    response = requests.get(url, headers=headers)
    return response.json()


def parse_telemetry_link(match):
    # takes in match data and outputs telemetry link
    for obj in match["included"]:
        # if not player then skip
        if obj['type'] != "asset":
            continue
        if obj['attributes']['name'] != 'telemetry':
            continue
        link = obj['attributes']['URL'] 
        return link


def get_telemetry_data(link):
    response = requests.get(link)
    return response.json()


def parse_parachute_landings(telemetry):

    # add game_id
    landing_data = []

    plane_data = []

    for data in telemetry:

        # if parachute landing then log data
        if "_T" in data and data["_T"] == "LogParachuteLanding":
            landing_data.append([data['character']['location']['x'], data['character']['location']['y']])
        
        
        # if vehicle is not or not set continue
        if 'vehicle' not in data or data['vehicle'] is None:
            continue
        
        # get plane position if in plane and velocity > 0
        if data['vehicle']['vehicleType'] == 'TransportAircraft' and data['vehicle']['velocity'] > 0:
            # append x and y values
            plane_data.append([data['character']['location']['x'], data['character']['location']['y']])

    px = []
    py = []

    lx = []
    ly = []

    for i in landing_data:
        px.append(i[0])
        py.append(i[1])

    for i in plane_data:
        lx.append(i[0])
        ly.append(i[1])

    fig, ax = plt.subplots()
    import matplotlib.patches as patches
    # Create a rectangle patch with the given dimensions
    rect = patches.Rectangle((0, 0), 800000, 800000, linewidth=1, edgecolor='r', facecolor='none')
    # Add the rectangle patch to the axes
    ax.add_patch(rect)
    # Set the x and y limits of the axes to fit the rectangle
    ax.set_xlim([0, 800000])
    ax.set_ylim([0, 800000])


    ax.scatter(px, py)
    ax.scatter(lx, ly)

    # scatter edge of map
    ax.scatter([8*1000*100], [8*1000*100])

 
    p1 = plane_data[0]
    p2 = plane_data[1]

    m = (p1[1] - p2[1]) / (p1[0] - p2[0])

    b = (p1[1]-(m*p1[0]))

    axes = plt.gca()
    x_vals = np.array(axes.get_xlim())
    y_vals = b + m * x_vals
    ax.plot(x_vals, y_vals, '--')

    plt.ylim(8*1000*100, 0)

    plt.show()

def main():
    
    with open('key.json') as file:
        data = json.load(file)

    key = data['key']

    samples = get_sample_games(key)

    for sample in samples['data']['relationships']['matches']['data']:

        print(sample['id'])

        match = get_match(key, sample['id'])

        link = parse_telemetry_link(match)
        print(f"found link: {link[0:80]}.....")

        telemetry = get_telemetry_data(link)

        parse_parachute_landings(telemetry)

        break


if __name__ == '__main__':
    main()