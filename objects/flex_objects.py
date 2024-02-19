class FlexObject():
    def __init__(self, id, uuid, name, displayName, objectTypeId, objectTypeName):
        self.id = id
        self.uuid = uuid
        self.name = name
        self.displayName = displayName
        self.objectTypeId = objectTypeId
        self.objectTypeName = objectTypeName

class FlexJob(FlexObject):
    def __init__(self, id, name, status, start = None, end = None, owner = None, error = None):
        self.id = id
        self.name = name
        self.status = status
        self.start = start
        self.end = end
        self.owner = owner
        self.error = error

class FlexAsset(FlexObject):
    def __init__(self, id, uuid, name, displayName, objectTypeId, objectTypeName, originalFileName = None):
        super().__init__(id, uuid, name, displayName, objectTypeId, objectTypeName)
        self.originalFileName = originalFileName

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
    
class FlexInstance(FlexObject):
    def __init__(self, id, uuid, name, displayName, objectTypeId, objectTypeName, status, scheduled, created, asset_id = None, asset_name = None, asset_type = None):
        super().__init__(id, uuid, name, displayName, objectTypeId, objectTypeName)
        self.status = status
        self.scheduled = scheduled
        self.created = created
        self.asset_id = asset_id
        self.asset_name = asset_name
        self.asset_type = asset_type
