from whoop_data import WhoopClient, get_heart_rate_data, get_sleep_data
import logging
import json
import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Optional PyPushBullet import (won't fail if not installed)
try:
    from PyPushBullet.client import PushBullet
    PUSHBULLET_AVAILABLE = True
except ImportError:
    logging.warning("PyPushBullet not installed. Notifications will not be sent.")
    PUSHBULLET_AVAILABLE = False

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_yesterday_date():
    """Returns yesterday's date in YYYY-MM-DD format"""
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")

def fetch_and_save_hr_data(client, date):
    """Fetch heart rate data for a specific date and save it as JSON"""
    try:
        # Fetch heart rate data with step of 6
        hr_data = get_heart_rate_data(client, start_date=date, end_date=date, step=6)
        logger.info(f"Fetched HR data for {date}.")
        
        # Create filename with date
        filename = os.path.join("data", "heartRate", f"heartRate_{date}.json")
        
        # Save data to JSON file
        with open(filename, 'w') as file:
            json.dump(hr_data, file, indent=4)
        
        logger.info(f"Saved HR data to {filename}.")
        return len(hr_data)
    except Exception as e:
        logger.error(f"An error occurred while fetching heart rate data: {e}")
        return 0

def fetch_and_save_sleep_data(client, date):
    """Fetch sleep data for a specific date and save each sleep event as a separate JSON file"""
    try:
        # Fetch sleep data
        sleep_data = get_sleep_data(client=client, start_date=date, end_date=date)
        logger.info(f"Fetched sleep data for {date}.")
        
        sleep_count = 0
        
        # Save each sleep event as a separate JSON file
        for sleep_event in sleep_data:
            # Use the activity ID instead of generating a random UUID
            sleep_id = sleep_event.get('activity_id')
            if not sleep_id:
                logger.warning("Missing activity_id for sleep event, skipping.")
                continue

            start_time = sleep_event.get('start', date).split('T')[0]
            filename = os.path.join("data", "sleep", f"sleep_{start_time}_{sleep_id}.json")

            # Save data to JSON file
            with open(filename, 'w') as file:
                json.dump(sleep_event, file, indent=4)

            logger.info(f"Saved sleep event to {filename}.")
            sleep_count += 1
        
        return sleep_count
    except Exception as e:
        logger.error(f"An error occurred while fetching sleep data: {e}")
        return 0

def retry_with_backoff(func, retries, backoff_intervals, *args, **kwargs):
    """Retries a function with exponential backoff intervals."""
    for attempt in range(retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                wait_time = backoff_intervals[attempt]
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                logger.error("All retry attempts failed.")
                raise

def get_missing_dates():
    """Identify missing dates for the past 30 days based on heartRate data."""
    existing_dates = set()
    heart_rate_dir = os.path.join("data", "heartRate")

    # Collect existing dates from heartRate filenames
    for filename in os.listdir(heart_rate_dir):
        if filename.startswith("heartRate_") and filename.endswith(".json"):
            date_str = filename[len("heartRate_"):-len(".json")]
            existing_dates.add(date_str)

    # Generate the past 30 days
    missing_dates = []
    for i in range(1, 31):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        if date not in existing_dates:
            missing_dates.append(date)

    return missing_dates

def redownload_missing_data():
    """Redownload missing heart rate and sleep data for the past 30 days."""
    # Get credentials from environment variables
    email = os.getenv("WHOOP_EMAIL")
    password = os.getenv("WHOOP_PASSWORD")

    if not email or not password:
        logger.error("Credentials not found in .env file. Please set WHOOP_EMAIL and WHOOP_PASSWORD.")
        return

    # Initialize the Whoop client
    try:
        client = WhoopClient(username=email, password=password)
        logger.info("Whoop client initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize Whoop client: {e}")
        return

    # Get missing dates
    missing_dates = get_missing_dates()
    logger.info(f"Missing dates identified: {missing_dates}")

    for date in missing_dates:
        logger.info(f"Processing missing data for date: {date}")

        # Fetch and save heart rate data
        hr_count = fetch_and_save_hr_data(client, date)
        logger.info(f"Processed {hr_count} heart rate data points for {date}.")

        # Fetch and save sleep data
        sleep_count = fetch_and_save_sleep_data(client, date)
        logger.info(f"Processed {sleep_count} sleep events for {date}.")

def main():
    # Create directories if they don't exist
    os.makedirs(os.path.join("data", "heartRate"), exist_ok=True)
    os.makedirs(os.path.join("data", "sleep"), exist_ok=True)
    
    # Get credentials from environment variables
    email = os.getenv("WHOOP_EMAIL")
    password = os.getenv("WHOOP_PASSWORD")
    
    if not email or not password:
        logger.error("Credentials not found in .env file. Please set WHOOP_EMAIL and WHOOP_PASSWORD.")
        return
    
    # Get yesterday's date
    yesterday = get_yesterday_date()
    logger.info(f"Processing data for date: {yesterday}")
    
    def task():
        # Initialize the Whoop client
        client = WhoopClient(username=email, password=password)
        logger.info("Whoop client initialized.")
        
        # Fetch and save heart rate data
        hr_count = fetch_and_save_hr_data(client, yesterday)
        logger.info(f"Processed {hr_count} heart rate data points.")
        
        # Fetch and save sleep data
        sleep_count = fetch_and_save_sleep_data(client, yesterday)
        logger.info(f"Processed {sleep_count} sleep events.")
        
        # Send success notification if enabled
        if hr_count > 0 or sleep_count > 0:
            send_notification(True, f"Successfully downloaded {hr_count} HR points and {sleep_count} sleep events for {yesterday}")
        else:
            send_notification(False, f"No data downloaded for {yesterday}")
    
    # Retry logic with backoff intervals
    backoff_intervals = [30 * 60, 60 * 60, 2 * 60 * 60, 4 * 60 * 60, 8* 60 * 60]  # 30 minutes, 1 hour, 2 hours, 4 hours, 8 hours
    try:
        retry_with_backoff(task, retries=len(backoff_intervals), backoff_intervals=backoff_intervals)
    except Exception as e:
        send_notification(False, f"Failed to download Whoop data after retries: {str(e)}")

def send_notification(success, message):
    """Send a PyPushBullet notification if configured"""
    if not PUSHBULLET_AVAILABLE:
        return
    
    api_key = os.getenv("PUSHBULLET_API_KEY")
    if not api_key:
        return
    
    try:
        # Using PyPushBullet library instead of pushbullet.py
        pb = PushBullet(api_key)
        title = "Whoop Data Download: Success" if success else "Whoop Data Download: Failed"
        pb.send_notification(title, message)
        logger.info(f"Sent PyPushBullet notification: {title}")
    except Exception as e:
        logger.error(f"Failed to send PyPushBullet notification: {e}")

if __name__ == "__main__":
    main()
    redownload_missing_data()