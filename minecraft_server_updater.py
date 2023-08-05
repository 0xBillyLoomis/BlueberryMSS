import requests
import zipfile
import os
import toml
import subprocess
from shutil import copy2, rmtree
import time

# Constants
BASE_URL = 'https://pack.funasfuck.com/'
PACK_TOML_URL = os.path.join(BASE_URL, 'pack.toml')
ZIP_URL = os.path.join(BASE_URL, 'FASF-Server.zip')
VERSION_FILE = 'previous_version.txt'
DESTINATION_FOLDER = os.path.dirname(os.path.abspath(__file__))  # Same directory as the script
SCREEN_NAME = 'minecraft_server'  # Name of the screen session

# Function to remove old versions of mod files
def remove_old_versions(new_file_name, destination_folder):
    mod_name = new_file_name.split('-')[0]  # Assuming the name is before the version
    for file_name in os.listdir(destination_folder):
        if file_name.startswith(mod_name) and file_name != new_file_name:
            os.remove(os.path.join(destination_folder, file_name))

# Function to start Minecraft server in a screen
def start_minecraft_server():
    subprocess.run(['screen', '-S', SCREEN_NAME, '-d', '-m', 'bash', 'run.sh'], cwd=DESTINATION_FOLDER)
    print("Minecraft server started in screen.")

# Function to send command to Minecraft server screen
def send_command_to_screen(command):
    subprocess.run(['screen', '-S', SCREEN_NAME, '-p', '0', '-X', 'stuff', f"{command}\n"], cwd=DESTINATION_FOLDER)

# Start Minecraft server
start_minecraft_server()

while True:
    # Read the pack.toml file from the given URL
    response = requests.get(PACK_TOML_URL)
    content = response.text

    # Parse the TOML content and extract the version
    parsed_toml = toml.loads(content)
    current_version = parsed_toml['version']

    # Read the previous version
    try:
        with open(VERSION_FILE, 'r') as file:
            previous_version = file.read().strip()
    except FileNotFoundError:
        previous_version = None

    # Compare the current version with the previous version
    if previous_version is None or tuple(map(int, current_version.split('.'))) > tuple(map(int, previous_version.split('.'))):
        print("New version detected. Preparing to update server files...")

        # Send save-all command and wait
        send_command_to_screen('save-all')
        time.sleep(60)  # Wait for save-all to complete, adjust as needed

        # Send stop command
        send_command_to_screen('stop')
        time.sleep(10)  # Wait for stop to complete, adjust as needed

        # Download the ZIP file
        response = requests.get(ZIP_URL)
        zip_path = 'FASF-Server.zip'
        with open(zip_path, 'wb') as file:
            file.write(response.content)

        # Extract the ZIP file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall('temp_folder')

        # Replace files and remove old versions
        for root, dirs, files in os.walk('temp_folder'):
            for file_name in files:
                temp_file_path = os.path.join(root, file_name)
                dest_file_path = os.path.join(DESTINATION_FOLDER, os.path.relpath(temp_file_path, 'temp_folder'))

                # Remove old versions of the mod file
                remove_old_versions(file_name, os.path.dirname(dest_file_path))

                # Copy new file
                os.makedirs(os.path.dirname(dest_file_path), exist_ok=True)
                copy2(temp_file_path, dest_file_path)

        # Remove the temporary folder and ZIP file
        rmtree('temp_folder')
        os.remove(zip_path)

        # Save the current version
        with open(VERSION_FILE, 'w') as file:
            file.write(current_version)

        print("Update completed.")

        # Start Minecraft server
        start_minecraft_server()

    else:
        print("No new version detected.")

    # Wait for 24 hours before checking again
    time.sleep(24 * 60 * 60)
