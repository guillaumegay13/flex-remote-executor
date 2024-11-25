import pandas as pd
from datetime import datetime
import os
import json
import concurrent.futures
from utils import create_empty_directory
from tqdm import tqdm

class FlexExport:
    def __init__(self, flex_api_client):
        self.flex_api_client = flex_api_client
    
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
        create_empty_directory(f'exports/{type}/')

        json_struct = json.loads(df.to_json(orient="records"))
        df_flat = pd.json_normalize(json_struct)

        file_path = os.path.join(os.getcwd(), f'exports/{type}/{filename}')
        print(f"Creating export file {filename} in {file_path}")
            
        df_flat.to_csv(f'exports/{type}/{filename}', columns=columns, sep=';', index=False)
        print(f"{file_path} created!")

    """
    Export method with parallelization, by batches of {limit} (100 by default).
    """
    def export_by_batch(self, args):

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

            if type == "jobs" and getattr(args, 'name', None):
                action_name = name
                action_id = self.flex_api_client.get_action_id(action_name)
                action = self.flex_api_client.get_action(action_id)
                action_type = action["type"]["name"]
                if filters:
                    filters += f";actionId={action_id};actionType={action_type}"
                else: 
                    filters = f"actionId={action_id};actionType={action_type}"
            elif type == "workflows" and getattr(args, 'name', None):
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

        print(f"Number of instances to export: {total_number_of_results}")

        offsets = range(0, total_number_of_results, limit)

        # Using ThreadPoolExecutor to run API calls in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Create a progress bar
            with tqdm(total=len(offsets), desc="Exporting data") as pbar:
                futures = [
                    executor.submit(self.flex_api_client.get_next_objects, type, filters, offset, limit)
                    for offset in offsets
                ]

                # Collecting results as they complete
                objects = []
                for future in concurrent.futures.as_completed(futures):
                    try:
                        data = future.result()
                        objects.extend(data[f'{type}'])
                    except Exception as exc:
                        print(f"An error occurred: {exc}")
                    finally:
                        pbar.update(1)  # Increment progress bar for each completed future

        df = pd.DataFrame(objects)

        if getattr(args, 'include_error', None) and "Failed" in filters and type == "jobs":
            # Using ThreadPoolExecutor to run API calls in parallel
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Create a future
                futures = [executor.submit(self.flex_api_client.get_job_history, object["id"]) for object in objects]

                # Initialize the job_errors list with placeholders
                job_errors = [None] * len(objects)
                
                # Collecting results as they complete
                job_errors = []
                for index, future in enumerate(concurrent.futures.as_completed(futures)):
                    error_message = "None"  # Default error message if no error is found

                    try:
                        job_errors.append("Failed")
                        job_history = future.result()
                        for event in job_history["events"]:
                            if event["eventType"] == "Failed":
                                exception_message = event["exceptionMessage"]
                                error_message = exception_message.split("\n")[0].replace('Exception: ', '')
                                break 
                    except Exception as exc:
                        print(f"An error occurred: {exc}")
                        error_message = "Failed"  # Set error message to "Failed" if an exception occurs

                    # Update the corresponding entry in job_errors with the determined error message
                    job_errors[index] = error_message

            assert len(job_errors) == len(df)
            # df["exceptionMessage"] = job_errors
            df['exceptionMessage'] = pd.Series(job_errors)

        return df

    def export_csv(self, df, root_dir, type, prefix, header = None):
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"{prefix}_{timestamp}.csv"
        create_empty_directory(f'{root_dir}/exports/{type}/')

        json_struct = json.loads(df.to_json(orient="records"))
        df_flat = pd.json_normalize(json_struct)

        file_path = f'{root_dir}/exports/{type}/{filename}'
        print(f"Creating export file {filename} in {root_dir}/exports/{type}/")
            
        # Specify header without extension
        if header:
            header_file_name = header + '.csv'
            header_file_path = f'{root_dir}/headers/{header_file_name}'
            header = pd.read_csv(header_file_path)
            # Load the CSV file
            header_df = pd.read_csv(header_file_path, nrows=0)
            header = header_df.columns[0]
            columns = header.split(';')
            df_flat.to_csv(f'{file_path}', columns=columns, sep=';', index=False)
        else:
            df_flat.to_csv(f'{file_path}', sep=';', index=False)

        print(f"{filename} created!")