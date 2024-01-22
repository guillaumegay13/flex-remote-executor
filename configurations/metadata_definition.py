import os

def get_metadata_definition_fields(FlexCmClient, metadataDefinitionName):

    print("Getting metadata definition...")
    (metadataDefinitionUuid, metadataDefinitionId) = FlexCmClient.get_metadata_definition(metadataDefinitionName)

    print("Getting fields...")
    fields = FlexCmClient.get_metadata_definition_fields(metadataDefinitionId)

    return fields

"""
def create_fields_file(FlexCmClient, metadataDefinitionName):

    print("Getting metadata definition...")
    (metadataDefinitionUuid, metadataDefinitionId) = FlexCmClient.get_metadata_definition(metadataDefinitionName)

    print("Getting fields...")
    fields = FlexCmClient.get_metadata_definition_fields(metadataDefinitionId)

    file_name = metadataDefinitionName.lower().replace(' ', '_') + ".txt"

    baseUrl = os.environ.get('BASE_URL')

    # Extract the directory path from the file path
    directory = os.path.dirname(baseUrl.replace('https://', '').replace('/api', ''))

    # Create the directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Create new file
    with open(f"{directory}/{file_name}", "w") as file:
"""
        