import os
from client.flexCmClient import FlexCmObject

def get_workflow_definition_dependancies(FlexCmClient, workflow_definition):

    workflowDefinitionId = workflow_definition.id
    # Dependancy list is a list of FlexCmObject
    # It's the list of all the dependancies to migrate for a workflow definition
    dependancyList = []

    print("Getting workflow references...")
    objectReferenceList = FlexCmClient.get_workflow_references(workflowDefinitionId)

    print("Getting workflow structure...")
    actionList = FlexCmClient.get_workflow_structure(workflowDefinitionId)

    for action in actionList:
        dependancyList.extend(get_action_dependancies(FlexCmClient, action))

        # Add the action once its dependancies have been added
        # It is important to keep the correct order
        dependancyList.append(action)

    # TODO: manage the references
    # Add them after the workflow definition ? What about the references dependancies ? Ideally : 1) references dependancies, 2) references.
    
    # Add workflow definition after all its dependancies
    # It is important to keep the correct order
    dependancyList.append(workflow_definition)

    return dependancyList

def get_action_dependancies(flexCmClient, action):
    actionDependancyList = []
    # TODO: add all the cases below
    match action.objectTypeName:
        case "transcode":
            action_configuration = flexCmClient.get_action_configuration(action.id)
            # Transcode resource
            execution_resource_instance = action_configuration["instance"]["execution-resource"]
            transcode_resource = FlexCmObject(execution_resource_instance["id"], execution_resource_instance["uuid"], execution_resource_instance["value"], execution_resource_instance["name"], None, execution_resource_instance["type"], "resource")
            actionDependancyList.append(transcode_resource)
            # Transcode profile
            output_file_list = action_configuration["instance"]["output-file"]
            for output_file in output_file_list:
                transcoder_profile_instance = output_file["transcoder-profile"]["profile"]
                transcode_profile = FlexCmObject(transcoder_profile_instance["id"], transcoder_profile_instance["uuid"], transcoder_profile_instance["value"], transcoder_profile_instance["name"], None, transcoder_profile_instance["type"], "profile")
                actionDependancyList.append(transcode_profile)
            # Output resource
            output_resource_instance = action_configuration["instance"]["destination"]["output-resource"]
            output_resource = FlexCmObject(output_resource_instance["id"], output_resource_instance["uuid"], output_resource_instance["value"], output_resource_instance["name"], None, output_resource_instance["type"], "action")
            actionDependancyList.append(output_resource)
        case "launch":
            action_configuration = flexCmClient.get_action_configuration(action.id)
            # Workflow definition
            workflow_definition_instance = action_configuration["instance"]["Workflow"]
            workflow_definition = FlexCmObject(workflow_definition_instance["id"], workflow_definition_instance["uuid"], workflow_definition_instance["value"], workflow_definition_instance["name"], None, workflow_definition_instance["type"], "workflow_definition")
            for dependancy in get_workflow_definition_dependancies(flexCmClient, workflow_definition):
                actionDependancyList.append(dependancy)
            actionDependancyList.append(workflow_definition)
        case "import":
            action_configuration = flexCmClient.get_action_configuration(action.id)
            # Workflow definition
            source_resource_instance = action_configuration["instance"]["source-file"]["source"]["source-resource-item"]["source-resource"]
            source_resource = FlexCmObject(source_resource_instance["id"], source_resource_instance["uuid"], source_resource_instance["value"], source_resource_instance["name"], source_resource_instance["type"], "resource")
            actionDependancyList.append(source_resource)
    return actionDependancyList

def create_dependancies_file(project_path, workflow_definition, dependancyList):

    file_name = workflow_definition.name.lower().replace(' ', '_') + ".txt"

    file_path = project_path + '/src/configurations/' + file_name

    # Extract the directory path from the file path
    directory = os.path.dirname(file_path)

    # Create the directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Create new file
    with open(file_path, "w") as file:

        for dependancy in dependancyList:
            file.write(f"pull --type {dependancy.flexCmName} --uuid {dependancy.uuid}\n")
            file.write(f"add --uuid {dependancy.uuid}\n")
            file.write(f"commit --uuid {dependancy.uuid}\n\n")