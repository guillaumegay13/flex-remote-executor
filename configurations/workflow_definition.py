import os
from client.flexCmClient import FlexCmObject, FlexCmResource

def get_workflow_definition_dependancies(FlexCmClient, workflow_definition):

    workflowDefinitionId = workflow_definition.id
    # Dependancy list is a list of FlexCmObject
    # It's the list of all the dependancies to migrate for a workflow definition
    dependancyList = []

    # TODO : get object references instead of workflow references
    # print(f"Getting workflow {workflow_definition.name} references...")
    # objectReferenceList = FlexCmClient.get_workflow_references(workflowDefinitionId)

    print(f"Getting workflow {workflow_definition.name} structure...")
    actionList = FlexCmClient.get_workflow_structure(workflowDefinitionId)

    for action in actionList:
        dependancyList.extend(get_action_dependancies(FlexCmClient, action))

    # TODO: manage the references
    # Add them after the workflow definition ? What about the references dependancies ? Ideally : 1) references dependancies, 2) references.
    
    # Add workflow definition after all its dependancies
    # It is important to keep the correct order
    dependancyList.append(workflow_definition)

    # Clean up the duplicates
    uniqueDependancyList = []
    for dependancy in dependancyList:
        if dependancy not in uniqueDependancyList:
            uniqueDependancyList.append(dependancy)

    return uniqueDependancyList

def get_action_dependancies(flexCmClient, action):
    actionDependancyList = []
    # TODO: add all the cases below
    match action.objectTypeName:
        case "transcode":
            action_configuration = flexCmClient.get_object_configuration(action.id, "action")
            # Transcode resource
            execution_resource_instance = action_configuration["instance"]["execution-resource"]
            transcode_resource = FlexCmResource(execution_resource_instance["id"], execution_resource_instance["uuid"], execution_resource_instance["value"], execution_resource_instance["name"], None, execution_resource_instance["type"], "resource", flexCmClient.get_resource_subtype(execution_resource_instance["id"]))
            actionDependancyList.append(transcode_resource)
            # Transcode profile
            output_file_list = action_configuration["instance"]["output-file"]
            for output_file in output_file_list:
                transcoder_profile_instance = output_file["transcoder-profile"]["profile"]
                transcode_profile = FlexCmObject(transcoder_profile_instance["id"], transcoder_profile_instance["uuid"], transcoder_profile_instance["value"], transcoder_profile_instance["name"], None, transcoder_profile_instance["type"], "profile")
                actionDependancyList.append(transcode_profile)
            # Output resource
            output_resource_instance = action_configuration["instance"]["destination"]["output-resource"]
            output_resource = FlexCmResource(output_resource_instance["id"], output_resource_instance["uuid"], output_resource_instance["value"], output_resource_instance["name"], None, output_resource_instance["type"], "resource", flexCmClient.get_resource_subtype(output_resource_instance["id"]))

            # Check if resource has dependancies, such as Storage Resource or workflow (for inbox/hotfolders)
            for dependancy in get_action_dependancies(flexCmClient, output_resource):
                actionDependancyList.append(dependancy)
            actionDependancyList.append(output_resource)
        case "launch":
            action_configuration = flexCmClient.get_object_configuration(action.id, "action")
            # Workflow definition
            workflow_definition_instance = action_configuration["instance"]["Workflow"]
            workflow_definition = FlexCmObject(workflow_definition_instance["id"], workflow_definition_instance["uuid"], workflow_definition_instance["value"], workflow_definition_instance["name"], None, workflow_definition_instance["type"], "workflow_definition")
            for dependancy in get_action_dependancies(flexCmClient, workflow_definition):
                actionDependancyList.append(dependancy)
            actionDependancyList.append(workflow_definition)
        case "import":
            action_configuration = flexCmClient.get_object_configuration(action.id, "action")
            # Workflow definition
            source_resource_instance = action_configuration["instance"]["source-file"]["source"]["source-resource-item"]["source-resource"]
            if not source_resource_instance["isExpression"]:
                # if isExpression is False, then a resource is mapped
                source_resource = FlexCmResource(source_resource_instance["id"], source_resource_instance["uuid"], source_resource_instance["value"], source_resource_instance["name"], None, source_resource_instance["type"], "resource", flexCmClient.get_resource_subtype(source_resource_instance["id"]))
                for dependancy in get_action_dependancies(flexCmClient, source_resource):
                    actionDependancyList.append(dependancy)
                actionDependancyList.append(source_resource)
            if action_configuration["instance"]["source-file"]["move-file"]["move-target-resource"]:
                move_resource_instance = action_configuration["instance"]["source-file"]["move-file"]["move-target-resource"]
                move_resource = FlexCmResource(move_resource_instance["id"], move_resource_instance["uuid"], move_resource_instance["value"], move_resource_instance["name"], None, move_resource_instance["type"], "resource", flexCmClient.get_resource_subtype(move_resource_instance["id"]))
                for dependancy in get_action_dependancies(flexCmClient, move_resource):
                    actionDependancyList.append(dependancy)
                actionDependancyList.append(move_resource)
        case "script":
            pass
        case "decision":
            pass
        case "message":
            pass
        case "wait":
            pass
        case "resource":
            action_configuration = flexCmClient.get_object_configuration(action.id, "resource")
            resourceSubType = flexCmClient.get_resource_subtype(action.id)
            match resourceSubType:
                # TODO : continue below ...
                case "Folder":
                    # Folders have a storage resource dependancy
                    storage_resource_instances = action_configuration["instance"]["Storage Resources"]
                    for storage_resource_instance in storage_resource_instances:                
                        storage_resource = FlexCmResource(storage_resource_instance["Storage Resource"]["id"], storage_resource_instance["Storage Resource"]["uuid"], storage_resource_instance["Storage Resource"]["value"], storage_resource_instance["Storage Resource"]["name"], storage_resource_instance["Storage Resource"]["type"], None, "resource", flexCmClient.get_resource_subtype(storage_resource_instance["Storage Resource"]["id"]))
                        actionDependancyList.append(storage_resource)
                    # TODO : add also the Folder resource itself
                case "Transcode":
                    # pass as there is no dependancies for Transcode resources
                    pass
                case "Storage":
                    # Storage resources have no dependancy, they are root objects
                    pass
        case "workflow-definition":
            actionDependancyList.extend(get_workflow_definition_dependancies(flexCmClient, action))
        case _:
            # This error has been added to make sure no dependancy is missing!
            raise Exception(f"action type {action.objectTypeName} is not implemented yet!")
        
    # Add the action object itself AFTER its dependancies have been added!
    # It is crutial to keep this order
    actionDependancyList.append(action)
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
            file.write(f"{dependancy.name}\n")
            file.write(f"pull --type {dependancy.flexCmName} --uuid {dependancy.uuid}\n")
            file.write(f"add --uuid {dependancy.uuid}\n")
            file.write(f"commit --uuid {dependancy.uuid}\n\n")