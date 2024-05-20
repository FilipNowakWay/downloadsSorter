import os
import shutil
import pyinotify
import json
import logging

# Set up logging
logging.basicConfig(filename='file_sorter.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_configuration(config_file):
    with open(config_file, 'r') as file:
        return json.load(file)

class EventHandler(pyinotify.ProcessEvent):
    def my_init(self, folder_path, extensions_to_categories):
        self.folder_path = folder_path
        self.extensions_to_categories = extensions_to_categories

    def process_IN_CREATE(self, event):
        file = os.path.join(event.path, event.name)
        file_extension = os.path.splitext(event.name)[1][1:].lower()
        category = self.extensions_to_categories.get(file_extension, None)

        if category:
            destination_folder = os.path.join(self.folder_path, category)
            if not os.path.exists(destination_folder):
                os.makedirs(destination_folder)
            destination_file = os.path.join(destination_folder, event.name)
            shutil.move(file, destination_file)
            logging.info(f"Moved file '{event.name}' to folder '{category}'")

# Replace 'your_folder_path_here' with the actual folder path you want to check
folder_path = '/home/evilmonarch/Downloads/'
config_file = 'config.json'

# Load configuration
config = load_configuration(config_file)
extensions_to_categories = config['extensions_to_categories']

# Set up inotify watcher
wm = pyinotify.WatchManager()
handler = EventHandler(folder_path=folder_path, extensions_to_categories=extensions_to_categories)
notifier = pyinotify.Notifier(wm, handler)

# Watch for file creation events in the specified folder
wm.add_watch(folder_path, pyinotify.IN_CREATE)

# Start the notifier
notifier.loop()
