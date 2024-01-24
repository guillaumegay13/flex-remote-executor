import os
from client.flex_cm_client import FlexCmResource
from objects.flex_objects import FlexCmObject

class WorfklowMigrator:
    def __init__(self, flexCmClient, workflow_definition_name):
        self.flexCmClient = flexCmClient
        self.workflow_definition = self.flexCmClient.get_workflow_definition(workflow_definition_name)
        self.dependancy_list = []
        
    def get_workflow_definition_dependancies(self):
        """Get workflow definition dependancies."""
        workflowDefinitionId = self.workflow_definition.id
        # Dependancy list is a list of FlexCmObject
        # It's the list of all the dependancies to migrate for a workflow definition
        dependancyList = []

        # TODO : get object references instead of workflow references
        # print(f"Getting workflow {workflow_definition.name} references...")
        # objectReferenceList = FlexCmClient.get_workflow_references(workflowDefinitionId)

        """Get workflow structure actions."""
        print(f"Getting workflow {self.workflow_definition.name} structure...")
        actionList = self.flexCmClient.get_workflow_structure(workflowDefinitionId)

        """Get action dependancies for each action of the workflow structure."""
        for action in actionList:
            dependancyList.extend(self.get_action_dependancies(self.flexCmClient, action))

        # TODO: manage the references
        # Add them after the workflow definition ? What about the references dependancies ? Ideally : 1) references dependancies, 2) references.
        
        # Add workflow definition after all its dependancies
        # It is important to keep the correct order
        dependancyList.append(self.workflow_definition)

        # Clean up the duplicates
        uniqueDependancyList = []
        for dependancy in dependancyList:
            if dependancy not in uniqueDependancyList:
                uniqueDependancyList.append(dependancy)

        self.dependancy_list = uniqueDependancyList

    def get_action_dependancies(self, action):
        """Recursively get action dependancies."""
        actionDependancyList = []
        # TODO: add all the cases below
        match action.objectTypeName:
            case "transcode":
                action_configuration = self.flexCmClient.get_object_configuration(action.id, "action")
                # Transcode resource
                execution_resource_instance = action_configuration["instance"]["execution-resource"]
                transcode_resource = FlexCmResource(execution_resource_instance["id"], execution_resource_instance["uuid"], execution_resource_instance["value"], execution_resource_instance["name"], None, execution_resource_instance["type"], "resource", self.flexCmClient.get_resource_subtype(execution_resource_instance["id"]))
                actionDependancyList.append(transcode_resource)
                # Transcode profile
                output_file_list = action_configuration["instance"]["output-file"]
                for output_file in output_file_list:
                    transcoder_profile_instance = output_file["transcoder-profile"]["profile"]
                    transcode_profile = FlexCmObject(transcoder_profile_instance["id"], transcoder_profile_instance["uuid"], transcoder_profile_instance["value"], transcoder_profile_instance["name"], None, transcoder_profile_instance["type"], "profile")
                    actionDependancyList.append(transcode_profile)
                # Output resource
                output_resource_instance = action_configuration["instance"]["destination"]["output-resource"]
                output_resource = FlexCmResource(output_resource_instance["id"], output_resource_instance["uuid"], output_resource_instance["value"], output_resource_instance["name"], None, output_resource_instance["type"], "resource", self.flexCmClient.get_resource_subtype(output_resource_instance["id"]))

                # Check if resource has dependancies, such as Storage Resource or workflow (for inbox/hotfolders)
                for dependancy in self.get_action_dependancies(self.flexCmClient, output_resource):
                    actionDependancyList.append(dependancy)
                actionDependancyList.append(output_resource)
            case "launch":
                action_configuration = self.flexCmClient.get_object_configuration(action.id, "action")
                # Workflow definition
                workflow_definition_instance = action_configuration["instance"]["Workflow"]
                workflow_definition = FlexCmObject(workflow_definition_instance["id"], workflow_definition_instance["uuid"], workflow_definition_instance["value"], workflow_definition_instance["name"], None, workflow_definition_instance["type"], "workflow_definition")
                for dependancy in self.get_action_dependancies(self.flexCmClient, workflow_definition):
                    actionDependancyList.append(dependancy)
                actionDependancyList.append(workflow_definition)
            case "import":
                action_configuration = self.flexCmClient.get_object_configuration(action.id, "action")
                # Workflow definition
                source_resource_instance = action_configuration["instance"]["source-file"]["source"]["source-resource-item"]["source-resource"]
                if not source_resource_instance["isExpression"]:
                    # if isExpression is False, then a resource is mapped
                    source_resource = FlexCmResource(source_resource_instance["id"], source_resource_instance["uuid"], source_resource_instance["value"], source_resource_instance["name"], None, source_resource_instance["type"], "resource", self.flexCmClient.get_resource_subtype(source_resource_instance["id"]))
                    for dependancy in self.get_action_dependancies(self.flexCmClient, source_resource):
                        actionDependancyList.append(dependancy)
                    actionDependancyList.append(source_resource)
                if action_configuration["instance"]["source-file"]["move-file"]["move-target-resource"]:
                    move_resource_instance = action_configuration["instance"]["source-file"]["move-file"]["move-target-resource"]
                    move_resource = FlexCmResource(move_resource_instance["id"], move_resource_instance["uuid"], move_resource_instance["value"], move_resource_instance["name"], None, move_resource_instance["type"], "resource", self.flexCmClient.get_resource_subtype(move_resource_instance["id"]))
                    for dependancy in self.get_action_dependancies(self.flexCmClient, move_resource):
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
                action_configuration = self.flexCmClient.get_object_configuration(action.id, "resource")
                resourceSubType = self.flexCmClient.get_resource_subtype(action.id)
                match resourceSubType:
                    # TODO : continue below ...
                    case "Folder":
                        # Folders have a storage resource dependancy
                        storage_resource_instances = action_configuration["instance"]["Storage Resources"]
                        for storage_resource_instance in storage_resource_instances:                
                            storage_resource = FlexCmResource(storage_resource_instance["Storage Resource"]["id"], storage_resource_instance["Storage Resource"]["uuid"], storage_resource_instance["Storage Resource"]["value"], storage_resource_instance["Storage Resource"]["name"], storage_resource_instance["Storage Resource"]["type"], None, "resource", self.flexCmClient.get_resource_subtype(storage_resource_instance["Storage Resource"]["id"]))
                            actionDependancyList.append(storage_resource)
                    case "Transcode":
                        # pass as there is no dependancies for Transcode resources
                        pass
                    case "Storage":
                        # Storage resources have no dependancy, they are root objects
                        pass
            case "workflow-definition":
                actionDependancyList.extend(self.get_workflow_definition_dependancies(self.flexCmClient, action))
            case _:
                # This error has been added to make sure no dependancy is missing!
                raise Exception(f"action type {action.objectTypeName} is not implemented yet!")
            
        # Add the action object itself AFTER its dependancies have been added!
        # It is crutial to keep this order
        actionDependancyList.append(action)

        # TODO: investigate possibility to use only dependancy_list class attribute instead
        return actionDependancyList

    def create_dependancies_file(self, project_path):
        """Create dependancy files in /src/configurations/ project directory."""
        file_name = self.workflow_definition.name.lower().replace(' ', '_') + ".txt"

        file_path = project_path + '/src/configurations/' + file_name

        # Extract the directory path from the file path
        directory = os.path.dirname(file_path)

        # Create the directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Create new file
        with open(file_path, "w") as file:

            for dependancy in self.dependancy_list:
                file.write(f"{dependancy.name}\n")
                file.write(f"pull --type {dependancy.flexCmName} --uuid {dependancy.uuid}\n")
                file.write(f"add --uuid {dependancy.uuid}\n")
                file.write(f"commit --uuid {dependancy.uuid}\n\n")