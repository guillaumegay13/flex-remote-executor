from ...client.flexApiClient import FlexApiClient
import sys
import os

        
def main():

    file_path = sys.argv[1]    # Path to the current file in IntelliJ

    actionName = os.path.splitext(os.path.basename(file_path))[0]

    baseUrl = os.environ.get('BASE_URL')
    username = os.environ.get('USERNAME')
    password = os.environ.get('PASSWORD')

    flexApiClient = FlexApiClient(baseUrl, username, password)

    # Dynamically get the account ID
    accountName = baseUrl.replace('https://', '').split('.')[0]
    accountId = flexApiClient.get_account_id(accountName)

    print("Creating action...")
    createActionResponse = flexApiClient.create_action(actionName, file_path, accountId)
    actionId = createActionResponse["id"]

    print("Updating action config...")
    flexApiClient.update_config(file_path, actionId, "action")

    print("Enabling action...")
    flexApiClient.enable_action(actionId)

if __name__ == "__main__":
    main()