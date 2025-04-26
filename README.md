# Whoop Daily Data Download

A Python application that automatically downloads and stores daily heart rate and sleep data from Whoop devices.

## Features

- Daily automatic download of heart rate data (sampled every 6 steps)
- Daily automatic download of sleep events
- Data stored as JSON files organized by date
- Logging system for tracking operations

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory with your Whoop credentials:
   ```
   WHOOP_EMAIL=your-email@example.com
   WHOOP_PASSWORD=your-password
   ```

## Usage

### One-time manual download

Run the cron.py script directly:

```
python cron.py
```

### Automated daily downloads

Set up the cron_daily.py script to run automatically using your system's scheduler:

```
python cron_daily.py
```

This will fetch data from the previous day and store it in the following structure:
- Heart rate data: `data/heartRate/heartRate_YYYY-MM-DD.json`
- Sleep data: `data/sleep/sleep_YYYY-MM-DD_[id].json`

## License

See the [LICENSE](LICENSE) file for details.