import pandas as pd
from datetime import datetime
import os
from objects.flex_objects import FlexJob
import json
import time
import concurrent.futures
import math

class MetadataMigrationTracker:
    def __init__(self, flex_api_client):
        self.flex_api_client = flex_api_client

    def create_empty_directory(self, directory_path):
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

    def get_jobs_errors(self, action_name, filters = None, errors = []):
        action_name = action_name
        action_id = self.flex_api_client.get_action_id(action_name)
        action = self.flex_api_client.get_action(action_id)
        action_type = action["type"]["name"]
        if filters:
            filters += f";actionId={action_id};actionType={action_type}"
        else: 
            filters = f"actionId={action_id};actionType={action_type}"
        job_list = self.flex_api_client.get_jobs_by_filter_df(filters)

        print(f"Fetched {len(job_list)} jobs")

        job_id_list_to_retry = []
        data = []
        
        for job in job_list:
            job_history = self.flex_api_client.get_job_history(job["id"])
            for event in job_history["events"]:
                if event["eventType"] == "Failed":
                    exception_message = event["exceptionMessage"]
                    error = exception_message.split("\n")[0].replace('Exception: ', '')
                    data.append({'id': job["id"], 'name': job["name"], 'status': job["status"], 'error': error})
                    for targetted_error in errors:
                        if targetted_error in error:
                            job_id_list_to_retry.append(job["id"])
        
        df = pd.DataFrame(data)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"{action_name}_{timestamp}.csv"
        self.create_empty_directory('exports/jobs/')
        df.to_csv(f'exports/jobs/{filename}', columns=['id', 'status', 'error'], sep=';', index=False)

        return job_id_list_to_retry
    
    def export_jobs(self, filters = None):
        job_list = self.flex_api_client.get_jobs_by_filter_df(filters, 0, 500)

        print(f"Fetched {len(job_list)} jobs")

        df = pd.DataFrame(job_list)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"jobs_{timestamp}.csv"
        self.create_empty_directory('exports/jobs/')

        json_struct = json.loads(df.to_json(orient="records"))    
        df_flat = pd.json_normalize(json_struct)
        df_flat.to_csv(f'exports/jobs/{filename}', columns=['id', 'name', 'status', 'created', 'workflow.displayName'], sep=';', index=False)

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
        self.create_empty_directory('exports/workflows/')

        if include_asset_filename:
            asset_original_file_name_map = {}
            for workflow in workflow_list:
                asset_id = workflow.asset_id
                original_file_name = self.flex_api_client.get_asset_filename(asset_id)
                asset_original_file_name_map[asset_id] = original_file_name

            data = [{'id': workflow.id, 'status': workflow.status, 'created': workflow.created, 'asset_id': workflow.asset_id, 'asset_name': workflow.asset_name, 'original_file_name': asset_original_file_name_map[workflow.asset_id]} for workflow in workflow_list]
            df = pd.DataFrame(data)
            df.to_csv(f'exports/workflows/{filename}', columns=['id', 'status', 'created', 'asset_id', 'asset_name', 'original_file_name'], sep=';', index=False)
        else:
            data = [{'id': workflow.id, 'status': workflow.status, 'created': workflow.created, 'asset_id': workflow.asset_id, 'asset_name': workflow.asset_name} for workflow in workflow_list]
            df = pd.DataFrame(data)
            df.to_csv(f'exports/workflows/{filename}', columns=['id', 'status', 'created', 'asset_id', 'asset_name'], sep=';', index=False)

    """
    Extract a list of assets information as CSV.
    :param str filters: filters to apply to the API query
    :param boolean include_asset_filename: add the original file name of the asset in context
    """
    def get_assets(self, filters = None, include_asset_filename = False):

        asset_list = self.flex_api_client.get_assets_by_filters(filters)

        print(f"Total number of assets retrieved : {len(asset_list)}")

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"assets_{timestamp}.csv"
        self.create_empty_directory('exports/assets/')

        if include_asset_filename:
            data = [{'id': asset.id, 'name': asset.name, 'original_file_name': asset.originalFileName} for asset in asset_list]
            df = pd.DataFrame(data)
            df.to_csv(f'exports/assets/{filename}', columns=['id', 'name', 'original_file_name'], sep=';', index=False)
        else:
            data = [{'id': asset.id, 'name': asset.name} for asset in asset_list]
            df = pd.DataFrame(data)
            df.to_csv(f'exports/assets/{filename}', columns=['id', 'name'], sep=';', index=False)

    def get_jobs_by_errors(self, workflow_definition_name, filters = None, errors = []):

        workflow_definition_id = self.flex_api_client.get_workflow_definition_id(workflow_definition_name)
        if filters:
            filters += f";definitionId={workflow_definition_id}"
        else:
            filters = f"definitionId={workflow_definition_id}"
        workflow_list = self.flex_api_client.get_workflows_by_filter(filters)

        print(f"workflow list size = {len(workflow_list)}")

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"jobs_{workflow_definition_name}_{timestamp}.csv"
        self.create_empty_directory('exports/jobs/')

        job_list = []
        data = []
        job_id_list_to_retry = []

        for workflow in workflow_list:
            jobs = self.flex_api_client.get_workflow_jobs(workflow.id)
            for job in jobs["jobs"]:
                if job["status"] == "Failed":
                    job = FlexJob(job["id"], job["name"], job["status"])
                    job_list.append(job)
                    job_id = job.id
                    job_history = self.flex_api_client.get_job_history(job_id)
                    for event in job_history["events"]:
                        if event["eventType"] == "Failed":
                            exception_message = event["exceptionMessage"]
                            error = exception_message.split("\n")[0].replace('Exception: ', '')
                            job.error = error
                            data.append({'id': job.id, 'name': job.name, 'status': job.status, 'error': job.error})
                            for targetted_error in errors:
                                if targetted_error in error:
                                    job_id_list_to_retry.append(job_id)

        print(f"job list size = {len(job_list)}")

        df = pd.DataFrame(data)
        df.to_csv(f'exports/jobs/{filename}', columns=['id', 'name', 'status', 'error'], sep=';', index=False)

        return job_id_list_to_retry
    
    def get_assets_full(self, filters):

        asset_list_dict = self.flex_api_client.get_objects_by_filters("assets", filters, 100)

        # data = [{'id': asset["id"], 'name': asset["name"], 'preferred_start_tc': asset["assetContext"]["formatContext"]["preferredStartTimecode"], 'preferred_drop_frame': asset["assetContext"]["formatContext"]["preferredDropFrame"]} for asset in asset_list_dict]

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"assets_{timestamp}.csv"
        self.create_empty_directory('exports/assets/')

        df = pd.DataFrame(asset_list_dict)

        json_struct = json.loads(df.to_json(orient="records"))    
        df_flat = pd.json_normalize(json_struct)

        print(f"index = {df_flat.columns}")

        df_flat.to_csv(f'exports/assets/{filename}', columns=['id', 'name', 'assetOrigin', 'referenceName', 'fileInformation.originalFileName'], sep=';', index=False)

    """
    Export method without parallelization (obsolete)
    """
    def export(self, type, filters = None, include_error = None):
        job_list = self.flex_api_client.get_objects_by_filters(type, filters, 100)

        columns=['id']
        if type == "jobs":
            columns.extend(['name', 'status', 'created', 'workflow.displayName'])
        elif type == "workflow":
            columns.extend(['name', 'status', 'created'])
        elif type == "events":
            columns.extend(['object.name', 'object.id', 'exceptionMessage'])

        print(f"Fetched {len(job_list)} objects")

        if include_error:
            columns.append('exceptionMessage')
            for job in job_list:
                job_history = self.flex_api_client.get_job_history(job["id"])
                for event in job_history["events"]:
                    if event["eventType"] == "Failed":
                        exception_message = event["exceptionMessage"]
                        error = exception_message.split("\n")[0].replace('Exception: ', '')
                        job["exceptionMessage"] = error

        df = pd.DataFrame(job_list)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"jobs_{timestamp}.csv"
        self.create_empty_directory(f'exports/{type}/')

        json_struct = json.loads(df.to_json(orient="records"))
        df_flat = pd.json_normalize(json_struct)

        file_path = os.path.join(os.getcwd(), f'exports/{type}/{filename}')
        print(f"Creating export file {filename} in {file_path}")
            
        df_flat.to_csv(f'exports/{type}/{filename}', columns=columns, sep=';', index=False)
        print(f"{file_path} created!")

    """
    Export method with parallelization, by batches of {limit} (100 by default).
    """
    def export_by_batch(self, args, root_dir):

        limit = 100
        filters = args.filters
        type = args.type

        """
        columns=['id']
        if type == "jobs":
            columns.extend(['name', 'status', 'created', 'workflow.displayName'])
        elif type == "workflows":
            columns.extend(['name', 'status', 'created', 'asset.id', 'asset.name'])
        elif type == "events":
            columns.extend(['object.name', 'object.id', 'exceptionMessage'])
        # elif type == "assets"
        """

        if getattr(args, 'name', None):
            name = args.name

            if type == "jobs":
                action_name = name
                action_id = self.flex_api_client.get_action_id(action_name)
                action = self.flex_api_client.get_action(action_id)
                action_type = action["type"]["name"]
                if filters:
                    filters += f";actionId={action_id};actionType={action_type}"
                else: 
                    filters = f"actionId={action_id};actionType={action_type}"
            elif type == "workflows":
                workflow_definition_name = name
                workflow_definition_id = self.flex_api_client.get_workflow_definition_id(workflow_definition_name)
                if filters:
                    filters += f";definitionId={workflow_definition_id}"
                else: 
                    filters = f"definitionId={workflow_definition_id}"

        # Include metadata for assets only
        if getattr(args, 'include_metadata', None) and type == 'assets':
            if filters:
                filters += f";includeMetadata=true"
            else:
                filters = f"includeMetadata=true"

        total_number_of_results = self.flex_api_client.get_total_results(type, filters)

        print(f"Number of instances to export : {total_number_of_results}")

        offsets = range(0, total_number_of_results, limit)

        # Using ThreadPoolExecutor to run API calls in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Create a future to URL mapping
            futures = [executor.submit(self.flex_api_client.get_next_objects, type, filters, offset, limit) for offset in offsets]

            # Collecting results as they complete
            objects = []
            for future in concurrent.futures.as_completed(futures):
                try:
                    data = future.result()
                    objects.extend(data[f'{type}'])
                    # print(f"Data fetched with offset {data['offset']}")
                except Exception as exc:
                    print(f"An error occurred: {exc}")

        if getattr(args, 'include_error', None) and "Failed" in filters:
            # Using ThreadPoolExecutor to run API calls in parallel
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Create a future to URL mapping
                futures = [executor.submit(self.flex_api_client.get_job_history, object["id"]) for object in data[f'{type}']]

                # Collecting results as they complete
                job_errors = []
                for future in concurrent.futures.as_completed(futures):
                    try:
                        job_history = future.result()
                        for event in job_history["events"]:
                            if event["eventType"] == "Failed":
                                exception_message = event["exceptionMessage"]
                                error = exception_message.split("\n")[0].replace('Exception: ', '')
                                object["exceptionMessage"] = error
                                job_errors.extend(data[f'{type}'])
                        # print(f"Data fetched with offset {data['offset']}")
                    except Exception as exc:
                        print(f"An error occurred: {exc}")

        df = pd.DataFrame(objects)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"{type}_{timestamp}.csv"
        self.create_empty_directory(f'{root_dir}/exports/{type}/')

        json_struct = json.loads(df.to_json(orient="records"))
        df_flat = pd.json_normalize(json_struct)

        file_path = f'{root_dir}/exports/{type}/{filename}'
        # print(f"Creating export file {filename} in {file_path}")
            
        if getattr(args, 'columns', None):
            columns = args.columns.split(',')
            df_flat.to_csv(f'{file_path}', columns=columns, sep=';', index=False)
        else:
            df_flat.to_csv(f'{file_path}', sep=';', index=False)

        print(f"{filename} created!")