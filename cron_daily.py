from whoop_data import WhoopClient, get_heart_rate_data, get_sleep_data
import logging
import json
import os
from datetime import datetime, timedelta
import uuid
from dotenv import load_dotenv

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
            # Generate a unique filename for each sleep event
            sleep_id = sleep_event.get('id', uuid.uuid4().hex[:8])
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
    
    try:
        # Initialize the Whoop client
        client = WhoopClient(username=email, password=password)
        logger.info("Whoop client initialized.")
        
        # Fetch and save heart rate data
        hr_count = fetch_and_save_hr_data(client, yesterday)
        logger.info(f"Processed {hr_count} heart rate data points.")
        
        # Fetch and save sleep data
        sleep_count = fetch_and_save_sleep_data(client, yesterday)
        logger.info(f"Processed {sleep_count} sleep events.")
        
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()