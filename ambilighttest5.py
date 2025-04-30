import tkinter as tk
from tkinter import ttk
import threading
import serial
import time
from PIL import ImageGrab
import numpy as np

# --- Settings ---
region_start = 'bottom_left'   # bottom_left, top_left, top_right, bottom_right
rotation = 'clockwise'         # clockwise or anti_clockwise

led_on_right = 9
led_on_left = 10
led_on_top = 17
led_on_bottom = 0

width_of_border = 5            # Border width in percentage
resize_factor = 10             # Resize factor for faster processing (in percentage)

# --- Detect Screen Size Automatically ---
screen_width, screen_height = ImageGrab.grab().size
resize_width = (screen_width * resize_factor) / 100
resize_height = (screen_height * resize_factor) / 100

# --- Calculate Region Sizes ---
region_width_lr = (resize_width * width_of_border) / 100
region_height_left = resize_height / led_on_left if led_on_left else 0
region_height_right = resize_height / led_on_right if led_on_right else 0
region_height_tb = (resize_height * width_of_border) / 100
region_width_top = resize_width / led_on_top if led_on_top else 0
region_width_bottom = resize_width / led_on_bottom if led_on_bottom else 0

negative_gap_lr = resize_width - region_width_lr
negative_gap_tb = resize_height - region_height_tb

# --- Generate Regions ---
regions_left = [(0, i * region_height_left, region_width_lr, (i + 1) * region_height_left) for i in range(led_on_left)]
regions_right = [(negative_gap_lr, i * region_height_right, negative_gap_lr + region_width_lr, (i + 1) * region_height_right) for i in range(led_on_right)]
regions_top = [(i * region_width_top, 0, (i + 1) * region_width_top, region_height_tb) for i in range(led_on_top)]
regions_bottom = [(i * region_width_bottom, negative_gap_tb, (i + 1) * region_width_bottom, negative_gap_tb + region_height_tb) for i in range(led_on_bottom)]

def generate_regions(rotation, region_start):
    global regions
    regions = []

    left = regions_left.copy()
    right = regions_right.copy()
    top = regions_top.copy()
    bottom = regions_bottom.copy()

    if rotation == 'clockwise':
        if region_start == 'bottom_left':
            left.reverse()
            bottom.reverse()
            regions = left + top + right + bottom
        elif region_start == 'bottom_right':
            bottom.reverse()
            left.reverse()
            regions = bottom + left + top + right
        elif region_start == 'top_left':
            left.reverse()
            bottom.reverse()
            regions = top + right + bottom + left
        elif region_start == 'top_right':
            left.reverse()
            bottom.reverse()
            regions = right + bottom + left + top

    elif rotation == 'anti_clockwise':
        right.reverse()
        top.reverse()
        if region_start == 'bottom_left':
            regions = bottom + right + top + left
        elif region_start == 'bottom_right':
            regions = right + top + left + bottom
        elif region_start == 'top_left':
            regions = left + bottom + right + top
        elif region_start == 'top_right':
            regions = top + left + bottom + right

# Generate regions
generate_regions(rotation, region_start)

# --- Globals ---
ser = None
running = False

# --- Functions ---
def capture_screen():
    return np.array(ImageGrab.grab().resize((int(resize_width), int(resize_height))))

def get_avg_color(img_np, region, brightness):
    x1, y1, x2, y2 = map(int, region)
    cropped = img_np[y1:y2, x1:x2]
    avg = cropped.mean(axis=(0, 1))
    return tuple(int(c * brightness) for c in avg[:3])

def send_colors(colors):
    if ser and ser.is_open:
        for r, g, b in colors:
            ser.write(bytes([r, g, b]))

def ambilight_loop(brightness_slider):
    global running
    while running:
        try:
            img_np = capture_screen()
            brightness = brightness_slider.get() / 100.0
            colors = [get_avg_color(img_np, reg, brightness) for reg in regions]
            send_colors(colors)
            time.sleep(0.03)
        except Exception as e:
            print(f"Error: {e}")
            break

def start_ambilight(com_entry, brightness_slider, start_button):
    global ser, running
    if not running:
        try:
            ser = serial.Serial(com_entry.get(), 115200)
            time.sleep(2)
            running = True
            threading.Thread(target=ambilight_loop, args=(brightness_slider,), daemon=True).start()
            start_button.config(text="Stop")
        except Exception as e:
            print(f"Failed to open serial port: {e}")
    else:
        running = False
        if ser:
            ser.close()
        start_button.config(text="Start")

def turn_off_leds(start_button):
    global running
    running = False
    time.sleep(0.05)  # Small delay to ensure loop ends
    if ser and ser.is_open:
        for _ in range(len(regions)):
            ser.write(bytes([0, 0, 0]))
    start_button.config(text="Start")


def build_gui():
    root = tk.Tk()
    root.title("Ambilight Controller")

    tk.Label(root, text="COM Port (e.g. COM3):").pack()
    com_entry = tk.Entry(root)
    com_entry.insert(0, "COM7")
    com_entry.pack()

    tk.Label(root, text="Brightness (%)").pack()
    brightness_slider = ttk.Scale(root, from_=0, to=100, orient='horizontal')
    brightness_slider.set(80)
    brightness_slider.pack()

    start_button = tk.Button(root, text="Start", width=20,
                             command=lambda: start_ambilight(com_entry, brightness_slider, start_button))
    start_button.pack(pady=10)

    tk.Button(root, text="Turn Off LEDs", command=lambda: turn_off_leds(start_button)).pack()


    root.mainloop()

# --- Start the GUI ---
if __name__ == "__main__":
    build_gui()
