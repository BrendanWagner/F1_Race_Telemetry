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
    # print(bulk_data)
    for driver in bulk_data.keys():
        data = bulk_data[driver]
        time = data[:, 0]
        x = data[:, 1]
        y = data[:, 2]
        z = data[:, 3]

        # Create figure object.
        Max = script_dir / "db" / race / "VER.npy"
        if driver == Max:
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.set_xlim(x.min(), x.max())
            ax.set_ylim(y.min(), y.max())
            ax.legend()
            data = data[::5]
            ###############################
            # data = data[:1000]
            longest_race = len(data)
            line, = ax.plot([], [], color='red', lw=1.5, alpha=0.6)
            leader_dot, = ax.plot([], [], color='red', marker='o', markersize=8, markeredgecolor='white')
            ###############################
            # line, = ax.plot([], [])
            def update(frame):
                # Update the line with data up to current frame
                line_length = 5
                start = max(0, frame - line_length)
                line.set_data(data[start:frame, 1], data[start:frame, 2])
                if frame > 0:
                    leader_dot.set_data([data[frame-1, 1]], [data[frame-1, 2]])
                return line, leader_dot
            ###############################
            ani = FuncAnimation(fig, update, frames=longest_race, interval=1000, blit=True)
            print("Encoding video... this might take a minute.")
            writer = FFMpegWriter(fps=30)
            ani.save(f"{race}_replay.mp4", writer=writer)
            plt.show()


if __name__ == "__main__":
    main_test()