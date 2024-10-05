
# Rare's Android Profile Builder

Welcome to **Rare's Android Profile Builder**! This project automates Android devices using ADB (Android Debug Bridge) to build realistic browsing profiles by performing searches on both Google and Wikipedia. The main goal is to simulate genuine, human-like behavior on a device, making it seem like it is being used for regular browsing, thereby reducing the chance of being flagged as a bot.

## Features
- Random searches on Google and Wikipedia.
- Simulated scrolling and reading of articles.
- Configurable to run indefinitely or for a set number of loops.
- Randomized delays between actions to mimic human behavior.

## Why I Created This

I built this project because I wanted a way to make my Android devices appear active, performing various tasks like web browsing, without requiring manual input. This helps in building realistic browsing profiles for use cases where automation is needed to simulate actual device activity.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/veryraregaming/Rare-s-Android-Profile-Builder.git
   ```

2. Install the required Python packages (using a virtual environment is recommended):
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure that ADB is installed and that your device is connected. You can verify your device's connection with:
   ```bash
   adb devices
   ```

## Configuration

The script uses a `config.yaml` file to define its behavior. Here’s an example configuration:

```yaml
devices:
  - id: "YOUR_DEVICE_ID"
    alias: "Pixel 6a"

tasks:
  - wikipedia_search: true
  - google_search: true

timing_parameters:
  min_delay_between_tasks: 3
  max_delay_between_tasks: 10

search_queries:
  - "Quantum mechanics"
  - "Artificial intelligence"
  - "Machine learning"

loop_settings:
  min_loops: 5
  max_loops: 10
```

- **devices**: List of devices to connect via ADB.
- **tasks**: Whether to perform Google and/or Wikipedia searches.
- **timing_parameters**: Delay settings for tasks.
- **search_queries**: List of search terms to randomly pick from.
- **loop_settings**: Number of times to loop through tasks. Set both to `0` for infinite loops.

## Usage

1. Ensure that your Android device is connected via ADB:
   ```bash
   adb devices
   ```

2. Run the script:
   ```bash
   python profile_builder.py
   ```

3. The script will randomly choose between Google and Wikipedia searches, simulate scrolling, and pause to simulate reading.

## Future Plans

- Add more tasks beyond searching, such as interacting with apps.
- Improve task variety to simulate a broader range of device activities.
- Implement a GUI for easier configuration and control.

## Contributing

Feel free to fork this repository and submit pull requests! Suggestions and improvements are always welcome.

## License

This project is licensed under the MIT License.
