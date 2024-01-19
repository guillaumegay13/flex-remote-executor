def create_action(flexApiClient, file_path, actionName, accountId):

    print("Creating action...")
    createActionResponse = flexApiClient.create_action(actionName, file_path, accountId)
    actionId = createActionResponse["id"]

    print("Updating action config...")
    flexApiClient.push_action_configuration(file_path, actionId, "action")

    print("Enabling action...")
    flexApiClient.enable_action(actionId)

def push_action_configuration(flexApiClient, file_path):

    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if 'actionId : ' in line:
                actionId = line.strip().split('actionId : ')[1]
                break

    print(f"Updating configuration of action ID {actionId}...")
    flexApiClient.push_action_configuration(file_path, actionId, "action")

def pull_action_configuration(flexApiClient, file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if 'actionId : ' in line:
                actionId = line.strip().split('actionId : ')[1]
                break

    print(f"Pulling configuration of action ID {actionId}...")
    flexApiClient.pull_action_configuration(file_path, actionId, "action")