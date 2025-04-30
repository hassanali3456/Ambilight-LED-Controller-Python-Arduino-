💡 Ambilight LED Controller (Python + Arduino)
This Python script creates an Ambilight effect for your monitor using an Arduino and WS2812B (or similar) RGB LEDs. It captures your screen, calculates the average color of defined regions around the borders, and sends color data to the Arduino in real-time to light up the LEDs.

📦 Features
Automatically detects screen dimensions.

Dynamically generates LED regions based on screen borders.

Supports clockwise or anti-clockwise LED arrangement.

Selectable starting corner for region ordering.

Adjustable brightness via GUI.

Real-time color capture with 30 FPS.

Simple Tkinter GUI for COM port input and control.

Safely turns off LEDs and stops loop with a button.

⚙️ Requirements
Python 3.x

Libraries:

bash
Copy
Edit
pip install pillow numpy pyserial
🖥️ How it works
Screen Capture: Captures a downscaled image of the full screen (using PIL.ImageGrab).

Region Division: Splits the screen edges into sections based on how many LEDs you have per side.

Color Averaging: Calculates the average RGB value of each region.

Serial Communication: Sends color data to Arduino over a COM port.

Arduino: Receives RGB values and controls LEDs accordingly.

🧠 Configuration
You can adjust these parameters at the top of the code:

python
Copy
Edit
region_start = 'bottom_left'   # Options: bottom_left, top_left, top_right, bottom_right
rotation = 'clockwise'         # Options: clockwise, anti_clockwise

led_on_right = 9
led_on_left = 10
led_on_top = 17
led_on_bottom = 0

width_of_border = 5  # Percentage of screen width/height used for each border region
🕹️ GUI
The GUI lets you:

Select COM port (e.g., COM3, COM4).

Adjust brightness (0–100%).

Start/Stop ambilight effect.

Instantly turn off all LEDs.

📁 File Structure
main.py – Main script (run this)

ArduinoSketch.ino – (optional) Arduino code to receive and set RGB values (not included here)

🔌 Arduino Setup
Each frame sends r, g, b bytes per LED. Your Arduino sketch should:

Receive serial bytes in sets of 3.

Use a library like FastLED to update LED colors.

✅ Todo / Improvements
Add support for multi-monitor setups.

Save/load configuration to file.

Add auto-reconnect if Arduino disconnects.

Support other LED types (APA102 etc).

