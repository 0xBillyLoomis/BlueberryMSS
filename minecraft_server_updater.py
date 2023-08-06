import requests
import zipfile
import os
import toml
import subprocess
from shutil import copy2, copytree, rmtree
import time

# Constants
BASE_URL = 'https://pack.funasfuck.com/'
PACK_TOML_URL = os.path.join(BASE_URL, 'pack.toml')
ZIP_URL = os.path.join(BASE_URL, 'FASF-Server.zip')
VERSION_FILE = 'previous_version.txt'
DESTINATION_FOLDER = os.path.dirname(os.path.abspath(__file__))  # Same directory as the script
SCREEN_NAME = 'minecraft_server'  # Name of the screen session

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

        # Download and extract the ZIP file
        response = requests.get(ZIP_URL)
        zip_path = 'FASF-Server.zip'
        with open(zip_path, 'wb') as file:
            file.write(response.content)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall('temp_folder')

        # Remove old mods folder and replace with the new one
        rmtree(os.path.join(DESTINATION_FOLDER, 'mods'), ignore_errors=True)
        copytree(os.path.join('temp_folder', 'mods'), os.path.join(DESTINATION_FOLDER, 'mods'))

        # For config and defaultconfigs, only copy files if they don't already exist in the destination
        for folder_name in ['config', 'defaultconfigs']:
            src_folder = os.path.join('temp_folder', folder_name)
            dest_folder = os.path.join(DESTINATION_FOLDER, folder_name)
            for root, dirs, files in os.walk(src_folder):
                for file_name in files:
                    src_file_path = os.path.join(root, file_name)
                    dest_file_path = os.path.join(dest_folder, os.path.relpath(src_file_path, src_folder))
                    if not os.path.exists(dest_file_path):
                        os.makedirs(os.path.dirname(dest_file_path), exist_ok=True)
                        copy2(src_file_path, dest_file_path, follow_symlinks=True)

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
