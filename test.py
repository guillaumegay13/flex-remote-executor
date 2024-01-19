from configurations.metadata_definition import get_metadata_definition_fields
from client.flexCmClient import FlexCmClient
import os

baseUrl = os.environ.get('BASE_URL')
username = os.environ.get('USERNAME')
password = os.environ.get('PASSWORD')

flexCmClient = FlexCmClient(baseUrl, username, password)
fields = get_metadata_definition_fields(flexCmClient, "Video MDA")

## TODO: possibility to add two environments (staging + prod) and compare fields from the same metadata definition between both env.

for field in fields:
    print(field.name)