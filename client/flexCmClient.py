from client.flexApiClient import FlexApiClient
import requests

class FlexObject():
    def __init__(self, id, uuid, name, displayName, objectTypeId, objectTypeName):
        self.id = id
        self.uuid = uuid
        self.name = name
        self.displayName = displayName
        self.objectTypeId = objectTypeId
        self.objectTypeName = objectTypeName

class FlexCmClient(FlexApiClient):
    def __init__(self, base_url, username, password):
        super().__init__(base_url, username, password)

    def get_workflow_definition(self, workflowDefinitionName):
        """Get workflow."""
        endpoint = f"/workflowDefinitions;name={workflowDefinitionName};exactNameMatch=true"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()

            responseJson = response.json()
            totalCount = responseJson["totalCount"]

            if (totalCount == 0):
                raise Exception(f"No workflow definition found with name {workflowDefinitionName}")
            else:
                workflowDefinition = responseJson["workflowDefinitions"][0]
            
            self.workflowDefinitionId = workflowDefinition["id"]
            self.workflowDefinitionUuid = workflowDefinition["uuid"]

            return (self.workflowDefinitionUuid, self.workflowDefinitionId)

        except requests.RequestException as e:
            raise Exception(e)

    def get_workflow_references(self, workflowDefinitionId):
        """Get workflow references."""
        endpoint = f"/workflowDefinitions/{workflowDefinitionId}/references"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()

            responseJson = response.json()
            totalCount = responseJson["totalCount"]
            self.flexObjectReferenceList = []

            if (totalCount > 0):
                objects = responseJson["objects"]
                for object in objects:
                    flexObject = FlexObject(object["id"], object["uuid"], object["name"], object["displayName"], object["objectType"]["id"], object["objectType"]["name"])
                    self.flexObjectReferenceList.append(flexObject)

            return self.flexObjectReferenceList

        except requests.RequestException as e:
            raise Exception(e)
    
    def get_workflow_structure(self, workflowDefinitionId):
        """Get workflow structure."""
        endpoint = f"/workflowDefinitions/{workflowDefinitionId}/structure"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()

            responseJson = response.json()
            
            nodes = responseJson["nodes"]

            self.actionList = []

            if (len(nodes) > 0):
                for node in nodes:
                    if (node["type"] == "ACTION"):
                        object = node["action"]
                        flexObject = FlexObject(object["id"], object["uuid"], object["name"], object["displayName"], object["actionType"]["id"], object["actionType"]["name"])
                        self.actionList.append(flexObject)

            return self.actionList

        except requests.RequestException as e:
            raise Exception(e)

    # Get resource reference
    # TODO: Get resource configuration ('/configuration') to get all the dependancies
    def get_resource_references(self, resourceId):
        """Get resource."""
        endpoint = f"/resources/{resourceId}"
