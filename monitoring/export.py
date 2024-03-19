import pandas as pd
from datetime import datetime
import os
import json
import concurrent.futures
from utils import create_empty_directory

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

        df = pd.DataFrame(objects)

        if getattr(args, 'include_error', None) and "Failed" in filters:
            # Using ThreadPoolExecutor to run API calls in parallel
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Create a future to URL mapping
                futures = [executor.submit(self.flex_api_client.get_job_history, object["id"]) for object in objects]

                # Collecting results as they complete
                job_errors = []
                for future in concurrent.futures.as_completed(futures):
                    try:
                        job_history = future.result()
                        error_found = False
                        for event in job_history["events"]:
                            if event["eventType"] == "Failed":
                                exception_message = event["exceptionMessage"]
                                error = exception_message.split("\n")[0].replace('Exception: ', '')
                                job_errors.append(error)
                                error_found = True
                        if not error_found:
                            job_errors.append("None")
                    except Exception as exc:
                        job_errors.append("Failed")
                        print(f"An error occurred: {exc}")

            df["exceptionMessage"] = job_errors
            # print (job_errors)

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"{type}_{timestamp}.csv"
        create_empty_directory(f'{root_dir}/exports/{type}/')

        json_struct = json.loads(df.to_json(orient="records"))
        df_flat = pd.json_normalize(json_struct)

        file_path = f'{root_dir}/exports/{type}/{filename}'
        print(f"Creating export file {filename} in {root_dir}/exports/{type}/")
        
        # Specify header without extension
        if getattr(args, 'header', None):
            header_file_name = args.header + '.csv'
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