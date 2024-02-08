import pandas as pd
from datetime import datetime

class MetadataMigrationTracker:
    def __init__(self, flex_api_client):
        self.flex_api_client = flex_api_client

    def get_metadata_migration_jobs(self, filters = None):
        action_name = "parse-rs2i-xml"
        action_id = self.flex_api_client.get_action_id(action_name)
        if filters:
            filters += f"actionId={action_id}"
        else: 
            filters = f"actionId={action_id}"
        job_list = self.flex_api_client.get_jobs(filters)

        data = [{'id': job.id, 'status': job.status, 'created': job.created} for job in job_list]

        df = pd.DataFrame(data)

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

        filename = f"{action_name}_{timestamp}.csv"
        df.to_csv(filename, columns=['id', 'status', 'created'], index=False)

    def get_metadata_migration_workflows(self, filters = None):
        workflow_definition_name = "RS2i Metadata Migration"
        workflow_definition_id = self.flex_api_client.get_workflow_definition_id(workflow_definition_name)
        filters = f"workflowDefinitionId={workflow_definition_id}"
        workflow_list = self.flex_api_client.get_workflows(filters)

        data = [{'id': workflow.id, 'status': workflow.status, 'created': workflow.created} for workflow in workflow_list]

        df = pd.DataFrame(data)

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

        filename = f"{workflow_definition_name}_{timestamp}.csv"
        df.to_csv(filename, columns=['id', 'status', 'created'], index=False)