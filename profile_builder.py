import subprocess
import random
import time
import yaml
import logging
import re
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style, init

# Initialize colorama for colored output
init(autoreset=True)

# Available colors for device aliases (excluding error-related colors like red)
COLORS = [Fore.CYAN, Fore.GREEN, Fore.YELLOW, Fore.MAGENTA, Fore.BLUE]

# Load the configuration
def load_config(config_file="config.yaml"):
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)

# Load search queries from searchlist.txt
def load_search_queries(search_file="searchlist.txt"):
    try:
        with open(search_file, 'r') as file:
            queries = [line.strip() for line in file.readlines() if line.strip()]
        logging.info(f"Loaded {len(queries)} search queries from {search_file}")
        return queries
    except FileNotFoundError:
        logging.error(f"Search file {search_file} not found!")
        return []

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

def adb_command(device_id, command, device_status, alias):
    """Executes ADB command on the specified device and retries if connection is closed."""
    if not device_status['connected']:
        return False  # Skip command if device is marked as disconnected
    
    try:
        cmd = f"adb -s {device_id} {command}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            if "not found" in result.stderr or "device offline" in result.stderr:
                # Mark device as disconnected and log the error only once
                if device_status['connected']:
                    logging.error(f"{alias} - Device {device_id} is not available: {result.stderr.strip()}")
                    device_status['connected'] = False
            return False
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"{alias} - Error running command {command} on {device_id}: {e}")
        return False

def adb_connect_via_ip(ip_address, usb_device_id=None):
    """Attempts to connect the device via ADB over IP."""
    try:
        if usb_device_id:
            logging.info(f"Setting ADB to TCP/IP mode for device {usb_device_id}")
            result = subprocess.run(f"adb -s {usb_device_id} tcpip 5555", shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                logging.error(f"Failed to set ADB to TCP/IP mode for device {usb_device_id}: {result.stderr}")
                return False
        
        logging.info(f"Connecting to device at {ip_address}")
        result = subprocess.run(f"adb connect {ip_address}:5555", shell=True, capture_output=True, text=True)
        if "already connected" in result.stdout or result.returncode == 0:
            logging.info(f"Successfully connected to device {ip_address} via ADB over IP.")
            return True
        else:
            logging.error(f"Failed to connect to device {ip_address}: {result.stderr}")
            return False
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to connect to device {ip_address} over IP: {e}")
        return False

def is_ip_address(device_id):
    """Checks if the given device_id is an IP address."""
    return re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", device_id)

def test_adb_connection(device_id, device_status):
    """Tests if the device is connected and ADB is working."""
    if is_ip_address(device_id):
        return adb_connect_via_ip(device_id)
    else:
        return adb_command(device_id, "devices", device_status, device_status['alias'])

def random_delay(min_time, max_time):
    """Waits for a random amount of time between min_time and max_time."""
    delay = random.uniform(min_time, max_time)
    time.sleep(delay)

def perform_tasks(device_id, device, alias_color, search_queries, config, device_status):
    """Performs tasks on a single device."""    
    alias = device['alias']
    
    if not device_status['connected']:
        logging.error(f"{alias_color}{alias} - Device {device_id} is not connected. Skipping tasks.")
        return

    logging.info(f"{alias_color}{alias} - Starting tasks on {device_id}{Style.RESET_ALL}")

    task_list = []
    for task in config['tasks']:
        if task.get('wikipedia_search'):
            task_list.append('wikipedia_search')
        if task.get('google_search'):
            task_list.append('google_search')

    random.shuffle(search_queries)  # Shuffle the search queries for randomness

    for query in search_queries:  # Iterate through the shuffled queries
        if not device_status['connected']:
            break  # Stop performing tasks if the device is disconnected
        task = random.choice(task_list)  # Randomly select a task
        if task == 'wikipedia_search':
            logging.info(f"{alias_color}{alias} - Performing a Wikipedia search for '{query}'{Style.RESET_ALL}")
            perform_wikipedia_search(device_id, query, device_status, config)
        elif task == 'google_search':
            logging.info(f"{alias_color}{alias} - Performing a Google search for '{query}'{Style.RESET_ALL}")
            perform_google_search(device_id, query, device_status, config)
        
        random_delay(config['timing_parameters']['min_delay_between_tasks'], 
                     config['timing_parameters']['max_delay_between_tasks'])

def perform_google_search(device_id, query, device_status, config):
    """Performs a Google search."""
    open_google(device_id, device_status, config)
    random_delay(2, 5)  # Added delay before typing
    if not device_status['connected']:
        return
    for _ in range(5):
        adb_command(device_id, "shell input keyevent 61", device_status, device_status['alias'])
        random_delay(0.5, 1)
    perform_search(device_id, query, device_status)
    random_delay(config['scroll_delay']['after_search'], config['scroll_delay']['after_search'] + 2)  # Delay before scrolling
    scroll_and_read(device_id, device_status)  # Scroll and read after search

def open_google(device_id, device_status, config):
    """Opens Google on the specified device.""" 
    logging.info(f"Opening Google on {device_id}")
    adb_command(device_id, "shell am start -a android.intent.action.VIEW -d 'https://www.google.com'", device_status, device_status['alias'])
    random_delay(config['loading_delays']['google'], config['loading_delays']['google'] + 2)  # Allow some time for the page to load

def perform_wikipedia_search(device_id, query, device_status, config):
    """Performs a Wikipedia search."""
    open_wikipedia(device_id, device_status, config)
    perform_search(device_id, query, device_status)
    random_delay(config['scroll_delay']['after_search'], config['scroll_delay']['after_search'] + 2)  # Delay before scrolling
    scroll_and_read(device_id, device_status)  # Scroll and read after search

def open_wikipedia(device_id, device_status, config):
    """Opens Wikipedia on the specified device."""
    logging.info(f"Opening Wikipedia on {device_id}")
    adb_command(device_id, "shell am start -a android.intent.action.VIEW -d 'https://www.wikipedia.org'", device_status, device_status['alias'])
    random_delay(config['loading_delays']['wikipedia'], config['loading_delays']['wikipedia'] + 3)  # Allow some time for the page to load

def perform_search(device_id, search_query, device_status):
    """Performs a search on the current platform."""
    logging.info(f"Searching for '{search_query}' on {device_id}")
    for word in search_query.split():
        adb_command(device_id, f"shell input text '{word}'", device_status, device_status['alias'])
        adb_command(device_id, "shell input text ' '", device_status, device_status['alias'])
    adb_command(device_id, "shell input keyevent 66", device_status, device_status['alias'])
    random_delay(5, 10)

def scroll_and_read(device_id, device_status):
    """Simulates scrolling and reading on a webpage."""
    logging.info(f"Scrolling and reading on {device_id}")
    for scroll in range(3):
        adb_command(device_id, "shell input swipe 500 1500 500 1000", device_status, device_status['alias'])
        read_time = random.uniform(15, 25)
        logging.info(f"Reading for {read_time:.2f} seconds after scroll {scroll + 1}/3")
        time.sleep(read_time)

def run_for_device(device, alias_color, search_queries, config):
    """Runs tasks for a single device."""
    device_id = device['id']
    device_status = {'connected': True, 'alias': device['alias']}
    
    if not test_adb_connection(device_id, device_status):
        logging.error(f"{alias_color}{device['alias']} - Device {device_id} is not connected or ADB is not working.")
        return
    
    min_loops = config['loop_settings']['min_loops']
    max_loops = config['loop_settings']['max_loops']

    if min_loops == 0 and max_loops == 0:
        while device_status['connected']:
            perform_tasks(device_id, device, alias_color, search_queries, config, device_status)
            random_delay(10, 20)
    else:
        loops = random.randint(min_loops, max_loops)
        logging.info(f"{alias_color}{device['alias']} - Running {loops} loops on device {device_id}")
        for i in range(loops):
            if not device_status['connected']:
                break  # Stop the loop if the device is disconnected
            logging.info(f"{alias_color}{device['alias']} - Starting loop {i+1}/{loops}")
            perform_tasks(device_id, device, alias_color, search_queries, config, device_status)
            logging.info(f"{alias_color}{device['alias']} - Completed loop {i+1}/{loops}")
            random_delay(10, 20)

def main():
    logging.info("Welcome to Rare's Android Profile Builder! Enjoy the process.")
    logging.info("Loading configuration...")
    config = load_config()  # Load config
    search_queries = load_search_queries()  # Load search queries from file
    devices = config['devices']

    # Initialize color_map for device aliases
    color_map = {}
    for i, device in enumerate(devices):
        color_map[device['alias']] = COLORS[i % len(COLORS)]  # Assign colors to each device alias

    # Log device configuration
    for device in devices:
        logging.info(f"Configured device: {device['alias']} with ID: {device['id']}")

    # Run each device in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor() as executor:
        for device in devices:
            alias_color = color_map[device['alias']]
            logging.info(f"Starting tasks for device: {alias_color}{device['alias']}{Style.RESET_ALL}")
            executor.submit(run_for_device, device, alias_color, search_queries, config)

    logging.info("All tasks submitted for execution.")

if __name__ == "__main__":
    logging.info("Script starting...")
    main()
