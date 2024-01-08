import sys
import os
from client.flexApiClient import FlexApiClient
from actions.action import create_action, update_action
from actions.job import create_job, update_job, retry_last_job
from actions.file import create_file

def main():

    file_path = sys.argv[1]    # Path to the current file in IntelliJ
    action = sys.argv[-1]

    actionName = os.path.splitext(os.path.basename(file_path))[0]

    baseUrl = os.environ.get('BASE_URL')
    username = os.environ.get('USERNAME')
    password = os.environ.get('PASSWORD')

    flexApiClient = FlexApiClient(baseUrl, username, password)

    # Dynamically get the account ID
    accountName = baseUrl.replace('https://', '').split('.')[0]
    accountId = flexApiClient.get_account_id(accountName)

    match action:
        case "create_action":
            create_action(flexApiClient, file_path, actionName, accountId)
        case "update_action":
            update_action(flexApiClient, file_path)
        case "create_job":
            create_job(flexApiClient, file_path)
        case "update_job":
            update_job(flexApiClient, file_path)
        case "retry_last_job":
            retry_last_job(flexApiClient, file_path)
        case "create_file":
            className = sys.argv[2]
            project_path = file_path
            if (len(sys.argv) == 4):
                folder_name = sys.argv[3]
            create_file(project_path, className, folder_name)

if __name__ == "__main__":
    main()