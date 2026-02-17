import os
import shutil
import numpy as np
from pathlib import Path
from data_handling import compile_driver_data
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
import imageio_ffmpeg

plt.rcParams['animation.ffmpeg_path'] = imageio_ffmpeg.get_ffmpeg_exe()

def main_test(race="Abu Dhabi Grand Prix"):
    downgrader = 1
    script_dir = Path(__file__).resolve().parent
    idk = script_dir / "db" / race
    bulk_data = {}
    longest_race = 0
    for driver_data in idk.glob("*.npy"):
        # Load the data
        bulk_data[driver_data] = np.load(driver_data)
        race_time = len(bulk_data[driver_data])
        if race_time > longest_race:
            longest_race = race_time

    longest_race //= downgrader

    fig, ax = plt.subplots(figsize=(10, 6))

    drivers_elements = {} # To store lines and dots for each driver
    max_frames = 0

    # 2. Pre-process and Create "Artists" for every driver
    for driver, raw_data in bulk_data.items():
        data = raw_data[::downgrader] # Downsample EDIT HERE LATER
        max_frames = max(max_frames, len(data)) // 10
        
        # Create the visual elements for THIS driver
        line, = ax.plot([], [], lw=.5, alpha=0.3, label=driver)
        dot, = ax.plot([], [], marker='o', markersize=4, markeredgecolor='white')
        
        # Store them so we can update them by name later
        drivers_elements[driver] = {
            'line': line,
            'dot': dot,
            'data': data
        }

    # Set limits based on the global min/max of your data
    # THESE ARE HARD CODED FOR NOW WHICH IS BAD
    # EDIT HERE
    global_x_min = -3000
    global_x_max = 6500
    global_y_min = -6000
    global_y_max = 12000
    #################################
    ax.set_xlim(global_x_min, global_x_max)
    ax.set_ylim(global_y_min, global_y_max)
    # ax.legend(loc='upper right', ncol=2) # Uncomment this later

    # 3. The Unified Update Function
    def update(frame):
        updated_artists = []
        for driver, elements in drivers_elements.items():
            data = elements['data']
            line = elements['line']
            dot = elements['dot']
            
            # Check if this driver still has data for this frame
            if frame < len(data):
                trail_size = 1
                start = max(0, frame - trail_size)
                
                line.set_data(data[start:frame, 1], data[start:frame, 2])
                dot.set_data([data[frame-1, 1]], [data[frame-1, 2]])
                
                updated_artists.extend([line, dot])
            
            else:
                line.set_data([], [])
                dot.set_data([], [])
                
                # We must include them here so the blitting manager 
                # knows to "erase" their previous positions
                updated_artists.extend([line, dot])
            driver = str(driver)
            driver = driver[driver.find(".npy")-3:-4]
            print(f"{frame} made for {driver}")
                
        return updated_artists
    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    # ax.set_xlim(x.min(), x.max())
    # ax.set_ylim(y.min(), y.max())
    # ax.legend()
    # for driver in bulk_data.keys():
    #     data = bulk_data[driver]
    #     time = data[:, 0]
    #     x = data[:, 1]
    #     y = data[:, 2]
    #     z = data[:, 3]

    #     data = data[::10]
    #     ###############################
    #     data = data[:500]
    #     line, = ax.plot([], [], color='red', lw=1.5, alpha=0.6)
    #     leader_dot, = ax.plot([], [], color='red', marker='o', markersize=8, markeredgecolor='white')
        ###############################
        # def update(frame):
        #     # Update the line with data up to current frame
        #     line_length = 5
        #     start = max(0, frame - line_length)
        #     line.set_data(data[start:frame, 1], data[start:frame, 2])
        #     if frame > 0:
        #         leader_dot.set_data([data[frame-1, 1]], [data[frame-1, 2]])
        #     return line, leader_dot
        ###############################
    ani = FuncAnimation(fig, update, frames=longest_race, interval=1000, blit=True)
    print("Encoding video... this might take a minute.")
    writer = FFMpegWriter(fps=60)
    ani.save(f"{race}_replay.mp4", writer=writer)
    plt.show()


if __name__ == "__main__":
    main_test()