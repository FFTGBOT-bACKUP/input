import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Function to make requests to the API with retry mechanism
def make_request_with_retry(uid, password, nickname, retry_attempts=3):
    url = f"http://13.126.82.233:8000/api/{uid}/{password}/{nickname}"
    for attempt in range(retry_attempts):
        try:
            response = requests.get(url)
            response_data = response.json()
            status_code = response.status_code
            return response_data, status_code
        except requests.exceptions.JSONDecodeError:
            if attempt < retry_attempts - 1:
                print(f"JSONDecodeError encountered. Retrying in 1 seconds. Attempt {attempt + 1}/{retry_attempts}")
                time.sleep(1)
            else:
                raise

# Function to handle successful responses and save account_id
def handle_success(uid, password, nickname, account_id):
    with open("success.txt", "a", encoding="utf-8") as success_file:
        success_file.write(f"UID: {uid}, Password: {password}, Nickname: {nickname}, Account ID: {account_id}\n")

# Function to handle error responses
def handle_error(uid, password, nickname):
    with open("error.txt", "a", encoding="utf-8") as error_file:
        error_file.write(f"UID: {uid}, Password: {password}, Nickname: {nickname}\n")

# Function to process a single line of input
def process_line(idx, line):
    uid, password = line.strip().split(": ")
    uid = uid.strip('"')
    password = password.strip('",')
    nickname = f"Aꜱᴛᴜᴛᴇ{idx:06d}"
    try:
        response_data, status_code = make_request_with_retry(uid, password, nickname)
        account_id = response_data.get("account_id", "N/A")
        if status_code == 200 and "success" in response_data and response_data["success"]:
            handle_success(uid, password, nickname, account_id)
        else:
            print(f"Error status code: {status_code} for UID: {uid}, Password: {password}")
            handle_error(uid, password, nickname)
    except Exception as e:
        print(f"Error occurred for UID: {uid}, Password: {password}: {e}")
        handle_error(uid, password, nickname)

# Function to process the input file with concurrency
def process_input(input_file):
    starting_index = 250000  # Starting index for the nickname
    with open(input_file, "r") as file:
        lines = file.readlines()
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(process_line, idx, line) for idx, line in enumerate(lines, start=starting_index)]
        for future in as_completed(futures):
            future.result()  # Retrieve any exceptions that were raised

# Main function
def main():
    process_input("input.txt")

if __name__ == "__main__":
    main()
