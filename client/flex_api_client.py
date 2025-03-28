import requests
import base64
import datetime
from objects.flex_objects import FlexInstance, FlexAsset
from datetime import datetime, timedelta
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import detect_encoding
import urllib.parse

# Increase default recursion limit (from 999 to 1500)
# See : https://stackoverflow.com/questions/14222416/recursion-in-python-runtimeerror-maximum-recursion-depth-exceeded-while-callin
# max_number_of_objects_to_retrieve = limit * recursion_limit
sys.setrecursionlimit(1500)

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
        
    def get_workflow_definition_id(self, workflowDefinitionName):
        """Get Workflow Definition."""
        endpoint = f"/workflowDefinitions;name={workflowDefinitionName};exactNameMatch=true"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()

            return response.json()["workflowDefinitions"][0]["id"]
        except requests.RequestException as e:
            raise Exception(e)
        
    def get_action_id(self, actionName):
        """Get action."""
        endpoint = f"/actions;name={actionName};exactNameMatch=true"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()

            return response.json()["actions"][0]["id"]
        except requests.RequestException as e:
            raise Exception(e)
    
    def get_jobs_by_filter(self, filters, offset = 0, limit = 100):
        """Get jobs."""
        endpoint = f"/jobs;{filters};offset={offset}"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            response_json = response.json()
            job_list = response_json["jobs"]
            for job in response_json["jobs"]:
                flex_job = FlexInstance(job["id"], None, job["name"], None, job["objectType"]["id"], job["objectType"]["name"], job["status"], job["scheduled"], job["created"])
                job_list.append(flex_job)

            # default limit is 100
            total_results = response_json["totalCount"]
            if (total_results > offset + limit):
                job_list.extend(self.get_jobs_by_filter(filters, offset + limit))

            return job_list
        except requests.RequestException as e:
            raise Exception(e)

    def get_jobs_by_filter_df(self, filters, offset = 0, limit = 100):
        """Get jobs."""
        endpoint = f"/jobs;{filters};offset={offset}"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            response_json = response.json()
            job_list = []
            job_list.extend(response_json["jobs"])

            # default limit is 100
            total_results = response_json["totalCount"]
            if (total_results > offset + limit):
                job_list.extend(self.get_jobs_by_filter_df(filters, offset + limit))

            return job_list
        except requests.RequestException as e:
            raise Exception(e)
        
    def get_jobs_batch_by_filter(self, filters, offset = 0, limit = 100):
        """Get jobs."""
        endpoint = f"/jobs;{filters};offset={offset}"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            response_json = response.json()
            return response_json
        except requests.RequestException as e:
            raise Exception(e)
        
    def get_workflows_by_filter(self, filters, offset = 0):
        """Get workflows."""
        endpoint = f"/workflows;{filters};offset={offset}"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            response_json = response.json()
            workflow_list = []
            for workflow in response_json["workflows"]:
                if (workflow.get("asset")):
                    flex_workflow = FlexInstance(workflow["id"], None, workflow["name"], None, workflow["objectType"]["id"], workflow["objectType"]["name"], workflow["status"], None, workflow["created"], workflow["asset"]["id"], workflow["asset"]["name"], workflow["asset"]["type"])
                else: flex_workflow = FlexInstance(workflow["id"], None, workflow["name"], None, workflow["objectType"]["id"], workflow["objectType"]["name"], workflow["status"], None, workflow["created"], None, None, None)
                workflow_list.append(flex_workflow)

            # default limit is 100
            total_results = response_json["totalCount"]
            if (total_results > offset + 100):
                workflow_list.extend(self.get_workflows_by_filter(filters, offset + 100))

            return workflow_list
        except requests.RequestException as e:
            raise Exception(e)
        
    def get_object_configuration(self, actionId, objectName):
        """Get action configuration."""
        endpoint = f"/{objectName}s/{actionId}/configuration"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()

            return response.json()
        except requests.RequestException as e:
            raise Exception(e)
        
    def get_resource(self, resourceId):
        """Get resource."""
        endpoint = f"/resources/{resourceId}"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()

            return response.json()
        except requests.RequestException as e:
            raise Exception(e)
    
    def get_resource_subtype(self, resourceId):
        """Get resource subType"""
        return self.get_resource(resourceId)["resourceSubType"]
    
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
        
    def get_script_configuration(self, objectId):
        """Get the action configuration from the environment."""
        endpoint = f"/actions/{objectId}/configuration"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            response_json = response.json()

            # Works only with scripts
            script_content = response_json["instance"]["internal-script"]["script-content"]
            script_import = response_json["instance"]["internal-script"]["script-import"]
            internal_jar_url = response_json["instance"]["internal-script"]["internal-jar-url"]
            lock = response_json["instance"]["execution-lock-type"]
            return script_content, script_import, internal_jar_url, lock
        except requests.RequestException as e:
            raise Exception(e)
    

    def push_object_configuration(self, file_path, objectId, objectType, keep_imports = False):
        """Push the action configuration to the environment."""
        endpoint = f"/{objectType}s/{objectId}/configuration"
        try:
            encoding = detect_encoding(file_path)

            with open(file_path, 'r', encoding=encoding) as file:
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
                if 'setAssetMetadata' in extracted_content and not keep_imports:
                    lock_type = 'EXCLUSIVE'
                else:
                    lock_type = 'NONE'
                
                if not keep_imports:
                    payload = {
                        'internal-script': {
                            'script-content': extracted_content,
                            'script-import': imports
                            },
                        'execution-lock-type': lock_type
                    }
                else:
                    job = self.get_job(objectId)
                    action_id = job["action"]["id"]
                    script_content, script_import, internal_jar_url, lock = self.get_script_configuration(action_id)
                    payload = {
                        'internal-script': {
                            'script-content': extracted_content,
                            'script-import': script_import,
                            'internal-jar-url': internal_jar_url
                            },
                        'execution-lock-type': lock
                    }


                response = requests.put(self.base_url + endpoint, json=payload, headers=self.headers)
                response.raise_for_status()
                return response.json()
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            pass
        except requests.RequestException as e:
            print(e)
            pass
    
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
                data_to_insert = f"""\n\n\t/**\n\tcreated : {datetime.now()}\n\tname : {actionName}\n\tactionId : {actionId}\n\tactionUuid : {actionUuid}\n\t**/\n\n"""
                for i, line in enumerate(lines):
                    if 'FlexSdkClient flexSdkClient' in line.strip():
                        insert_index = i + 1
                        break
            else:
                data_to_insert = f"""\n\n/**\ncreated : {datetime.now()}\nname : {actionName}\nactionId : {actionId}\nactionUuid : {actionUuid}\n**/\n\n"""
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
        
    def create_job(self, actionId, assetId = None, variables = None):
        """Create a new job."""
        endpoint = "/jobs"
        try:
            payload = {
                        'actionId': actionId
                    }
                
            if assetId:
                payload["assetId"] = assetId

            if variables:
                payload["stringVariables"] = variables

            response = requests.post(self.base_url + endpoint, json=payload, headers=self.headers)
            response.raise_for_status()

            return response.json()
        except requests.RequestException as e:
            raise Exception(e)
        
    def create_workflow(self, definitionId, assetId, variables = None):
        """Create a new workflow."""
        endpoint = "/workflows"
        try:
            payload = {
                        'definitionId': definitionId
                    }
                
            if assetId:
                payload["assetId"] = assetId

            if variables:
                payload["stringVariables"] = variables

            response = requests.post(self.base_url + endpoint, json=payload, headers=self.headers)
            response.raise_for_status()

            print("Launched workflow ID " + str(response.json()["id"]))

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
                print(f"Couldn't retry the job as it is not Failed, its status is : {jobStatus}")
                pass

            payload = {
                        'action': 'retry'
                    }
            
            print(f"Retrying job ID {jobId}")
            response = requests.post(self.base_url + endpoint, json=payload, headers=self.headers)
            response.raise_for_status()

            return response.json()
        except requests.RequestException as e:
            print(f"Couldn't retry job ID {jobId} :", e)
            pass
        
    def cancel_job(self, jobId):
        """Cancel a job."""
        endpoint = f"/jobs/{jobId}/actions"
        try:
            """
            jobStatus = self.get_job(jobId)["status"]

            if jobStatus != "Failed" or jobStatus != "Pending":
                raise Exception(f"Couldn't cancel the job as it is not Failed, its status is : {jobStatus}")
            """

            payload = {
                        'action': 'cancel'
                    }
                
            response = requests.post(self.base_url + endpoint, json=payload, headers=self.headers)
            response.raise_for_status()

            return response.json()
        except requests.RequestException as e:
            print(f"POST request error: {e}")
            return None
        
    def cancel_instance(self, type, instanceId):
        """Cancel a job."""
        endpoint = f"/{type}/{instanceId}/actions"
        try:
            status = self.get_instance(instanceId, type)["status"]

            if status != "Failed" :
                raise Exception(f"Couldn't cancel the instance ID {instanceId} as it is not Failed, its status is : {status}")
            payload = {
                        'action': 'cancel'
                    }
                
            response = requests.post(self.base_url + endpoint, json=payload, headers=self.headers)
            response.raise_for_status()

            return response.json()
        except requests.RequestException as e:
            print(f"POST request error: {e}")
            return None
    
    def get_jobs(self, name=None, status=None):
        """Get a job."""
        endpoint = f"/jobs"
        filters = []
        if (name):
            filters.append(f"name={name}")
        if (status):
            filters.append(f"statuses={status}")
        for filter in filters:
            endpoint += f";{filter}"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(e)
        
    def get_job_history(self, job_id):
        """Get a job."""
        endpoint = f"/jobs/{job_id}/history"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(e)
        
    def get_asset(self, asset_id):
        """Get an asset."""
        endpoint = f"/assets/{asset_id}"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(e)
        
    def get_asset_filename(self, asset_id):
        """Get an asset filename."""
        try:
            return self.get_asset(asset_id)["fileInformation"]["originalFileName"]
        except requests.RequestException as e:
            raise Exception(e)

    def get_assets_by_filters(self, filters, offset = 0, pagination=False, createdFrom=None, createdTo=None, pagination_delta_in_days=None):
        """Get assets."""
        """Supports the offset until 10000 results, and pagination on created dates if it is required (metadata filters)."""
        # Set variables
        limit = 100
        if not pagination_delta_in_days:
            pagination_delta_in_days = 10

        # End condition
        if createdFrom and datetime.now() < datetime.strptime(createdFrom, '%d %b %Y'):
            # if current_datetime < createdFromAsDate
            # createdFrom date cannot be a future date : return an empy list.
            parsed_current_date = datetime.now().strftime('%d %b %Y')
            print(f"createdFrom is later that the current date : createdFrom={createdFrom}, current_date={parsed_current_date}")
            # No asset can be found
            return []
        
        # Set up creation date filters for pagination in the endpoint
        if createdFrom and createdTo:
            endpoint = f"/assets;{filters};offset={offset};createdFrom={createdFrom};createdTo={createdTo}"
        else:
            endpoint = f"/assets;{filters};offset={offset}"

        # Retrieve assets
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            response_json = response.json()
            response_assets = response_json["assets"]
            total_results = response_json["totalCount"]

            print(f"Found {total_results} assets with filters {filters}, offset {offset}, createdFrom {createdFrom}, createdTo {createdTo}")

            asset_list = []
            for asset in response_assets:
                if (asset["fileInformation"]["originalFileName"]):
                    flex_asset = FlexAsset(asset["id"], asset["uuid"], asset["name"], asset["displayName"], asset["objectType"]["id"], asset["objectType"]["name"], asset["fileInformation"]["originalFileName"])
                else:
                    flex_asset = FlexAsset(asset["id"], asset["uuid"], asset["name"], asset["displayName"], asset["objectType"]["id"], asset["objectType"]["name"], None)
                asset_list.append(flex_asset)

            if (total_results > 10000 and "metadata" in filters):
                # Activate pagination
                if "created" not in filters:
                    # if not createdTo is equivalent to if not pagination
                    if not pagination:
                        # Init created - 1st of Sept. 2023
                        from_date = datetime(2023, 9, 1)
                        createdFrom = from_date.strftime('%d %b %Y')
                        new_createdTo = from_date + timedelta(days=pagination_delta_in_days)
                        createdTo = new_createdTo.strftime('%d %b %Y')
                        asset_list.extend(self.get_assets_by_filters(filters, 0, True, createdFrom, createdTo))
                    else:
                        # if pagination and total_results > 10000, divide the pagination delta by 2
                        pagination_delta_in_days //= 2
                        print(f"Reducing the pagination delta to {pagination_delta_in_days}")
                        parsed_createdTo = datetime.strptime(createdTo, '%d %b %Y')
                        # Add days for the pagination
                        new_createdTo = parsed_createdTo - timedelta(days=pagination_delta_in_days)
                        createdTo = new_createdTo.strftime('%d %b %Y')
                        asset_list.extend(self.get_assets_by_filters(filters, 0, True, createdFrom, createdTo))
                else:
                    raise Exception("Unable to paginate on the creation date filters as there query already contains a creation date filter.")

            elif (total_results > offset + limit):
                # Set new offset
                asset_list.extend(self.get_assets_by_filters(filters, offset + limit, pagination, createdFrom, createdTo))
            elif pagination:
                # Set new pagination creation date filters
                createdFrom = createdTo
                parsed_date = datetime.strptime(createdTo, '%d %b %Y')
                # Add days for the pagination
                new_date = parsed_date + timedelta(days=pagination_delta_in_days)
                createdTo = new_date.strftime('%d %b %Y')
                asset_list.extend(self.get_assets_by_filters(filters, 0, True, createdFrom, createdTo))

            return asset_list
        except requests.RequestException as e:
            raise Exception(e)
        
    def get_workflow_jobs(self, workflow_id):
        """Get workflow jobs."""
        endpoint = f"/workflows/{workflow_id}/jobs"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            response_json = response.json()
            return response_json
        except requests.RequestException as e:
            raise Exception(e)
        
    def get_assets_by_filters_full(self, filters, offset = 0, pagination=False, createdFrom=None, createdTo=None, pagination_delta_in_days=None):
        """Get assets."""
        """Return a list of dict."""
        """Supports the offset until 10000 results, and pagination on created dates if it is required (metadata filters)."""
        # Set variables
        limit = 500
        if not pagination_delta_in_days:
            pagination_delta_in_days = 10

        # End condition
        if createdFrom and datetime.now() < datetime.strptime(createdFrom, '%d %b %Y'):
            # if current_datetime < createdFromAsDate
            # createdFrom date cannot be a future date : return an empy list.
            parsed_current_date = datetime.now().strftime('%d %b %Y')
            print(f"createdFrom is later that the current date : createdFrom={createdFrom}, current_date={parsed_current_date}")
            # No asset can be found
            return []
        
        # Set up creation date filters for pagination in the endpoint
        if createdFrom and createdTo:
            endpoint = f"/assets;{filters};offset={offset};createdFrom={createdFrom};createdTo={createdTo}"
        else:
            endpoint = f"/assets;{filters};offset={offset}"

        # Retrieve assets
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            response_json = response.json()
            response_assets = response_json["assets"]
            total_results = response_json["totalCount"]

            print(f"Found {total_results} assets with filters {filters}, offset {offset}, createdFrom {createdFrom}, createdTo {createdTo}")

            asset_list = []
            asset_list.extend(response_assets)

            if (total_results > 10000 and "metadata" in filters):
                # Activate pagination
                if "created" not in filters:
                    # if not createdTo is equivalent to if not pagination
                    if not pagination:
                        # Init created - 1st of Sept. 2023
                        from_date = datetime(2023, 9, 1)
                        createdFrom = from_date.strftime('%d %b %Y')
                        new_createdTo = from_date + timedelta(days=pagination_delta_in_days)
                        createdTo = new_createdTo.strftime('%d %b %Y')
                        asset_list.extend(self.get_assets_by_filters_full(filters, 0, True, createdFrom, createdTo))
                    else:
                        # if pagination and total_results > 10000, divide the pagination delta by 2
                        pagination_delta_in_days //= 2
                        print(f"Reducing the pagination delta to {pagination_delta_in_days}")
                        parsed_createdTo = datetime.strptime(createdTo, '%d %b %Y')
                        # Add days for the pagination
                        new_createdTo = parsed_createdTo - timedelta(days=pagination_delta_in_days)
                        createdTo = new_createdTo.strftime('%d %b %Y')
                        asset_list.extend(self.get_assets_by_filters_full(filters, 0, True, createdFrom, createdTo))
                else:
                    raise Exception("Unable to paginate on the creation date filters as there query already contains a creation date filter.")

            elif (total_results > offset + limit):
                # Set new offset
                asset_list.extend(self.get_assets_by_filters_full(filters, offset + limit, pagination, createdFrom, createdTo))
                    
            elif pagination:
                # Set new pagination creation date filters
                createdFrom = createdTo
                parsed_date = datetime.strptime(createdTo, '%d %b %Y')
                # Add days for the pagination
                new_date = parsed_date + timedelta(days=pagination_delta_in_days)
                createdTo = new_date.strftime('%d %b %Y')
                asset_list.extend(self.get_assets_by_filters_full(filters, 0, True, createdFrom, createdTo))

            return asset_list
        except requests.RequestException as e:
            raise Exception(e)
        
    def get_objects_by_filters(self, type, filters, limit = 100, offset = 0, pagination=False, createdFrom=None, createdTo=None, pagination_delta_in_days=None, plural_name=None, pagination_delta_in_hours = 24):
        """Get objects."""
        """Supports the offset until 10000 results, and pagination on created dates if it is required (metadata filters)."""
        # Set variables
        if not pagination_delta_in_days:
            pagination_delta_in_days = 10

        if pagination_delta_in_hours != 24 and createdTo.hours < 24:
            time_change = datetime.timedelta(hours=pagination_delta_in_hours)
            createdFrom += time_change
            createdTo += time_change

        # End condition
        if createdFrom and datetime.now() < datetime.strptime(createdFrom, '%d %b %Y'):
            # if current_datetime < createdFromAsDate
            # createdFrom date cannot be a future date : return an empy list.
            parsed_current_date = datetime.now().strftime('%d %b %Y')
            print(f"createdFrom is later that the current date : createdFrom={createdFrom}, current_date={parsed_current_date}")
            # No asset can be found
            return []
        
        if (plural_name):
            if createdFrom and createdTo:
                endpoint = f"/{plural_name};{filters};offset={offset};createdFrom={createdFrom};createdTo={createdTo}"
            else:
                endpoint = f"/{plural_name};{filters};offset={offset}"

        else:
            # Set up creation date filters for pagination in the endpoint
            if createdFrom and createdTo:
                if ('fql' in filters):
                    # AND created > "2019-08-22" AND created < "2024-03-22"
                    parsed_created_from = datetime.strptime(createdFrom, '%d %b %Y')
                    fql_formatted_created_from = datetime.strftime(parsed_created_from, '%Y-%m-%d')
                    parsed_created_to = datetime.strptime(createdTo, '%d %b %Y')
                    fql_formatted_created_to = datetime.strftime(parsed_created_to, '%Y-%m-%d')
                    date_filters_fql = f" AND created > \"{fql_formatted_created_from}\" AND created < \"{fql_formatted_created_to}\""
                    encoded_date_filters_fql = urllib.parse.quote(date_filters_fql)
                    # Add encoded date filters for fql
                    endpoint = f"/{type};{filters}{encoded_date_filters_fql};offset={offset}"
                else:
                    endpoint = f"/{type};{filters};offset={offset};createdFrom={createdFrom};createdTo={createdTo}"
            else:
                endpoint = f"/{type};{filters};offset={offset}"

        # Retrieve assets
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            response_json = response.json()
            object_list = response_json[type]
            total_results = response_json["totalCount"]

            print(f"Found {total_results} {type} with filters {filters}, offset {offset}, createdFrom {createdFrom}, createdTo {createdTo}")

            if (total_results > 10000 and "metadata" in filters):
                # Activate pagination
                if "created" not in filters:
                    # if not createdTo is equivalent to if not pagination
                    if not pagination:
                        # Init created - 1st of Sept. 2023
                        from_date = datetime(2023, 9, 1)
                        createdFrom = from_date.strftime('%d %b %Y')
                        new_createdTo = from_date + timedelta(days=pagination_delta_in_days)
                        createdTo = new_createdTo.strftime('%d %b %Y')
                        object_list.extend(self.get_objects_by_filters(type, filters, limit, 0, True, createdFrom, createdTo, None, plural_name))
                    else:
                        if pagination_delta_in_days == 1:
                            pagination_delta_in_hours //= 2
                            print(f"Reducing the pagination delta to {pagination_delta_in_hours} hours")
                            parsed_createdTo = datetime.strptime(createdTo, '%d %b %Y')
                            # Add days for the pagination
                            new_createdTo = parsed_createdTo - timedelta(days=pagination_delta_in_days)
                            createdTo = new_createdTo.strftime('%d %b %Y')
                            object_list.extend(self.get_objects_by_filters(type, filters, limit, 0, True, createdFrom, createdTo, pagination_delta_in_days, plural_name, pagination_delta_in_hours))
                        else:
                            # if pagination and total_results > 10000, divide the pagination delta by 2
                            pagination_delta_in_days //= 2
                            print(f"Reducing the pagination delta to {pagination_delta_in_days} days")
                            parsed_createdTo = datetime.strptime(createdTo, '%d %b %Y')
                            # Add days for the pagination
                            new_createdTo = parsed_createdTo - timedelta(days=pagination_delta_in_days)
                            createdTo = new_createdTo.strftime('%d %b %Y')
                            object_list.extend(self.get_objects_by_filters(type, filters, limit, 0, True, createdFrom, createdTo, pagination_delta_in_days, plural_name))
                else:
                    raise Exception("Unable to paginate on the creation date filters as there query already contains a creation date filter.")

            elif (total_results > offset + limit):
                # Set new offset
                object_list.extend(self.get_objects_by_filters(type, filters, limit, offset + limit, pagination, createdFrom, createdTo, None, plural_name))
            elif pagination:
                # Set new pagination creation date filters
                createdFrom = createdTo
                parsed_date = datetime.strptime(createdTo, '%d %b %Y')
                # Add days for the pagination
                new_date = parsed_date + timedelta(days=pagination_delta_in_days)
                createdTo = new_date.strftime('%d %b %Y')
                object_list.extend(self.get_objects_by_filters(type, filters, limit, 0, True, createdFrom, createdTo, None, plural_name))

            return object_list
        except requests.RequestException as e:
            raise Exception(e)
        
    def get_total_results(self, type, filters):
        """Get the total number of results."""
        endpoint = f"/{type};{filters};limit=1"
        # Retrieve objects
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            response_json = response.json()
            total_results = response_json["totalCount"]
            return total_results
        except requests.RequestException as e:
            raise Exception(e)
        
    def retry_workflow(self, workflowId):
        """Retry a workflow."""
        endpoint = f"/workflows/{workflowId}/actions"
        try:
            workflowStatus = self.get_workflow(workflowId)["status"]

            if workflowStatus != "Failed":
                raise Exception(f"Couldn't retry the job as it is not Failed, its status is : {workflowStatus}")

            payload = {
                        'action': 'retry'
                    }
            
            print(f"Retrying workflow ID {workflowId}")
            response = requests.post(self.base_url + endpoint, json=payload, headers=self.headers)
            response.raise_for_status()

            return response.json()
        except requests.RequestException as e:
            print(f"Couldn't retry job ID {workflowId} :", e)

    def get_workflow(self, workflowId, include_variables = 'false'):
        """Get a workflow."""
        endpoint = f"/workflows/{workflowId};includeVariables={include_variables}"
        try:
                
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(e)
        
    def get_instance(self, instanceId, type):
        """Get an instance."""
        endpoint = f"/{type}/{instanceId}"
        try:
                
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(e)
        
    def retry_instance(self, instanceId, type):
        """Retry an instance."""
        endpoint = f"/{type}/{instanceId}/actions"
        try:
            status = self.get_instance(instanceId, type)["status"]

            if status != "Failed":
                print(f"Couldn't retry the job as it is not Failed, its status is : {status}")

            payload = {
                        'action': 'retry'
                    }
            
            print(f"Retrying instance ID {instanceId}")
            response = requests.post(self.base_url + endpoint, json=payload, headers=self.headers)
            response.raise_for_status()

            return response.json()
        except requests.RequestException as e:
            print(f"Couldn't retry instance ID {instanceId} :", e)

    def get_next_objects(self, type, filters, offset = 0, limit = 100):
        """Get next objects."""
        endpoint = f"/{type};{filters};offset={offset};limit={limit}"

        # Retrieve objects
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            response_json = response.json()
            return response_json
        except requests.RequestException as e:
            raise Exception(e)
        
    def get_workflow_structure(self, workflowDefinitionId):
        """Get workflow structure."""
        endpoint = f"/workflowDefinitions/{workflowDefinitionId}/structure"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            response_json = response.json()
            return response_json

        except requests.RequestException as e:
            raise Exception(e)