def get_metadata_definition_fields(FlexCmClient, metadataDefinitionName):

    print("Getting metadata definition...")
    (metadataDefinitionUuid, metadataDefinitionId) = FlexCmClient.get_metadata_definition(metadataDefinitionName)

    print("Getting fields...")
    fields = FlexCmClient.get_metadata_definition_fields(metadataDefinitionId)

    return fields