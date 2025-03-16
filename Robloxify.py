import os
from PIL import Image
import base64
from flask import Flask, jsonify
from flask_cors import CORS
import logging
import clipboard
import platform
version = "v0.4(BETA)"
grid_size = 256
block_size = 0.1 * (256 / grid_size)

# ASCII Art
fire_art = [
    "    ____        __    __           _ ____     ",
    "   / __ \\____  / /_  / /___  _  __(_) __/_  __",
    "  / /_/ / __ \\/ __ \\/ / __ \\| |/_/ / /_/ / / /",
    " / _, _/ /_/ / /_/ / / /_/ />  </ / __/ /_/ / ",
    "/_/ |_|\\____/_.___/_/\\____/_/|_/_/_/  \\__, /  ",
    "                                     /____/   "
]

# Function to generate 24-bit RGB ANSI escape codes
def rgb(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"

# Define starting (red) and ending (yellow) RGB values
start_color = (255, 0, 0)    # Red
end_color = (255, 255, 0)    # Yellow

# Function to interpolate between two colors
def interpolate_color(start, end, factor):
    return tuple(int(start[i] + (end[i] - start[i]) * factor) for i in range(3))

# Total number of lines
total_lines = len(fire_art)

# Generate and print each line with interpolated colors
for i, line in enumerate(fire_art):
    factor = i / (total_lines - 1)  # Compute factor for interpolation (0 to 1)
    color = interpolate_color(start_color, end_color, factor)  # Interpolated color
    print(rgb(*color) + line)

# Reset terminal color
print("\033[0m")

# ANSI escape codes for styling
RESET = "\033[0m"       # Reset all styles
BOLD = "\033[1m"        # Bold text
LIGHT = "\033[2m"       # Light (faint) text
RED = "\033[91m"        # Bright red text

# Print the developer's name in regular style
print(f"{LIGHT}By devsoniexpert{RESET}")

# Print the thank you message in bold
print(f"Thank You for using robloxify", f"{LIGHT}{version}{RESET}")

# Optional: Custom logger class to suppress certain levels of logs
class CustomLogger(logging.Logger):
    def info(self, msg, *args, **kwargs):
        pass  # Suppress info messages
    def warning(self, msg, *args, **kwargs):
        print(f"{LIGHT}Warning: {msg}{RESET}")  # Print warnings in light text
    def error(self, msg, *args, **kwargs):
        print(f"{RED}Error: {msg}{RESET}")  # Print errors in red text

# Replace the default logger with the custom logger
logging.setLoggerClass(CustomLogger)
logger = logging.getLogger(__name__)

# Folder where the script is located
script_dir = os.path.dirname(os.path.realpath(__file__))

# Allowed image extensions
allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']

# Get a list of image files in the folder
image_files = [f for f in os.listdir(script_dir) if os.path.splitext(f)[1].lower() in allowed_extensions]

# Check if there's more than one image
if len(image_files) < 1:
    logger.error("More than 1 image found in the folder or no image found. Please keep only 1 image.")
    exit()

# Path to the image
image_path = os.path.join(script_dir, image_files[0])

# Print the image name in LIGHT text
print(f"{LIGHT}Processing image: {image_files[0]}{RESET}")

# Open the image
try:
    with Image.open(image_path) as img:
        # Convert image to PNG if it's not in PNG format
        if img.format != 'PNG':
            png_image_path = image_path.replace(os.path.splitext(image_path)[1], '.png')
            img.save(png_image_path, 'PNG')
            image_path = png_image_path
            print(f"{LIGHT}Image converted to PNG format.{RESET}")
        else:
            print(f"{LIGHT}Image is already in PNG format.{RESET}")

        # Resize image if necessary
        if img.width > grid_size or img.height > grid_size:
            img = img.resize((grid_size, grid_size))

        # Convert the image to RGB
        img = img.convert('RGB')

        # Collect the pixel data
        pixel_data = []
        for y in range(img.height):
            for x in range(img.width):
                r, g, b = img.getpixel((x, y))
                pixel_data.append(r)
                pixel_data.append(g)
                pixel_data.append(b)

        # Convert pixel data to bytes and then encode it in base64
        pixel_bytes = bytes(pixel_data)
        base64_data = base64.b64encode(pixel_bytes).decode('utf-8')

except Exception as e:
    logger.error(f"Error processing the image: {e}")

# Flask setup
app = Flask(__name__)
CORS(app)

# Global variable to store base64 image data
image_data = base64_data

# Get local IP address
import socket

# Create a dummy connection to an external IP to get the actual local IP
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))  # Connect to a public IP (Google's DNS server)
local_ip = s.getsockname()[0]
s.close()

ip_parts = local_ip.split(".")
third_fourth = f"{ip_parts[2]}.{ip_parts[3]}"
encoded_ip = base64.b64encode(third_fourth.encode()).decode()

print(f"{LIGHT}Copy this{RESET} {BOLD}{encoded_ip}{RESET}{LIGHT} and paste it in the lua script{RESET}")
if platform.system() == "Windows":
    clipboard.copy(f"{encoded_ip}")
print(f"{LIGHT}Dont know where to get lua script? Get it at https://pastebin.com/raw/rnk1mBDt{RESET}")
# Function to serve image data on request
@app.route('/data', methods=['GET'])
def get_data():
    return jsonify({
        "data": image_data,
        "grid_size": grid_size,
        "block_size": block_size
    })
CORS(app, resources={r"/*": {"origins": "*"}})
# Start the Flask server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)