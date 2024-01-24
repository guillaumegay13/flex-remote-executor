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

class FlexCmObject(FlexObject):
    def __init__(self, id, uuid, name, displayName, objectTypeId, objectTypeName, flexCmName):
        super().__init__(id, uuid, name, displayName, objectTypeId, objectTypeName)
        self.flexCmName = flexCmName

class FlexCmResource(FlexCmObject):
    def __init__(self, id, uuid, name, displayName, objectTypeId, objectTypeName, flexCmName, resourceSubType):
        super().__init__(id, uuid, name, displayName, objectTypeId, objectTypeName, flexCmName)
        self.resourceSubType = resourceSubType

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

        # attributes used for comparison
        self.attributeNames = ("name", "displayName", "description", "type", "multiplicity", "searchable", "editable", "required", "formType", "format", "isComplex")
        self.attributes = (name, displayName, description, type, multiplicity, searchable, editable, required, formType, format, isComplex)
        self.attributesLength = len(self.attributes)

    def __eq__(self, other):
        # Define equality condition
        # Compare tuples
        return (self.name, self.displayName, self.description, self.type, self.multiplicity, self.searchable, self.editable, self.required, self.formType, self.format, self.isComplex) == (other.name, other.displayName, other.description, other.type, other.multiplicity, other.searchable, other.editable, other.required, other.formType, other.format, other.isComplex)
    
    def __hash__(self):
        # Hash based on the same attributes used in __eq__
        return hash(self.name, self.displayName, self.description, self.type, self.multiplicity, self.searchable, self.editable, self.required, self.formType, self.format, self.isComplex)

class FlexTaxonomyField(FlexMetadataField):
    def __init__(self, id, name, displayName, description, type, multiplicity, searchable, editable, required, formType, format, formatDescription, validation, maxLength, expressionEnabled, secretEnabled, validationDescription, validationHandler, valueGeneratorType, unitString, commentable, isVisible, preProcessors, isComplex, filter, backingStoreType, taxonomyName):
        super().__init__(id, name, displayName, description, type, multiplicity, searchable, editable, required, formType, format, formatDescription, validation, maxLength, expressionEnabled, secretEnabled, validationDescription, validationHandler, valueGeneratorType, unitString, commentable, isVisible, preProcessors, isComplex)

        # filter is the taxonomy ID
        self.filter = filter
        self.backingStoreType = backingStoreType
        self.taxonomyName = taxonomyName

        # attributes used for comparison
        self.attributeNames = ("name", "displayName", "description", "type", "multiplicity", "searchable", "editable", "required", "formType", "format", "isComplex", "backingStoreType", "taxonomyName")
        self.attributes = (name, displayName, description, type, multiplicity, searchable, editable, required, formType, format, isComplex, backingStoreType, taxonomyName)
        self.attributesLength = len(self.attributes)

        
    def __eq__(self, other):
        if not isinstance(other, FlexTaxonomyField):
            return NotImplemented

        # check equality based on the Parent Class' __eq__ method
        if not super().__eq__(other):
            return False

        # check for additionnal attributes
        return (self.backingStoreType, self.taxonomyName) == (other.backingStoreType, other.taxonomyName)

class FlexObjectField(FlexMetadataField):
    def __init__(self, id, name, displayName, description, type, multiplicity, searchable, editable, required, formType, format, formatDescription, validation, maxLength, expressionEnabled, secretEnabled, validationDescription, validationHandler, valueGeneratorType, unitString, commentable, isVisible, preProcessors, isComplex, objectType, classNames, objectTypeId, variantId, objectTypeName, objectTypeDisplayName, objectTypePluralName):
        super().__init__(id, name, displayName, description, type, multiplicity, searchable, editable, required, formType, format, formatDescription, validation, maxLength, expressionEnabled, secretEnabled, validationDescription, validationHandler, valueGeneratorType, unitString, commentable, isVisible, preProcessors, isComplex)
        self.objectType = objectType
        self.classNames = classNames
        self.objectTypeId = objectTypeId
        self.variantId = variantId
        if (objectTypeId):
            self.notype = False
        else:
            self.notype = True
        self.objectTypeName = objectTypeName
        self.objectTypeDisplayName = objectTypeDisplayName
        self.objectTypePluralName = objectTypePluralName

        # attributes used for comparison
        self.attributeNames = ("name", "displayName", "description", "type", "multiplicity", "searchable", "editable", "required", "formType", "format", "isComplex", "objectType", "objectTypeName", "objectTypeDisplayName", "objectTypePluralName")
        self.attributes = (name, displayName, description, type, multiplicity, searchable, editable, required, formType, format, isComplex, objectType, objectTypeName, objectTypeDisplayName, objectTypePluralName)
        self.attributesLength = len(self.attributes)


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
            
            workflow_definition = FlexCmObject(workflowDefinition["id"], workflowDefinition["uuid"], workflowDefinition["name"], workflowDefinition["displayName"], workflowDefinition["objectType"]["id"], workflowDefinition["objectType"]["name"], "worfklow_definition")

            return workflow_definition

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
            responseJson = response.json()

            if "errors" in responseJson:
                raise Exception(responseJson["errors"]["error"])

            return responseJson["name"]
        except requests.RequestException as e:
            raise Exception(e)
        
    def get_object_type_names(self, objectTypeId):
        """Get object type."""
        endpoint = f"/objectTypes/{objectTypeId}"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            responseJson = response.json()

            if "errors" in responseJson:
                raise Exception(responseJson["errors"]["error"])

            return (responseJson["name"], responseJson["displayName"], responseJson["pluralName"])
        except requests.RequestException as e:
            raise Exception(e)