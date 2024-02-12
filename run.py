import sys
import os
from client.flex_api_client import FlexApiClient
from client.flex_cm_client import FlexCmClient
from actions.action import create_action, push_action_configuration, pull_action_configuration
from actions.job import create_job, update_job, retry_last_job, cancel_job
from actions.file import create_file
from configurations.workflow_migrator import WorfklowMigrator
from configurations.metadata_definition_comparator import MetadataDefinitionComparator
from monitoring.metadata_migration_tracker import MetadataMigrationTracker

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
    #metadata_migration_tracker.get_metadata_migration_jobs("createdFrom=08 Feb 2024 14:40:00")

    # workflow_definition_name = "Publish Asset to Imagen"
    # metadata_migration_tracker.get_metadata_migration_workflows(workflow_definition_name, "createdFrom=12 Feb 2024", True)

    pho_metadata_definition_id = 972
    published_taxon_id = 40107159
    metadata_migration_tracker.get_assets(f"metadataDefinitionId={pho_metadata_definition_id};metadata=publishing-status:{published_taxon_id}", True)


if __name__ == "__main__":
    main()