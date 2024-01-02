import requests
import base64
import datetime
import sys
import os

class ApiClient:
    def __init__(self, base_url, accountId, username, password):
        self.base_url = base_url
        self.accountId = accountId
        
        # Prepare basic authentication header
        credentials = f"{username}:{password}"
        base64_encoded_credentials = base64.b64encode(credentials.encode())
        auth_header = {'Authorization': f'Basic {base64_encoded_credentials.decode()}'}

        # Set Content-Type header and combine with additional headers
        self.headers = {
            'Content-Type': 'application/vnd.nativ.mio.v1+json',
            **auth_header,
        }
        
    def create_action(self, actionName, file_path):
        """Create a new action."""
        endpoint = "/actions"
        self.actionName = actionName
        self.file_path = file_path
        try:
            payload = {
                        'name': actionName,
                        'type': "Script",
                        'pluginClass': 'tv.nativ.mio.plugins.actions.jef.JEFActionProxyCommand',
                        'pluginUuid': 'cab6f437-3ce0-4857-9578-fd519b783d66',
                        'visibilityIds': [self.accountId]
                      }
            
            response = requests.post(self.base_url + endpoint, json=payload, headers=self.headers)
            response.raise_for_status()
            
            self.actionId = response.json()["id"]
            self.actionUuid = response.json()["uuid"]

            ## Add header
            self.writeClassHeader(actionName, self.actionId, self.actionUuid, file_path)

            return response.json()
        except requests.RequestException as e:
            print(f"POST request error: {e}")
            return None
        
    def update_action_config(self, file_path, actionId):
        """Update action configuration."""
        endpoint = f"/actions/{actionId}/configuration"
        try:
            with open(file_path, 'r') as file:
                file_content = file.read()

                ## TODO: the file content needs to be parsed properly
                ## TODO: import the correct libs
                ## TODO: auto-select the lock type
                imports = []
                payload = {
                    'internal-script': {
                        'script-content': file_content,
                        'script-import': imports
                        },
                    'execution-lock-type': 'EXCLUSIVE'
                }

                response = requests.put(self.base_url + endpoint, json=payload, headers=self.headers)
                response.raise_for_status()
                return response.json()
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return None
        except requests.RequestException as e:
            print(f"PUT request error: {e}")
            return None
        
    def enable_action(self, actionId):
        """Enable an action."""
        endpoint = f"/actions/{actionId}/actions"
        try:
            payload = {
                        'action': 'enable'
                      }
            
            response = requests.post(self.base_url + endpoint, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"POST request error: {e}")
            return None
        
    def writeClassHeader(self, actionName, actionId, actionUuid, file_path):
            
        # Read the existing content
        with open(file_path, 'r') as file:
            lines = file.readlines()

            # Convert the list of lines to a single string for easy searching
            file_content = ''.join(lines)

            insert_index = 0
            if 'GroovyScriptContext context' in file_content and 'FlexSdkClient flexSdkClient' in file_content:
                data_to_insert = f"""\n\n\t\"\"\"\n\tcreated : {datetime.date.today()}\n\tname : {actionName}\n\tactionId : {actionId}\n\tactionUuid : {actionUuid}\n\t\"\"\"\n\n"""
                for i, line in enumerate(lines):
                    if 'FlexSdkClient flexSdkClient' in line.strip():
                        insert_index = i + 1
                        break
            else:
                data_to_insert = f"""\n\n\"\"\"\ncreated : {datetime.date.today()}\nname : {actionName}\nactionId : {actionId}\nactionUuid : {actionUuid}\n\"\"\"\n\n"""
                # Find the end of the import statements
                for i, line in enumerate(lines):
                    if not line.strip().startswith('import') and line.strip() != '':
                        insert_index = i
                        break

            # Insert the new data
            lines.insert(insert_index, data_to_insert)

            # Write everything back to the file
            with open(file_path, 'w') as file:
                print("Writing header at line " + str(insert_index))
                file.writelines(lines)
        
def main():

    file_path = sys.argv[1]    # Path to the current file in IntelliJ

    actionName = os.path.splitext(os.path.basename(file_path))[0]

    baseUrl = os.environ.get('BASE_URL')
    username = os.environ.get('USERNAME')
    password = os.environ.get('PASSWORD')

    # TODO : dynamically get the account ID
    accountId = os.environ.get('ACCOUNT_ID')

    apiClient = ApiClient(baseUrl, accountId, username, password)

    print("Creating action...")
    createActionResponse = apiClient.create_action(actionName, file_path)
    actionId = createActionResponse["id"]

    print("Updating action config...")
    apiClient.update_action_config(file_path, actionId)

    print("Enabling action...")
    apiClient.enable_action(actionId)

if __name__ == "__main__":
    main()