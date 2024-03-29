import sys
import os
from client.flex_api_client import FlexApiClient
from client.flex_cm_client import FlexCmClient
from actions.action import create_action, push_action_configuration, pull_action_configuration
from actions.job import create_job, push_job_configuration, retry_last_job, cancel_job, update_and_retry_last_job
from actions.file import create_file
from configurations.workflow_migrator import WorfklowMigrator
from configurations.metadata_definition_comparator import MetadataDefinitionComparator

def main():

    file_path = sys.argv[1]    # Path to the current file in IntelliJ
    action = sys.argv[-1]

    actionName = os.path.splitext(os.path.basename(file_path))[0]

    baseUrl = os.environ.get('FRE_SOURCE_BASE_URL')
    username = os.environ.get('FRE_SOURCE_USERNAME')
    password = os.environ.get('FRE_SOURCE_PASSWORD')

    flexApiClient = FlexApiClient(baseUrl, username, password)

    # Dynamically get the account ID
    accountName = baseUrl.replace('https://', '').split('.')[0]
    accountId = flexApiClient.get_account_id(accountName)

    match action:
        case "create_action":
            create_action(flexApiClient, file_path, actionName, accountId)
        case "push_action_configuration":
            push_action_configuration(flexApiClient, file_path)
        case "pull_action_configuration":
            pull_action_configuration(flexApiClient, file_path)
        case "create_job":
            create_job(flexApiClient, file_path)
        case "update_job":
            push_job_configuration(flexApiClient, file_path)
        case "retry_last_job":
            retry_last_job(flexApiClient, file_path)
        case "update_and_retry_last_job":
            update_and_retry_last_job(flexApiClient, file_path)
        case "create_file":
            className = sys.argv[2]
            project_path = file_path
            if (len(sys.argv) == 5):
                folder_name = sys.argv[3]
                create_file(project_path, className, folder_name)
            else:
                create_file(project_path, className)
        case "cancel_job":
            cancel_job(flexApiClient, file_path)
        case "get_workflow_dependancies":
            defaultArgLength = 3
            if (len(sys.argv) == defaultArgLength):
                raise Exception("No workflow definition name has been specified!")
            workflowDefinitionNameList = []
            for i in range(defaultArgLength, len(sys.argv)):
                workflowDefinitionNameList.append(sys.argv[i-1])
            workflow_definition_name = " ".join(workflowDefinitionNameList)
            project_path = file_path
            flex_cm_client = FlexCmClient(baseUrl, username, password)
            workflowMigrator = WorfklowMigrator(flex_cm_client)
            workflow_definition = flex_cm_client.get_workflow_definition(workflow_definition_name)
            dependency_list = workflowMigrator.get_workflow_definition_dependencies(workflow_definition)
            dependency_list.extend(workflowMigrator.get_workflow_references(workflow_definition))
            workflowMigrator.create_dependencies_file(project_path, workflow_definition, dependency_list)
        case "compare_metadata_definitions":
            defaultArgLength = 3
            if (len(sys.argv) == defaultArgLength):
                raise Exception("No metadata definition name has been specified!")
            metadataDefinitionNameList = []
            for i in range(defaultArgLength, len(sys.argv)):
                metadataDefinitionNameList.append(sys.argv[i-1])
            metadataDefinitionName = " ".join(metadataDefinitionNameList)
            
            # Target environment
            target_base_url = os.environ.get('FRE_TARGET_BASE_URL')
            target_username = os.environ.get('FRE_TARGET_USERNAME')
            target_password = os.environ.get('FRE_TARGET_PASSWORD')

            metadataDefinitionComparator = MetadataDefinitionComparator(baseUrl, username, password, target_base_url, target_username, target_password)
            metadataDefinitionComparator.compare_metadata_definitions(metadataDefinitionName)
        case _:
            raise Exception("IntelliJ Action not implemented yet.")

if __name__ == "__main__":
    main()