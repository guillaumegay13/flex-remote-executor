from flexApiClient import FlexApiClient
import sys
import os

def main():

    file_path = sys.argv[1]    # Path to the current file in IntelliJ

    baseUrl = os.environ.get('BASE_URL')
    username = os.environ.get('USERNAME')
    password = os.environ.get('PASSWORD')

    flexApiClient = FlexApiClient(baseUrl, username, password)

    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if 'actionId : ' in line:
                actionId = line.strip().split('actionId : ')[1]
                break

    print("Updating action config...")
    flexApiClient.update_action_config(file_path, actionId)

if __name__ == "__main__":
    main()