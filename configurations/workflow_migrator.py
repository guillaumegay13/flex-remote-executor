import os
from client.flex_cm_client import FlexCmResource
from objects.flex_objects import FlexCmObject

class WorfklowMigrator:
    def __init__(self, flex_cm_client):
        self.flex_cm_client = flex_cm_client

    def get_workflow_definition_dependencies(self, workflow_definition):
        """Get workflow definition dependencies."""
        workflow_definition_id = workflow_definition.id
        # Dependancy list is a list of FlexCmObject
        # It's the list of all the dependencies to migrate for a workflow definition
        full_dependency_list = []

        """Get workflow structure actions."""
        print(f"Getting workflow {workflow_definition.name} structure...")
        actionList = self.flex_cm_client.get_workflow_structure(workflow_definition_id)

        """Get action dependencies for each action of the workflow structure."""
        for action in actionList:
            full_dependency_list.extend(self.get_action_dependencies(action))
        
        # Add workflow definition after all its dependencies
        # It is important to keep the correct order
        full_dependency_list.append(workflow_definition)

        # Clean up the duplicates
        unique_dependency_list = []
        for dependency in full_dependency_list:
            if dependency not in unique_dependency_list:
                unique_dependency_list.append(dependency)
        
        return unique_dependency_list

    def get_action_dependencies(self, action):
        """Recursively get action dependencies."""
        action_dependency_list = []
        # TODO: add all the cases below
        match action.objectTypeName:
            case "transcode" | "create-proxy":
                action_configuration = self.flex_cm_client.get_object_configuration(action.id, "action")
                # Transcode resource
                execution_resource_instance = action_configuration["instance"]["execution-resource"]
                transcode_resource = FlexCmResource(execution_resource_instance["id"], execution_resource_instance["uuid"], execution_resource_instance["value"], execution_resource_instance["name"], None, execution_resource_instance["type"], "resource", self.flex_cm_client.get_resource_subtype(execution_resource_instance["id"]))
                action_dependency_list.append(transcode_resource)
                # Transcode profile
                if action.objectTypeName == "transcode":
                    output_file_list = action_configuration["instance"]["output-file"]
                    for output_file in output_file_list:
                        transcoder_profile_instance = output_file["transcoder-profile"]["profile"]
                        transcode_profile = FlexCmObject(transcoder_profile_instance["id"], transcoder_profile_instance["uuid"], transcoder_profile_instance["value"], transcoder_profile_instance["name"], None, transcoder_profile_instance["type"], "profile")
                        action_dependency_list.append(transcode_profile)
                elif action.objectTypeName == "create-proxy":
                        transcoder_profile_instance = action_configuration["instance"]["transcoder-profile"]["profile"]
                        transcode_profile = FlexCmObject(transcoder_profile_instance["id"], transcoder_profile_instance["uuid"], transcoder_profile_instance["value"], transcoder_profile_instance["name"], None, transcoder_profile_instance["type"], "profile")
                        action_dependency_list.append(transcode_profile)
                # Output resource
                output_resource_instance = action_configuration["instance"]["destination"]["output-resource"]
                output_resource = FlexCmResource(output_resource_instance["id"], output_resource_instance["uuid"], output_resource_instance["value"], output_resource_instance["name"], None, output_resource_instance["type"], "resource", self.flex_cm_client.get_resource_subtype(output_resource_instance["id"]))

                # Check if resource has dependencies, such as Storage Resource or workflow (for inbox/hotfolders)
                for dependency in self.get_action_dependencies(output_resource):
                    action_dependency_list.append(dependency)
                action_dependency_list.append(output_resource)
            case "launch":
                action_configuration = self.flex_cm_client.get_object_configuration(action.id, "action")
                action_configuration_instance = action_configuration["instance"]
                # Workflow definition
                if "Workflow" in action_configuration_instance:
                    workflow_definition_instance = action_configuration["instance"]["Workflow"]
                    workflow_definition_to_append = FlexCmObject(workflow_definition_instance["id"], workflow_definition_instance["uuid"], workflow_definition_instance["value"], workflow_definition_instance["name"], None, workflow_definition_instance["type"], "workflow_definition")
                    for dependency in self.get_action_dependencies(workflow_definition_to_append):
                        action_dependency_list.append(dependency)
                    action_dependency_list.append(workflow_definition_to_append)
                elif "workflows" in action_configuration_instance and len(action_configuration_instance["workflows"]) > 0:
                    for workflow in action_configuration_instance["workflows"]:
                        workflow_definition_instance = workflow["Workflow"]
                        workflow_definition_to_append = FlexCmObject(workflow_definition_instance["id"], workflow_definition_instance["uuid"], workflow_definition_instance["value"], workflow_definition_instance["name"], None, workflow_definition_instance["type"], "workflow_definition")
                        for dependency in self.get_action_dependencies(workflow_definition_to_append):
                            action_dependency_list.append(dependency)
                        action_dependency_list.append(workflow_definition_to_append)
            case "import" | "re-import":
                action_configuration = self.flex_cm_client.get_object_configuration(action.id, "action")
                # Workflow definition
                source_resource_instance = action_configuration["instance"]["source-file"]["source"]["source-resource-item"]["source-resource"]
                if "isExpression" not in source_resource_instance or not source_resource_instance["isExpression"]:
                    # if isExpression is False, then a resource is mapped
                    source_resource = FlexCmResource(source_resource_instance["id"], source_resource_instance["uuid"], source_resource_instance["value"], source_resource_instance["name"], None, source_resource_instance["type"], "resource", self.flex_cm_client.get_resource_subtype(source_resource_instance["id"]))
                    for dependency in self.get_action_dependencies(source_resource):
                        action_dependency_list.append(dependency)
                    action_dependency_list.append(source_resource)
                if "move-file" in action_configuration["instance"]["source-file"]:
                    if action_configuration["instance"]["source-file"]["move-file"]["move-target-resource"] and "id" in action_configuration["instance"]["source-file"]["move-file"]["move-target-resource"]:
                        print(action_configuration)
                        move_resource_instance = action_configuration["instance"]["source-file"]["move-file"]["move-target-resource"]
                        move_resource = FlexCmResource(move_resource_instance["id"], move_resource_instance["uuid"], move_resource_instance["value"], move_resource_instance["name"], None, move_resource_instance["type"], "resource", self.flex_cm_client.get_resource_subtype(move_resource_instance["id"]))
                        for dependency in self.get_action_dependencies(move_resource):
                            action_dependency_list.append(dependency)
                        action_dependency_list.append(move_resource)
            case "script":
                pass
            case "decision":
                pass
            case "message":
                pass
            case "wait":
                pass
            case "resource":
                action_configuration = self.flex_cm_client.get_object_configuration(action.id, "resource")
                resourceSubType = self.flex_cm_client.get_resource_subtype(action.id)
                match resourceSubType:
                    # TODO : continue below ...
                    case "Folder":
                        # Folders have a storage resource dependency
                        storage_resource_instances = action_configuration["instance"]["Storage Resources"]
                        for storage_resource_instance in storage_resource_instances:                
                            storage_resource = FlexCmResource(storage_resource_instance["Storage Resource"]["id"], storage_resource_instance["Storage Resource"]["uuid"], storage_resource_instance["Storage Resource"]["value"], storage_resource_instance["Storage Resource"]["name"], None, storage_resource_instance["Storage Resource"]["type"], "resource", self.flex_cm_client.get_resource_subtype(storage_resource_instance["Storage Resource"]["id"]))
                            action_dependency_list.append(storage_resource)
                    case "Transcode":
                        # pass as there is no dependencies for Transcode resources
                        pass
                    case "Storage":
                        # Storage resources have no dependency, they are root objects
                        pass
                    case "Process":
                        # Process is FSP or FFP resource
                        # Process resources have no dependency, they are root objects
                        pass
            case "workflow-definition":
                action_dependency_list.extend(self.get_workflow_definition_dependencies(action))
            case "move":
                action_configuration = self.flex_cm_client.get_object_configuration(action.id, "action")
                instance = action_configuration["instance"]
                if "folder-resource" in instance:
                    folder_resource_instance = action_configuration["instance"]["folder-resource"]
                    folder_resource = FlexCmResource(folder_resource_instance["id"], folder_resource_instance["uuid"], folder_resource_instance["value"], folder_resource_instance["name"], None, folder_resource_instance["type"], "resource", "Folder")
                    action_dependency_list.extend(self.get_action_dependencies(folder_resource))
            case "purge":
                pass
            case "rename":
                pass
            case "modify-relationship":
                pass
            case "restore" | "extract" | "archive":
                action_configuration = self.flex_cm_client.get_object_configuration(action.id, "action")
                instance = action_configuration["instance"]
                if "execution-resource" in instance:
                    execution_resource_instance = instance["execution-resource"]
                    execution_resource = FlexCmResource(execution_resource_instance["id"], execution_resource_instance["uuid"], execution_resource_instance["value"], execution_resource_instance["name"], None, execution_resource_instance["type"], "resource", "Process")
                    action_dependency_list.extend(self.get_action_dependencies(execution_resource))
            case _:
                # This error has been added to make sure no dependency is missing!
                raise Exception(f"action type {action.objectTypeName} is not implemented yet!")
            
        # Add the action object itself AFTER its dependencies have been added!
        # It is crutial to keep this order
        action_dependency_list.append(action)

        return action_dependency_list
    
    """
    def get_object_references(self, object):
        object_id = object.id
        return self.flex_cm_client.get_object_references(object_id)
    """
    
    def get_workflow_references(self, worfklow_definition):
        """Get workflow references."""
        reference_list = []
        workflow_definition_id = worfklow_definition.id
        # Add the workflow references in the dependency list
        workflow_reference_list = self.flex_cm_client.get_workflow_references(workflow_definition_id)
        for flex_object in workflow_reference_list:
            # TODO: recursively get references, without going too deep
            """
            if flex_object.objectTypeName != "workflow-definition":
                reference_list.extend(self.get_object_references(flex_object))
            """
            reference_list.append(flex_object)

        return reference_list

    def create_dependencies_file(self, project_path, workflow_definition, dependency_list):
        """Create dependency files in /src/configurations/ project directory."""
        file_name = workflow_definition.name.lower().replace(' ', '_') + ".txt"

        file_path = project_path + '/src/configurations/' + file_name

        # Extract the directory path from the file path
        directory = os.path.dirname(file_path)

        # Create the directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Create new file
        with open(file_path, "w") as file:

            for index, dependency in enumerate(dependency_list):
                file.write(f"{dependency.name}\n")
                file.write(f"pull --type {dependency.flexCmName} --uuid {dependency.uuid}\n")
                file.write(f"add --uuid {dependency.uuid}\n")
                file.write(f"commit --uuid {dependency.uuid}\n\n")
                # If the dependency is the actual workflow definition and it's not the last object of the dependency list, meaning there are references
                if dependency.uuid == workflow_definition.uuid and index != len(dependency_list) - 1:
                    file.write("\nReferences (optional): \n\n")