import os

def get_workflow_definition_dependancies(FlexCmClient, workflowDefinitionName):

    print("Getting workflow definition...")
    (workflowDefinitionUuid, workflowDefinitionId) = FlexCmClient.get_workflow_definition(workflowDefinitionName)

    print("Getting workflow references...")
    objectReferenceList = FlexCmClient.get_workflow_references(workflowDefinitionId)

    print("Getting workflow structure...")
    actionList = FlexCmClient.get_workflow_structure(workflowDefinitionId)

    return (workflowDefinitionUuid, objectReferenceList, actionList)

def create_dependancies_file(project_path, workflowDefinitionName, workflowDefinitionUuid, objectReferenceList, actionList):

    file_name = workflowDefinitionName.lower().replace(' ', '_') + ".txt"

    file_path = project_path.split('src')[0] + 'src/configurations/' + file_name

    # Extract the directory path from the file path
    directory = os.path.dirname(file_path)

    # Create the directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Create new file
    with open(file_path, "w") as file:
        file.write(f"references :\n\n")
        for objectReference in objectReferenceList:
            file.write(f"pull --type {objectReference.objectTypeName.lower().replace(' ', '-')} --uuid {objectReference.uuid}\n")
            file.write(f"add --uuid {objectReference.uuid}\n")
            file.write(f"commit --uuid {objectReference.uuid}\n\n")

        file.write(f"actions :\n\n")
        for action in actionList:
            file.write(f"pull --type action --uuid {action.uuid}\n")
            file.write(f"add --uuid {action.uuid}\n")
            file.write(f"commit --uuid {action.uuid}\n\n")

        file.write(f"workflowDefinition :\n\n")
        file.write(f"pull --type workflow_definition --uuid {workflowDefinitionUuid}\n")
        file.write(f"add --uuid {workflowDefinitionUuid}\n")
        file.write(f"commit --uuid {workflowDefinitionUuid}\n")