import os
import shutil
import numpy as np
from pathlib import Path
from data_handling import compile_driver_data
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
import imageio_ffmpeg

plt.rcParams['animation.ffmpeg_path'] = imageio_ffmpeg.get_ffmpeg_exe()

def main_test(race="Abu Dhabi Grand Prix", downgrader=20, tail=2):
    script_dir = Path(__file__).resolve().parent
    idk = script_dir / "db" / race
    bulk_data = {}
    longest_race = 0 # In number of frames
    slowest_time = 0 # How long the race actually took
    global_x_min = 0
    global_x_max = 0
    global_y_min = 0
    global_y_max = 0
    for driver_data in idk.glob("*.npy"):
        # Load the data
        this_drivers_race_line = np.load(driver_data)
        bulk_data[driver_data] = this_drivers_race_line
        race_time = len(this_drivers_race_line) # To be clear this is frames, not time... Though I should extract the time
        time_stamps = this_drivers_race_line[:, 0]
        x = this_drivers_race_line[:, 1]
        y = this_drivers_race_line[:, 2]
        longest_race = max(longest_race, race_time)
        global_x_min = min(global_x_min, min(x))
        global_x_max = max(global_x_max, max(x))
        global_y_min = min(global_y_min, min(y))
        global_y_max = max(global_y_max, max(y))
    # I don't like that the cars touch the edge of the graph
    x_span = global_x_max - global_x_min
    y_span = global_y_max - global_y_min
    global_x_min -= x_span * 0.1
    global_x_max += x_span * 0.1
    global_y_min -= y_span * 0.1
    global_y_max += y_span * 0.1

    longest_race //= downgrader # To match the animation length to the number of datapoints
    longest_race += 10 # Apparently we need a little buffer at the end

    fig, ax = plt.subplots(figsize=(10, 6))

    drivers_elements = {} # To store lines and dots for each driver

    # Pre-process and Create "Artists" for every driver
    for driver, raw_data in bulk_data.items():
        # Downsample: this is actually a super important line for testing
        data = raw_data[::downgrader]
        # For labels
        driver_str = str(driver)
        driver_name = driver_str[driver_str.find(".npy")-3:-4]
        
        # Create the visual elements for THIS driver
        line, = ax.plot([], [], lw=.5, alpha=0.3, label="_nolegend_")
        dot, = ax.plot([], [], marker='o', markersize=4, markeredgecolor='white', label=driver_name)

        
        # Store them so we can update them by name later
        drivers_elements[driver] = {
            'line': line,
            'dot': dot,
            'data': data
        }

    ax.set_xlim(global_x_min, global_x_max)
    ax.set_ylim(global_y_min, global_y_max)

    # Update Function
    def update(frame):
        updated_artists = []
        for driver, elements in drivers_elements.items():
            data = elements['data']
            line = elements['line']
            dot = elements['dot']
            
            # Check whether the driver has finished the race by this frame
            if frame < len(data):
                trail_size = tail
                start = max(0, frame - trail_size)
                
                line.set_data(data[start:frame, 1], data[start:frame, 2])
                dot.set_data([data[frame-1, 1]], [data[frame-1, 2]])
                
                updated_artists.extend([line, dot])
            
            else: # Make the lines and dots disappear after they finish the race
                line.set_data([], [])
                dot.set_data([], [])
                updated_artists.extend([line, dot])
    
        print(f"{frame} out of {longest_race}")
                
        return updated_artists

    ani = FuncAnimation(fig, update, frames=longest_race, interval=1000, blit=True) # Need to fix the interval here
    print("Encoding video... this might take a minute.")
    writer = FFMpegWriter(fps=8) # Need to change the fps here
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.set_axis_off()
    ax.legend(loc='upper right', bbox_to_anchor=(1.1, 1)) # Comment this out when we get to our leaderboard thing running
    os.makedirs("race_replays", exist_ok=True)
    ani.save(f"race_replays/{race}_replay.mp4", writer=writer)
    # plt.show()

def make_all_animations():
    script_dir = Path(__file__).resolve().parent
    idk = script_dir / "db"
    for file in idk.glob("*Grand Prix*"):
        main_test(race=file.name, downgrader=200)



if __name__ == "__main__":
    # main_test(race="Qatar Grand Prix", downgrader=20, tail=0)
    make_all_animations()