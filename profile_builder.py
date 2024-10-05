import subprocess
import random
import time
import yaml
import logging
from datetime import datetime

# Load the configuration
def load_config(config_file="config.yaml"):
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)

# Set up logging
logging.basicConfig(
    filename='adb_profile_builder.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Log to both the file and console for immediate feedback
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

def adb_command(device_id, command):
    """Executes ADB command on the specified device."""
    try:
        cmd = f"adb -s {device_id} {command}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            logging.error(f"ADB command failed: {command}, error: {result.stderr}")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running command {command} on {device_id}: {e}")
        return False

def random_delay(min_time, max_time):
    """Waits for a random amount of time between min_time and max_time."""
    delay = random.uniform(min_time, max_time)
    time.sleep(delay)

def open_wikipedia(device_id):
    """Opens Wikipedia on the specified device."""
    logging.info(f"Opening Wikipedia...")
    adb_command(device_id, "shell am start -a android.intent.action.VIEW -d 'https://www.wikipedia.org'")
    random_delay(5, 8)

def open_google(device_id):
    """Opens Google on the specified device."""
    logging.info(f"Opening Google...")
    adb_command(device_id, "shell am start -a android.intent.action.VIEW -d 'https://www.google.com'")
    random_delay(5, 7)  # Allow time for Google to load

def perform_search(device_id, search_query):
    """Performs a search on the current search platform (Wikipedia or Google)."""
    logging.info(f"Searching for: {search_query}")
    
    # Simulate typing the search query with spaces
    for word in search_query.split():
        adb_command(device_id, f"shell input text '{word}'")
        adb_command(device_id, "shell input text ' '")  # Add a real space between words

    # Press "Enter" to submit the search query
    adb_command(device_id, "shell input keyevent 66")  # Keyevent 66 = Enter key
    random_delay(5, 10)

def scroll_and_read(device_id):
    """Simulates slower scrolling and pauses to read for 15-25 seconds."""
    logging.info(f"Scrolling through content and simulating reading.")
    
    for scroll in range(3):  # Perform 3 slow scrolls
        adb_command(device_id, "shell input swipe 500 1500 500 1000")  # Simulate scroll
        read_time = random.uniform(15, 25)  # Pause to simulate reading (15-25 seconds)
        logging.info(f"Simulated reading for {read_time:.2f} seconds after scroll {scroll + 1}/3")
        time.sleep(read_time)

def perform_google_search(device_id, search_queries):
    """Performs a random search on Google."""
    open_google(device_id)  # Open Google first
    random_delay(5, 7)  # Allow Google to fully load

    # Press Tab 5 times to focus on the search bar
    for _ in range(5):
        adb_command(device_id, "shell input keyevent 61")  # Keyevent 61 = Tab key
        random_delay(0.5, 1)  # Small delay between tabs to simulate real navigation

    query = random.choice(search_queries)  # Randomly select a search query
    perform_search(device_id, query)  # Perform the search on Google
    scroll_and_read(device_id)  # Simulate scrolling and reading

def perform_wikipedia_search(device_id, search_queries):
    """Performs a random search on Wikipedia."""
    open_wikipedia(device_id)  # Open Wikipedia first
    
    query = random.choice(search_queries)  # Randomly select a search query
    perform_search(device_id, query)  # Perform the search on Wikipedia
    scroll_and_read(device_id)  # Simulate scrolling and reading

def perform_tasks(device_id, config):
    """Performs tasks on a single device."""
    search_queries = config['search_queries']  # List of search queries from config
    task_list = []

    # Check which search options are enabled (Google, Wikipedia, or both)
    for task in config['tasks']:
        if task.get('wikipedia_search'):
            task_list.append('wikipedia_search')
        if task.get('google_search'):
            task_list.append('google_search')

    logging.info(f"Performing tasks on device {device_id}")

    # Perform tasks in random order
    for _ in range(len(search_queries)):
        task = random.choice(task_list)  # Randomly select Google or Wikipedia
        if task == 'wikipedia_search':
            logging.info(f"Selected task: Wikipedia search")
            perform_wikipedia_search(device_id, search_queries)
        elif task == 'google_search':
            logging.info(f"Selected task: Google search")
            perform_google_search(device_id, search_queries)
        random_delay(config['timing_parameters']['min_delay_between_tasks'], 
                     config['timing_parameters']['max_delay_between_tasks'])

def test_adb_connection(device_id):
    """Tests if the device is connected and ADB is working."""
    return adb_command(device_id, "devices")

def main():
    logging.info("Welcome to Rare's Android Profile Builder! Enjoy the process.")
    logging.info("Loading configuration...")
    config = load_config()
    devices = config['devices']
    min_loops = config['loop_settings']['min_loops']
    max_loops = config['loop_settings']['max_loops']
    
    # Main loop for each device
    for device in devices:
        device_id = device['id']
        
        # Test if ADB connection is successful
        if not test_adb_connection(device_id):
            logging.error(f"Device {device_id} is not connected or ADB is not working.")
            continue  # Skip to the next device if ADB connection fails
        
        logging.info(f"Starting task loop on device: {device_id}")
        
        # Infinite loops if both min_loops and max_loops are set to 0
        if min_loops == 0 and max_loops == 0:
            logging.info(f"Running in infinite loop mode...")
            while True:
                perform_tasks(device_id, config)
                random_delay(10, 20)  # Break between loops to simulate human-like behavior
        else:
            loops = random.randint(min_loops, max_loops)
            logging.info(f"Running {loops} loops on device {device_id}")
            
            for i in range(loops):
                logging.info(f"Starting loop {i+1}/{loops}")
                perform_tasks(device_id, config)
                logging.info(f"Completed loop {i+1}/{loops}")
                random_delay(10, 20)  # Break between loops to simulate human-like behavior

        logging.info(f"Completed all tasks on device {device_id}")

if __name__ == "__main__":
    logging.info("Script starting...")
    main()
