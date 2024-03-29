from client.flex_api_client import FlexApiClient
import requests
from objects.flex_objects import FlexObject, FlexCmObject, FlexMetadataField, FlexCmResource, FlexObjectField, FlexTaxonomyField

class FlexCmClient(FlexApiClient):
    def __init__(self, base_url, username, password):
        super().__init__(base_url, username, password)

    def get_workflow_definition(self, name = None, uuid = None):
        """Get workflow definition."""
        endpoint = f"/workflowDefinitions"
        if name:
            endpoint += f";name={name};exactNameMatch=true"
        elif uuid:
            endpoint += f";uuid={uuid}"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()

            response_json = response.json()
            totalCount = response_json["totalCount"]

            if (totalCount == 0):
                raise Exception(f"No workflow definition found")
            else:
                workflowDefinition = response_json["workflowDefinitions"][0]
            
            workflow_definition = FlexCmObject(workflowDefinition["id"], workflowDefinition["uuid"], workflowDefinition["name"], workflowDefinition["displayName"], workflowDefinition["objectType"]["id"], workflowDefinition["objectType"]["name"], "workflow_definition")

            return workflow_definition

        except requests.RequestException as e:
            raise Exception(e)

    def get_workflow_references(self, workflowDefinitionId):
        """Get workflow references."""
        endpoint = f"/workflowDefinitions/{workflowDefinitionId}/references"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()

            response_json = response.json()
            totalCount = response_json["totalCount"]
            self.flex_object_reference_list = []

            if (totalCount > 0):
                objects = response_json["objects"]
                for object in objects:
                    flex_object = FlexCmObject(object["id"], object["uuid"], object["name"], object["displayName"], object["objectType"]["id"], object["objectType"]["name"], object["objectType"]["name"])
                    self.flex_object_reference_list.append(flex_object)

            return self.flex_object_reference_list

        except requests.RequestException as e:
            raise Exception(e)
        
    def get_object_references(self, object):
        """Get object references."""
        endpoint = f"/{object.objectTypeName}s/{object.id}/references"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()

            response_json = response.json()
            totalCount = response_json["totalCount"]
            self.flex_object_reference_list = []

            if (totalCount > 0):
                objects = response_json["objects"]
                for object in objects:
                    flex_object = FlexCmObject(object["id"], object["uuid"], object["name"], object["displayName"], object["objectType"]["id"], object["objectType"]["name"], object["objectType"]["name"])
                    self.flex_object_reference_list.append(flex_object)

            return self.flex_object_reference_list

        except requests.RequestException as e:
            raise Exception(e)
    
    def get_workflow_structure(self, workflowDefinitionId):
        """Get workflow structure."""
        endpoint = f"/workflowDefinitions/{workflowDefinitionId}/structure"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()

            response_json = response.json()
            
            nodes = response_json["nodes"]

            self.actionList = []
            self.actionNameList = []

            if (len(nodes) > 0):
                for node in nodes:
                    if (node["type"] == "ACTION"):
                        object = node["action"]
                        if (object["name"] not in self.actionNameList):
                            flexObject = FlexCmObject(object["id"], object["uuid"], object["name"], object["displayName"], object["actionType"]["id"], object["actionType"]["name"], "action")
                            self.actionList.append(flexObject)
                            self.actionNameList.append(flexObject.name)

            return self.actionList

        except requests.RequestException as e:
            raise Exception(e)

    # Get resource reference
    # TODO: Get resource configuration ('/configuration') to get all the dependancies
    def get_resource_references(self, resourceId):
        """Get resource."""
        endpoint = f"/resources/{resourceId}"

    def get_metadata_definition(self, metadataDefinitionName):
        """Get metadata definition."""
        endpoint = f"/metadataDefinitions;name={metadataDefinitionName};exactNameMatch=true"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()

            response_json = response.json()
            totalCount = response_json["totalCount"]

            if (totalCount == 0):
                raise Exception(f"No metadata definition found with name {metadataDefinitionName}")
            else:
                metadataDefinition = response_json["metadataDefinitions"][0]
            
            self.metadataDefinitionId = metadataDefinition["id"]
            self.metadataDefinitionUuid = metadataDefinition["uuid"]

            return (self.metadataDefinitionUuid, self.metadataDefinitionId)

        except requests.RequestException as e:
            raise Exception(e)
        
    def get_metadata_definition_fields(self, metadataDefinitionId):
        """Get metadata definition fields."""
        endpoint = f"/metadataDefinitions/{metadataDefinitionId}/definition"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            response_json = response.json()

            return self.add_fields(response_json["definition"])
        except requests.RequestException as e:
            raise Exception(e)
        
    def add_fields(self, fieldDict):
        fieldList = []
        for field in fieldDict:
            if "multiplicity" in field:
                multiplicity = field["multiplicity"]
            else:
                multiplicity = "1"

            if "children" in field:
                isComplex = True
            else:
                isComplex = False

            if (field["type"] == "drill-down-option"):
                taxonomyId = field["filter"]
                taxonomyName = self.get_taxonomy_name(taxonomyId)
                fieldToAdd = FlexTaxonomyField(field["id"], field["name"], field["displayName"], field["description"], field["type"], multiplicity, field["searchable"], field["editable"], field["required"], field["formType"], field["format"], field["formatDescription"], field["validation"], field["maxLength"], field["expressionEnabled"], field["secretEnabled"], field["validationDescription"], field["validationHandler"], field["valueGeneratorType"], field["unitString"], field["commentable"], field["isVisible"], field["preProcessors"], False, field["filter"], field["backingStoreType"], taxonomyName)
            elif (field["type"] == "object"):
                if (field["objectTypeId"]):
                    # type
                    objectTypeId = field["objectTypeId"]
                    name, displayName, pluralName = self.get_object_type_names(objectTypeId)
                else:
                    # else notype
                    name, displayName, pluralName = None, None, None
                fieldToAdd = FlexObjectField(field["id"], field["name"], field["displayName"], field["description"], field["type"], multiplicity, field["searchable"], field["editable"], field["required"], field["formType"], field["format"], field["formatDescription"], field["validation"], field["maxLength"], field["expressionEnabled"], field["secretEnabled"], field["validationDescription"], field["validationHandler"], field["valueGeneratorType"], field["unitString"], field["commentable"], field["isVisible"], field["preProcessors"], False, field["objectType"], field["classNames"], field["objectTypeId"], field["variantId"], name, displayName, pluralName)
            else:
                fieldToAdd = FlexMetadataField(field["id"], field["name"], field["displayName"], field["description"], field["type"], multiplicity, field["searchable"], field["editable"], field["required"], field["formType"], field["format"], field["formatDescription"], field["validation"], field["maxLength"], field["expressionEnabled"], field["secretEnabled"], field["validationDescription"], field["validationHandler"], field["valueGeneratorType"], field["unitString"], field["commentable"], field["isVisible"], field["preProcessors"], isComplex)
            
            fieldList.append(fieldToAdd)
            
            if (isComplex):
                fieldList.extend(self.add_fields(field["children"]))

        return fieldList
    
    def get_taxonomy_name(self, taxonomyId):
        """Get taxonomy name."""
        endpoint = f"/taxonomies/{taxonomyId}"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            response_json = response.json()

            if "errors" in response_json:
                raise Exception(response_json["errors"]["error"])

            return response_json["name"]
        except requests.RequestException as e:
            raise Exception(e)
        
    def get_object_type_names(self, objectTypeId):
        """Get object type."""
        endpoint = f"/objectTypes/{objectTypeId}"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            response_json = response.json()

            if "errors" in response_json:
                raise Exception(response_json["errors"]["error"])

            return (response_json["name"], response_json["displayName"], response_json["pluralName"])
        except requests.RequestException as e:
            raise Exception(e)