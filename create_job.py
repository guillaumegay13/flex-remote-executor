from create_action import FlexApiClient
import os
import sys

def main():

    file_path = sys.argv[1]    # Path to the current file in IntelliJ

    baseUrl = os.environ.get('BASE_URL')
    username = os.environ.get('USERNAME')
    password = os.environ.get('PASSWORD')

    # TODO : dynamically get the account ID
    accountId = os.environ.get('ACCOUNT_ID')

    flexApiClient = FlexApiClient(baseUrl, accountId, username, password)

    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if 'actionId : ' in line:
                actionId = line.strip().split('actionId : ')[1]
                break

    print("Launching job...")
    response = flexApiClient.create_job(actionId)

    jobId = response["id"]
    print(f"Launched job ID {jobId}")

if __name__ == "__main__":
    main()