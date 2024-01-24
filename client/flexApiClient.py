import requests
import base64
import datetime

class FlexApiClient:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        
        # Prepare basic authentication header
        credentials = f"{username}:{password}"
        base64_encoded_credentials = base64.b64encode(credentials.encode())
        auth_header = {'Authorization': f'Basic {base64_encoded_credentials.decode()}'}

        # Set Content-Type header and combine with additional headers
        self.headers = {
            'Content-Type': 'application/vnd.nativ.mio.v1+json',
            **auth_header,
        }
    
    def get_action(self, actionId):
        """Get action."""
        endpoint = f"/actions/{actionId}"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()

            return response.json()
        except requests.RequestException as e:
            raise Exception(e)
        
    def get_action_configuration(self, actionId):
        """Get action configuration."""
        endpoint = f"/actions/{actionId}/configuration"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()

            return response.json()
        except requests.RequestException as e:
            raise Exception(e)
        
    def create_action(self, actionName, file_path, accountId):
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
                        'visibilityIds': [accountId]
                      }
            
            response = requests.post(self.base_url + endpoint, json=payload, headers=self.headers)
            response.raise_for_status()
            
            self.actionId = response.json()["id"]
            self.actionUuid = response.json()["uuid"]

            ## Add header
            self.writeClassHeader(actionName, self.actionId, self.actionUuid, file_path)

            return response.json()
        except requests.RequestException as e:
            raise Exception(e)
        
    def push_action_configuration(self, file_path, objectId, objectType):
        """Push the action configuration to the environment."""
        endpoint = f"/{objectType}s/{objectId}/configuration"
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()

                ## Parse the file properly
                start_condition = "**/"
                end_condition = '}'
                capture = False
                captured_content = []
                imports = []

                # Reverse the list to find the last '}' from the end
                for line in reversed(lines):
                    if end_condition in line:
                        last_brace_index = lines.index(line)
                        break

                for line in lines:
                    if capture and lines.index(line) < last_brace_index:
                        captured_content.append(line)
                    elif start_condition in line:
                        capture = True
                        continue  # Skip the line with the start condition
                    else:
                        if line.startswith('import ') and not line.startswith('import com.ooyala.flex') or line.startswith('import com.ooyala.flex.mediacore'):
                            # Import the correct libs
                            imports.append(line.replace('import ', ''))


                # Convert the list of lines to a single string
                extracted_content = ''.join(captured_content)
            
                # Auto-select the lock type
                if 'setAssetMetadata' in extracted_content:
                    lock_type = 'EXCLUSIVE'
                else:
                    lock_type = 'NONE'

                ## Encode the extracted_content special characters
                encoded_content = extracted_content.encode('ISO-8859-1').decode('utf-8')
                
                payload = {
                    'internal-script': {
                        'script-content': encoded_content,
                        'script-import': imports
                        },
                    'execution-lock-type': lock_type
                }

                response = requests.put(self.base_url + endpoint, json=payload, headers=self.headers)
                response.raise_for_status()
                return response.json()
        except FileNotFoundError:
            raise Exception(f"File not found: {file_path}")
        except requests.RequestException as e:
            raise Exception(e)
    
    def pull_action_configuration(self, file_path, objectId, objectType):
        """Pull the action configuration from the environment."""
        endpoint = f"/{objectType}s/{objectId}/configuration"
        try:

            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            responseJson = response.json()

            if "errors" in responseJson:
                raise Exception(responseJson["errors"]["error"])
            
            scriptContent = responseJson["instance"]["internal-script"]["script-content"]

            with open(file_path, 'r') as file:
                lines = file.readlines()

                ## Parse the file properly
                start_condition = "**/"

                ## TODO : add imports
                # imports = []

                actionIdLine = f"actionId : {objectId}"
                hasHeader = False

                for line in lines:
                    if actionIdLine in line:
                        hasHeader = True
                    if hasHeader and start_condition in line:
                        start_index = lines.index(line)
                        break
                    if "execute()" in line:
                        break
                
                # Split the script content string into a list of lines
                lines_to_add = scriptContent.split('\n')

                ## Encode the extracted_content special characters
                # encoded_content = extracted_content.encode('ISO-8859-1').decode('utf-8')
                    
            # Truncate the content after the specified line number
            # and insert the new content at that position
            lines = lines[:start_index + 1] + ['\n\t' + scriptContent.replace('\r', '') + '\n}']
            with open(file_path, 'w') as file:
                file.writelines(lines)
        except FileNotFoundError:
            raise Exception(f"File not found: {file_path}")
        except requests.RequestException as e:
            raise Exception(e)
        
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
            raise Exception(e)
        
    def writeClassHeader(self, actionName, actionId, actionUuid, file_path):
            
        # Read the existing content
        with open(file_path, 'r') as file:
            lines = file.readlines()

            # Convert the list of lines to a single string for easy searching
            file_content = ''.join(lines)

            insert_index = 0
            if 'GroovyScriptContext context' in file_content and 'FlexSdkClient flexSdkClient' in file_content:
                data_to_insert = f"""\n\n\t/**\n\tcreated : {datetime.date.today()}\n\tname : {actionName}\n\tactionId : {actionId}\n\tactionUuid : {actionUuid}\n\t**/\n\n"""
                for i, line in enumerate(lines):
                    if 'FlexSdkClient flexSdkClient' in line.strip():
                        insert_index = i + 1
                        break
            else:
                data_to_insert = f"""\n\n/**\ncreated : {datetime.date.today()}\nname : {actionName}\nactionId : {actionId}\nactionUuid : {actionUuid}\n**/\n\n"""
                # Find the end of the import statements
                for i, line in enumerate(lines):
                    if not line.strip().startswith('import') and line.strip() != '':
                        insert_index = i
                        break

            # Insert the new data
            lines.insert(insert_index, data_to_insert)
            self.classHeader = data_to_insert

            # Write everything back to the file
            with open(file_path, 'w') as file:
                print("Writing header at line " + str(insert_index))
                file.writelines(lines)
        
    def create_job(self, actionId):
        """Create a new job."""
        endpoint = "/jobs"
        try:
            payload = {
                        'actionId': actionId
                    }
                
            response = requests.post(self.base_url + endpoint, json=payload, headers=self.headers)
            response.raise_for_status()

            return response.json()
        except requests.RequestException as e:
            raise Exception(e)
        
    def get_account_id(self, accountName):
        """Get account ID"."""
        endpoint = f"/accounts;name={accountName}"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()

            return response.json()["accounts"][0]["id"]
        except requests.RequestException as e:
            raise Exception(e)
        
    def get_job(self, jobId):
        """Get a job."""
        endpoint = f"/jobs/{jobId}"
        try:
                
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(e)
    
    def retry_job(self, jobId):
        """Retry a job."""
        endpoint = f"/jobs/{jobId}/actions"
        try:
            jobStatus = self.get_job(jobId)["status"]

            if jobStatus != "Failed":
                raise Exception(f"Couldn't retry the job as it is not Failed, its status is : {jobStatus}")

            payload = {
                        'action': 'retry'
                    }
                
            response = requests.post(self.base_url + endpoint, json=payload, headers=self.headers)
            response.raise_for_status()

            return response.json()
        except requests.RequestException as e:
            raise Exception(e)
        
    def cancel_job(self, jobId):
        """Cancel a job."""
        endpoint = f"/jobs/{jobId}/actions"
        try:
            jobStatus = self.get_job(jobId)["status"]

            if jobStatus != "Failed":
                raise Exception(f"Couldn't cancel the job as it is not Failed, its status is : {jobStatus}")
            payload = {
                        'action': 'cancel'
                    }
                
            response = requests.post(self.base_url + endpoint, json=payload, headers=self.headers)
            response.raise_for_status()

            return response.json()
        except requests.RequestException as e:
            print(f"POST request error: {e}")
            return None