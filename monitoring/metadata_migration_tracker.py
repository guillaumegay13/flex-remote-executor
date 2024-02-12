import pandas as pd
from datetime import datetime
import os

class MetadataMigrationTracker:
    def __init__(self, flex_api_client):
        self.flex_api_client = flex_api_client
        self.create_empty_directory('exports')

    def create_empty_directory(self, directory_path):
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

    def get_metadata_migration_jobs(self, filters = None):
        action_name = "parse-rs2i-xml"
        action_id = self.flex_api_client.get_action_id(action_name)
        if filters:
            filters += f"actionId={action_id}"
        else: 
            filters = f"actionId={action_id}"
        job_list = self.flex_api_client.get_jobs_by_filter(filters)

        data = [{'id': job.id, 'status': job.status, 'created': job.created} for job in job_list]

        df = pd.DataFrame(data)

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

        filename = f"{action_name}_{timestamp}.csv"
        df.to_csv(f'exports/{filename}', columns=['id', 'status', 'created'], index=False)

    """
    Extract a list of workflows information as CSV.
    :param str workflow_definition_name: the workflow definition name to extract the instances from
    :param str filters: filters to apply to the API query
    :param boolean include_asset_filename: add the original file name of the asset in context
    """
    def get_metadata_migration_workflows(self, workflow_definition_name, filters = None, include_asset_filename = False):
        workflow_definition_id = self.flex_api_client.get_workflow_definition_id(workflow_definition_name)
        if filters:
            filters += f";definitionId={workflow_definition_id}"
        else:
            filters = f"definitionId={workflow_definition_id}"
        workflow_list = self.flex_api_client.get_workflows_by_filter(filters)

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"{workflow_definition_name}_{timestamp}.csv"

        if include_asset_filename:
            asset_original_file_name_map = {}
            for workflow in workflow_list:
                asset_id = workflow.asset_id
                original_file_name = self.flex_api_client.get_asset_filename(asset_id)
                asset_original_file_name_map[asset_id] = original_file_name

            data = [{'id': workflow.id, 'status': workflow.status, 'created': workflow.created, 'asset_id': workflow.asset_id, 'asset_name': workflow.asset_name, 'original_file_name': asset_original_file_name_map[workflow.asset_id]} for workflow in workflow_list]
            df = pd.DataFrame(data)
            df.to_csv(f'exports/{filename}', columns=['id', 'status', 'created', 'asset_id', 'asset_name', 'original_file_name'], index=False)
        else:
            data = [{'id': workflow.id, 'status': workflow.status, 'created': workflow.created, 'asset_id': workflow.asset_id, 'asset_name': workflow.asset_name} for workflow in workflow_list]
            df = pd.DataFrame(data)
            df.to_csv(f'exports/{filename}', columns=['id', 'status', 'created', 'asset_id', 'asset_name'], index=False)

    """
    Extract a list of assets information as CSV.
    :param str filters: filters to apply to the API query
    :param boolean include_asset_filename: add the original file name of the asset in context
    """
    def get_assets(self, filters = None, include_asset_filename = False):

        asset_list = self.flex_api_client.get_assets_by_filters(filters)

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"assets_{timestamp}.csv"

        if include_asset_filename:
            data = [{'id': asset.id, 'name': asset.name, 'original_file_name': asset.originalFileName} for asset in asset_list]
            df = pd.DataFrame(data)

            df.to_csv(f'exports/{filename}', columns=['id', 'name', 'original_file_name'], index=False)
        else:
            data = [{'id': asset.id, 'name': asset.name} for asset in asset_list]
            df = pd.DataFrame(data)
            df.to_csv(f'exports/{filename}', columns=['id', 'name'], index=False)

