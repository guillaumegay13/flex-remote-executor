from ...client.flexApiClient import FlexApiClient
import os
import sys

def main():

    file_path = sys.argv[1]    # Path to the current file in IntelliJ

    baseUrl = os.environ.get('BASE_URL')
    username = os.environ.get('USERNAME')
    password = os.environ.get('PASSWORD')

    flexApiClient = FlexApiClient(baseUrl, username, password)

    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if 'lastJobId : ' in line:
                lastJobId = line.strip().split('lastJobId : ')[1]
    
    if not lastJobId:
        raise Exception("Last Job ID not found. Please create a new job first!")
    
    print(f"Updating job ID {lastJobId}...")
    flexApiClient.update_config(file_path, lastJobId, "job")

if __name__ == "__main__":
    main()