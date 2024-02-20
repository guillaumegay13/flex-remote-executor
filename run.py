import sys
import os
from client.flex_api_client import FlexApiClient
from client.flex_cm_client import FlexCmClient
from actions.action import create_action, push_action_configuration, pull_action_configuration
from actions.job import create_job, push_job_configuration, retry_last_job, cancel_job
from actions.file import create_file
from configurations.workflow_migrator import WorfklowMigrator
from configurations.metadata_definition_comparator import MetadataDefinitionComparator
from monitoring.metadata_migration_tracker import MetadataMigrationTracker
import time

def main():

    baseUrl = os.environ.get('FRE_SOURCE_BASE_URL')
    username = os.environ.get('FRE_SOURCE_USERNAME')
    password = os.environ.get('FRE_SOURCE_PASSWORD')

    #metadataDefinitionName = "Photo  PHO"
            
    # Target environment
    # target_base_url = os.environ.get('FRE_TARGET_BASE_URL')
    # target_username = os.environ.get('FRE_TARGET_USERNAME')
    #target_password = os.environ.get('FRE_TARGET_PASSWORD')

    # metadataDefinitionComparator = MetadataDefinitionComparator(baseUrl, username, password, target_base_url, target_username, target_password)
    # metadataDefinitionComparator.compare_metadata_definitions(metadataDefinitionName)

    flex_api_client = FlexApiClient(baseUrl, username, password)

    metadata_migration_tracker = MetadataMigrationTracker(flex_api_client)
    #metadata_migration_tracker.get_metadata_migration_jobs("parse-rs2i-xml", "createdFrom=08 Feb 2024 14:40:00")

    # workflow_definition_name = "Publish Asset to Imagen"
    # metadata_migration_tracker.get_metadata_migration_workflows(workflow_definition_name, "createdFrom=12 Feb 2024", True)


    # for job_id in job_id_list_to_retry:
    #     flex_api_client.retry_job(job_id)

    # extract_published_assets(metadata_migration_tracker)

    # extract_workflows_assets(metadata_migration_tracker, "RS2i Metadata Migration", "status=Completed;createdFrom=18 Feb 2024")

    # extract_failed_migration_workflow(metadata_migration_tracker, f"createdFrom=17 Feb 2024;createdTo=18 Feb 2024;status=Failed")

    # extract_workflows_assets(metadata_migration_tracker, "Publish Asset to Imagen", "status=Completed")

    # metadata_migration_tracker.get_metadata_migration_errors(workflow_definition_name, filters, errors)

    """
    script_path = "/mnt/c/Users/ggay/Documents/Projects/IOC/ioc/src/main/groovy/RS2iMetadataMigration/ParseXML.groovy"
    errors = ["No UDO found in Flex with ITM ID '366861' for authorised-use"]

    retry_failed_jobs_from_workflow(metadata_migration_tracker, flex_api_client, "RS2i Metadata Migration", f"createdFrom=19 Feb 2024 12:00:00;status=Failed", errors, script_path)
    """

    # cancel_failed_jobs(metadata_migration_tracker, flex_api_client, "rs2i-xml-import", "status=Failed;createdFrom=08 Feb 2024", ["No valid source file location specified"])

    # extract_published_assets(metadata_migration_tracker)

    # metadata_migration_tracker.get_jobs_errors("rs2i-xml-import", "status=Failed;createdFrom=08 Feb 2024")

    metadata_migration_tracker.get_assets_full("variant=MDA;metadataDefinitionId=884;metadata=archive-tier:44097265")

def extract_published_assets(metadata_migration_tracker):
    pho_metadata_definition_id = 972
    published_taxon_id = 40107159
    metadata_migration_tracker.get_assets(f"metadataDefinitionId={pho_metadata_definition_id};metadata=publishing-status:{published_taxon_id}", False)

def extract_workflows_assets(metadata_migration_tracker, workflow_definition_name, filters):
    metadata_migration_tracker.get_metadata_migration_workflows(workflow_definition_name, filters)

def extract_failed_migration_workflow(metadata_migration_tracker, filters):
    workflow_definition_name = "RS2i Metadata Migration"
    metadata_migration_tracker.get_metadata_migration_workflows(workflow_definition_name, filters)

def retry_failed_jobs_from_workflow(metadata_migration_tracker, flex_api_client, workflow_definition_name, filters = None, errors = None, script_path = None):
    job_id_list_to_retry = metadata_migration_tracker.get_metadata_migration_errors(workflow_definition_name, filters, errors)

    print(f"Number of jobs to retry : {len(job_id_list_to_retry)}")

    for job_id in job_id_list_to_retry:
        push_job_configuration(flex_api_client, script_path, job_id)
        flex_api_client.retry_job(job_id)
        time.sleep(10)

def cancel_failed_jobs(metadata_migration_tracker, flex_api_client, action_name, filters = None, errors = None):
    job_id_list_to_cancel = metadata_migration_tracker.get_jobs_errors(action_name, filters, errors)

    print(f"Number of jobs to cancel : {len(job_id_list_to_cancel)}")

    for job_id in job_id_list_to_cancel:
        try:
            cancel_job(flex_api_client, None, job_id)
        except Exception as e:
            print(f"Unable to cancel job {job_id} : ", e)
        time.sleep(1)


if __name__ == "__main__":
    main()