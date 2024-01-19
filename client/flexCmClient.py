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

class FlexMetadataField():
    def __init__(self, id, name, displayName, description, type, multiplicity, searchable, editable, required, formType, format, formatDescription, validation, maxLength, expressionEnabled, secretEnabled, validationDescription, validationHandler, valueGeneratorType, unitString, commentable, isVisible, preProcessors, isComplex):
        self.id = id
        self.name = name
        self.displayName = displayName
        self.description = description
        self.type = type
        self.multiplicity = multiplicity
        self.searchable = searchable
        self.editable = editable
        self.required = required
        self.formType = formType
        self.format = format
        self.formatDescription = formatDescription
        self.validation = validation
        self.maxLength = maxLength
        self.expressionEnabled = expressionEnabled
        self.secretEnabled = secretEnabled
        self.validationDescription = validationDescription
        self.validationHandler = validationHandler
        self.valueGeneratorType = valueGeneratorType
        self.unitString = unitString
        self.commentable = commentable
        self.isVisible = isVisible
        self.preProcessors = preProcessors
        self.isComplex = isComplex

    def __eq__(self, other):
        # Define equality condition
        return self.name == other.name and self.displayName == other.displayName and self.description == other.description and self.type == other.type and self.multiplicity == other.multiplicity and self.searchable == other.searchable and self.editable == other.editable and self.required == other.required and self.formType == other.formType and self.format == other.format and self.isComplex == other.isComplex
    
    def __hash__(self):
        # Hash based on the same attributes used in __eq__
        return hash(self.name, self.type)

class FlexTaxonomyField(FlexMetadataField):
    def __init__(self, id, name, displayName, description, type, multiplicity, searchable, editable, required, formType, format, formatDescription, validation, maxLength, expressionEnabled, secretEnabled, validationDescription, validationHandler, valueGeneratorType, unitString, commentable, isVisible, preProcessors, isComplex, filter, backingStoreType):
        super().__init__(id, name, displayName, description, type, multiplicity, searchable, editable, required, formType, format, formatDescription, validation, maxLength, expressionEnabled, secretEnabled, validationDescription, validationHandler, valueGeneratorType, unitString, commentable, isVisible, preProcessors, isComplex)
        self.filter = filter
        self.backingStoreType = backingStoreType
        
    def __eq__(self, other):
        if not isinstance(other, FlexTaxonomyField):
            return NotImplemented

        # First check equality based on the Parent Class' __eq__ method
        if not super().__eq__(other):
            return False

        # Then check the additional attributes
        # TODO: for filter, add a Taxonomy API query to get the taxonomy name based on it
        # TODO: then, compare both taxonomy names
        return self.backingStoreType == other.backingStoreType

class FlexObjectField(FlexMetadataField):
    def __init__(self, id, name, displayName, description, type, multiplicity, searchable, editable, required, formType, format, formatDescription, validation, maxLength, expressionEnabled, secretEnabled, validationDescription, validationHandler, valueGeneratorType, unitString, commentable, isVisible, preProcessors, isComplex, objectType, classNames, objectTypeId, variantId):
        super().__init__(id, name, displayName, description, type, multiplicity, searchable, editable, required, formType, format, formatDescription, validation, maxLength, expressionEnabled, secretEnabled, validationDescription, validationHandler, valueGeneratorType, unitString, commentable, isVisible, preProcessors, isComplex)
        self.objectType = objectType
        self.classNames = classNames
        self.objectTypeId = objectTypeId
        self.variantId = variantId
        if (objectTypeId):
            self.notype = False
        else:
            self.notype = True

    def __eq__(self, other):
        if not isinstance(other, FlexTaxonomyField):
            return NotImplemented

        # First check equality based on the Parent Class' __eq__ method
        if not super().__eq__(other):
            return False

        # Then check the additional attributes
        # TODO: for objectTypeId, add an object API query to get the UDO name based on it
        # TODO: then, compare both object names
        return self.objectType == other.objectType


class FlexCmClient(FlexApiClient):
    def __init__(self, base_url, username, password):
        super().__init__(base_url, username, password)

    def get_workflow_definition(self, workflowDefinitionName):
        """Get workflow definition."""
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

    def get_metadata_definition(self, metadataDefinitionName):
        """Get metadata definition."""
        endpoint = f"/metadataDefinitions;name={metadataDefinitionName};exactNameMatch=true"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()

            responseJson = response.json()
            totalCount = responseJson["totalCount"]

            if (totalCount == 0):
                raise Exception(f"No metadata definition found with name {metadataDefinitionName}")
            else:
                metadataDefinition = responseJson["metadataDefinitions"][0]
            
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
            responseJson = response.json()

            return self.add_fields(responseJson["definition"])
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
                fieldToAdd = FlexTaxonomyField(field["id"], field["name"], field["displayName"], field["description"], field["type"], multiplicity, field["searchable"], field["editable"], field["required"], field["formType"], field["format"], field["formatDescription"], field["validation"], field["maxLength"], field["expressionEnabled"], field["secretEnabled"], field["validationDescription"], field["validationHandler"], field["valueGeneratorType"], field["unitString"], field["commentable"], field["isVisible"], field["preProcessors"], False, field["filter"], field["backingStoreType"])
            elif (field["type"] == "object"):
                fieldToAdd = FlexObjectField(field["id"], field["name"], field["displayName"], field["description"], field["type"], multiplicity, field["searchable"], field["editable"], field["required"], field["formType"], field["format"], field["formatDescription"], field["validation"], field["maxLength"], field["expressionEnabled"], field["secretEnabled"], field["validationDescription"], field["validationHandler"], field["valueGeneratorType"], field["unitString"], field["commentable"], field["isVisible"], field["preProcessors"], False, field["objectType"], field["classNames"], field["objectTypeId"], field["variantId"])
            else:
                fieldToAdd = FlexMetadataField(field["id"], field["name"], field["displayName"], field["description"], field["type"], multiplicity, field["searchable"], field["editable"], field["required"], field["formType"], field["format"], field["formatDescription"], field["validation"], field["maxLength"], field["expressionEnabled"], field["secretEnabled"], field["validationDescription"], field["validationHandler"], field["valueGeneratorType"], field["unitString"], field["commentable"], field["isVisible"], field["preProcessors"], isComplex)
            
            fieldList.append(fieldToAdd)
            
            if (isComplex):
                fieldList.extend(self.add_fields(field["children"]))

        return fieldList