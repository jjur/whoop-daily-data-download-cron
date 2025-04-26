from whoop_data import WhoopClient, get_heart_rate_data, get_sleep_data
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def fetch_hr_data(email, password):
    try:
        # Initialize the Whoop client
        client = WhoopClient(username=email, password=password)
        logger.info("Whoop client initialized.")
   

        # Fetch today's HR data
        hr_data = get_heart_rate_data(client, start_date="2025-04-24", end_date="2025-04-24", step=600)
        logger.info("Fetched HR data for today.")

        # Print the HR data
        for entry in hr_data:
            logger.info(f"Timestamp: {entry['timestamp']}, HR: {entry['heart_rate']}")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
    
def fetch_sleep_data(email, password, start_date=None, end_date=None):
    try:
        # Initialize the Whoop client
        client = WhoopClient(username=email, password=password)
        logger.info("Whoop client initialized for sleep data.")
        
        # Fetch sleep data
        if start_date and end_date:
            sleep_data = get_sleep_data(client=client, start_date=start_date, end_date=end_date)
            logger.info(f"Fetched sleep data from {start_date} to {end_date}.")
        else:
            sleep_data = get_sleep_data(client=client)
            logger.info("Fetched sleep data for the last 7 days (default).")
        
        return sleep_data
            
    except Exception as e:
        logger.error(f"An error occurred while fetching sleep data: {e}")
        return []

if __name__ == "__main__":
    # Replace with your Whoop credentials
    email = "domacenoviny@gmail.com"
    password = "Jurkovasek1@"

    # Fetch heart rate data
    fetch_hr_data(email, password)
    
    # Fetch sleep data for the last 7 days (default)
    # fetch_sleep_data(email, password)
    
    # Fetch sleep data for a specific date range
    fetch_sleep_data(email, password, start_date="2025-04-20", end_date="2025-04-26")
