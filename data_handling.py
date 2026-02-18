import requests
from pathlib import Path
import json
import numpy as np

# def repo_race_data_url(race, driver):
#     return f"https://api.github.com/repos/TracingInsights/2025/contents/{race}/Race/{driver}"

def compile_driver_data(race, driver):
    """
    Docstring for combine_data

    :param race: string
    :param driver: string

    returns 
    final: a Nx4 array. First column time, then x, y, z positions.
    """
    input_dir = Path("2025") / race / "Race" / driver
    race_data_json = {}

    # .glob("*.json") finds all JSON files in the folder
    for file_path in input_dir.glob("*.json"):
        # Handle laptimes specifically
        if file_path.name == "laptimes.json":
            with open(file_path, 'r') as f:
                raw_data = json.load(f)["time"]
                
            laptimes = [0] + [lap if lap != "None" else 0 for lap in raw_data]
            cumulative_lap_times = [sum(laptimes[:i]) for i in range(len(laptimes))]
            
        else:
            # Handling ill-formatted strings for sorting (adding leading zero)
            name = file_path.stem if file_path.stem.find("_") > 1 else "0" + file_path.stem
            
            with open(file_path, 'r') as f:
                race_data_json[name] = json.load(f)
    
    
    # Extract times and positions
    times = []
    x = []
    y = []
    z = []
    for lap in sorted(race_data_json.keys()):
        # Get times
        lap_number = int(lap[:lap.find("_")])
        this_lap = race_data_json[lap]["tel"]["time"] # List of timestamps for this lap
        offset = cumulative_lap_times[lap_number]
        if offset == "None":
            offset = this_lap[-1]
        else:
            new_lap = [j + offset for j in this_lap]

        times += new_lap

        # Get positions
        this_lap_x = race_data_json[lap]["tel"]["x"] # List of x positions for this lap
        this_lap_y = race_data_json[lap]["tel"]["y"] # List of y positions for this lap
        this_lap_z = race_data_json[lap]["tel"]["z"] # List of z positions for this lap
        x += this_lap_x
        y += this_lap_y
        z += this_lap_z
    
    # Prepare (positional) data for being returned
    x = np.array(x)
    y = np.array(y)
    z = np.array(z)
    final = np.column_stack((times, x, y, z))

    return final

if __name__ == "__main__":
    print("Max's 2025 Las Vegas Race")
    data = compile_driver_data("United States Grand Prix", "VER")
    print(data)