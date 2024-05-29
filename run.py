#!/usr/bin/env python3

import os
from client.flex_api_client import FlexApiClient
from client.flex_cm_client import FlexCmClient
from actions.job import cancel_job
from monitoring.export import FlexExport
import time
import argparse
import os
import json
from utils import create_empty_directory
import csv
import pandas as pd
from objects.flex_objects import FlexAction
from actions.job import push_job_configuration
from actions.action import push_action_configuration
from configurations.workflow_migrator import WorfklowMigrator

current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)

def connect(env):
    file_path = f"{current_dir}/env.json"

    with open(file_path, 'a') as file:
        pass
    
    with open(file_path) as file:
        env_json = json.load(file)

        if env in env_json:
            BASE_URL = env_json[env]["url"]
            USERNAME = env_json[env]["username"]
            PASSWORD = env_json[env]["password"]
            print(f"Successfully connected to {env}!")
            return (BASE_URL, USERNAME, PASSWORD)
        else:
            print("Environment has not been added yet. Please add it first!")

def create_env(env, url, username, password):
    file_path = f"{current_dir}/env.json"

    with open(file_path, 'a') as file:
        pass 

    # Read json
    with open(file_path, 'r') as file:
        content = file.read()
        if not content:
            content = str({})
        env_json = json.loads(content)
    # Create new env
    env_json[env] = {'url': url, 'username': username, 'password': password}
    # Add new env
    with open(file_path, 'w') as file:
        json.dump(env_json, file, indent=4)

    print(f"Environment '{env}' has been added successfully!")

def main():

    parser = argparse.ArgumentParser(description='Flex Remote Executor (FRE) allows you to run commands remotely from your local terminal to Flex.')
    subparsers = parser.add_subparsers(help='Commands')

    # Export
    export_command = subparsers.add_parser('export', help='Export objects to a CSV.')
    export_command.add_argument('--env', type=str, help='Environment to use.')
    export_command.add_argument('--type', type=str, help='Object type : jobs, assets, workflows, etc.')
    export_command.add_argument('--name', type=str, help='Object name : action name, workflow definition name.')
    export_command.add_argument('--filters', type=str, help='Export filters to apply. Example : "status=Failed"')
    export_command.add_argument('--include-error', action='store_true', help='Include error (only useful for failed jobs).')
    export_command.add_argument('--include-metadata', action='store_true', help='Include metadata (only useful for assets).')
    export_command.add_argument('--header', type=str, help='Header for columns to export.')
    export_command.add_argument('--uuid', type=str, help='Object UUID to export.')
    export_command.set_defaults(func=export)

    # Retry
    retry_command = subparsers.add_parser('retry', help='Retry failed jobs.')
    retry_command.add_argument('--env', type=str, help='Environment to use.')
    retry_command.add_argument('--type', type=str, help='Object type : jobs, workflows.')
    retry_command.add_argument('--name', type=str, help='Object name : action name, workflow definition name.')
    retry_command.add_argument('--filters', type=str, help='Filters to apply. Example : "status=Failed"')
    retry_command.add_argument('--id', type=str, help='Object ID to retry.')
    retry_command.add_argument('--ids', type=str, help='Object IDs to retry.')
    retry_command.add_argument('--script-path', type=str, help='Script path to update the job or action.')
    retry_command.add_argument('--keep-imports', action='store_true', help='Keep the import section of the job, without updating it with classes from the script. Only available with the --script-path flag.')
    retry_command.add_argument('--errors', type=str, help='Error message of jobs to cancel. Example : "Resource item named"')
    retry_command.add_argument('--delay', type=int, help='Delay in seconds between each retry')
    retry_command.set_defaults(func=retry)

    # Cancel
    cancel_command = subparsers.add_parser('cancel', help='Cancel failed jobs.')
    cancel_command.add_argument('--env', type=str, help='Environment to use.')
    cancel_command.add_argument('--type', type=str, help='Object type : jobs, workflows.')
    cancel_command.add_argument('--name', type=str, help='Object name : action name, workflow definition name.')
    cancel_command.add_argument('--filters', type=str, help='Filters to apply. Example : "status=Failed"')
    cancel_command.add_argument('--errors', type=str, help='Error message of jobs to cancel. Example : "Resource item named"')
    cancel_command.add_argument('--delay', type=int, help='Delay in seconds between each cancel')
    cancel_command.set_defaults(func=cancel)

    # Create
    create_command = subparsers.add_parser('create', help='Create new object or environment.')
    create_command.add_argument('--env', type=str, help='Environment to use.')
    create_command.add_argument('--set-default', action='store_true', help="Set environment as default.")
    create_command.add_argument('--type', type=str, help='Object type : env, action, header, workflow, job.')
    create_command.add_argument('--name', type=str, help='Object name.')
    create_command.add_argument('--value', type=str, help='Object value.')
    create_command.add_argument('--definitionId', type=str, help='Workflow definition ID.')
    create_command.add_argument('--assetId', type=str, help='Asset ID to launch the job or workflow on.')
    create_command.add_argument('--assetIds', type=str, help='Asset IDs to launch the job or workflow on.')
    create_command.add_argument('--url', type=str, help='Environment URL.')
    create_command.add_argument('--username', type=str, help='Username.')
    create_command.add_argument('--password', type=str, help='User password')
    create_command.set_defaults(func=create)

    # Update
    update_command = subparsers.add_parser('update', help='Update an object.')
    update_command.add_argument('--env', type=str, help='Environment to use.')
    update_command.add_argument('--type', type=str, help='Object type : job, action, ...')
    update_command.add_argument('--id', type=str, help='Object ID.')
    update_command.add_argument('--script-path', type=str, help='Script path to update the job or action.')
    update_command.set_defaults(func=update)

    # Cancel and relaunch
    cancel_and_relaunch_command = subparsers.add_parser('cancel_and_relaunch', help='Cancel an instance and relaunch a new one with the same variables.')
    cancel_and_relaunch_command.add_argument('--env', type=str, help='Environment to use.')
    cancel_and_relaunch_command.add_argument('--name', type=str, help='Object name.')
    cancel_and_relaunch_command.add_argument('--filters', type=str, help='Filters to apply.')
    cancel_and_relaunch_command.add_argument('--type', type=str, help='Object type : workflows, jobs, actions, ...')
    cancel_and_relaunch_command.add_argument('--id', type=str, help='Object ID.')
    cancel_and_relaunch_command.add_argument('--ids', type=str, help='Object IDs.')
    cancel_and_relaunch_command.set_defaults(func=cancel_and_relaunch_cmd)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        # Call the function associated with the command
        args.func(args)
    else:
        # No command was provided, so you can print the help message
        parser.print_help()

def create(args):

    start_time = time.time()

    if not getattr(args, 'type', None):
        print("Please specify a type for the object to create.")
        return
    
    type = args.type

    match type:
        case 'env':
            if not getattr(args, 'name', None):
                print("Please specify a name for the object to create.")
                return
            name = args.name
            if getattr(args, 'url', None) and getattr(args, 'username', None) and getattr(args, 'password', None):
                url = args.url
                username = args.username
                password = args.password
                if getattr(args, 'set_default', None):
                    create_env('default', url, username, password)
                create_env(name, url, username, password)
            else:
                print('Please specify a url, username and password value to create a new environment!')
        case 'header':
            if not getattr(args, 'name', None):
                print("Please specify a name for the object to create.")
                return
            name = args.name
            header = args.value.split(',')
            create_empty_directory(current_dir + '/headers/')
            if not getattr(args, 'name', None):
                raise ("Please specify a header name!")
            file_name = args.name + '.csv'
            file_path = f'{current_dir}/headers/{file_name}'
            # Open the file in write mode and write the headers
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(header)
        case 'workflow':
            if getattr(args, 'definitionId', None):
                definitionId = args.definitionId
            else:
                raise Exception("Please specify a definitionId!")

            if getattr(args, 'env', None):
                (BASE_URL, USERNAME, PASSWORD) = connect(args.env)
            else:
                (BASE_URL, USERNAME, PASSWORD) = connect('default')
            
            flex_api_client = FlexApiClient(BASE_URL, USERNAME, PASSWORD)

            if getattr(args, 'assetId', None):
                assetId = args.assetId
                flex_api_client.create_workflow(definitionId, assetId)
            elif (getattr(args, 'assetIds', None)):
                assetIds = args.assetIds
                list_of_ids = assetIds.split(',')
                for id in list_of_ids:
                    flex_api_client.create_workflow(definitionId, id)
            else:
                flex_api_client.create_workflow(definitionId)
        case 'job':
            if getattr(args, 'actionId', None):
                actionId = args.actionId
            else:
                raise Exception("Please specify an actionId!")

            if getattr(args, 'env', None):
                (BASE_URL, USERNAME, PASSWORD) = connect(args.env)
            else:
                (BASE_URL, USERNAME, PASSWORD) = connect('default')
            
            flex_api_client = FlexApiClient(BASE_URL, USERNAME, PASSWORD)

            if getattr(args, 'assetId', None):
                assetId = args.assetId
                flex_api_client.create_job(definitionId, assetId)
            elif (getattr(args, 'assetIds', None)):
                assetIds = args.assetIds
                list_of_ids = assetIds.split(',')
                for id in list_of_ids:
                    flex_api_client.create_job(definitionId, id)
            else:
                flex_api_client.create_job(definitionId)
        case _:
            print(f"{name} object cannot be created.")
    
    end_time = time.time()
    duration = end_time - start_time
    print(f"finished in {round(duration)}s.")

def update(args):

    start_time = time.time()
    
    id = args.id

    if not getattr(args, 'type', None):
        print("Please specify a type for the object to update.")
        return
    
    type = args.type

    if getattr(args, 'env', None):
        (BASE_URL, USERNAME, PASSWORD) = connect(args.env)
    else:
        (BASE_URL, USERNAME, PASSWORD) = connect('default')
    
    flex_api_client = FlexApiClient(BASE_URL, USERNAME, PASSWORD)

    match type:
        case 'job':
            if not getattr(args, 'script_path', None):
                print("Please specify a script path for the object to update.")
                return
            script_path = args.script_path
            push_job_configuration(flex_api_client, script_path, id)
        case 'action':
            if not getattr(args, 'script_path', None):
                print("Please specify a type for the object to update.")
                return
            script_path = args.script_path
            push_action_configuration(flex_api_client, script_path, id)

        case _:
            print(f"Type {type} is not implemented yet!")
    
    end_time = time.time()
    duration = end_time - start_time
    print(f"finished in {round(duration)}s.")

def export(args):

    start_time = time.time()
    if getattr(args, 'env', None):
        (BASE_URL, USERNAME, PASSWORD) = connect(args.env)
    else:
        (BASE_URL, USERNAME, PASSWORD) = connect('default')

    type = args.type
    filters = args.filters

    if getattr(args, 'name', None):
        name = args.name

    if type == "workflow_dependencies":
        flex_cm_client = FlexCmClient(BASE_URL, USERNAME, PASSWORD)
        migrator = WorfklowMigrator(flex_cm_client)

        if getattr(args, 'name', None):
            name = args.name
            workflow_definition_name = name
            workflow_definition = flex_cm_client.get_workflow_definition(workflow_definition_name, None)
        elif getattr(args, 'uuid', None):
            uuid = args.uuid
            workflow_definition = flex_cm_client.get_workflow_definition(None, uuid)
        else:
            raise Exception("Please specify name or uuid!")
        
        dependency_list = migrator.get_workflow_definition_dependencies(workflow_definition)
        dependency_list.extend(migrator.get_workflow_references(workflow_definition))
        dependency_dir_path = current_dir + '/dependencies/'
        create_empty_directory(dependency_dir_path)
        migrator.create_dependencies_file(dependency_dir_path, workflow_definition, dependency_list)
        return

    flex_api_client = FlexApiClient(BASE_URL, USERNAME, PASSWORD)
    metadata_migration_tracker = FlexExport(flex_api_client)

    if getattr(args, 'include_error', None) and "Failed" in filters and type == "workflows":
        print("Getting jobs from workflow definition")
        workflow_definition_name = name
        workflow_definition_id = flex_api_client.get_workflow_definition_id(workflow_definition_name)
        workflow_structure = flex_api_client.get_workflow_structure(workflow_definition_id)

        nodes = workflow_structure["nodes"]

        action_list = []

        if (len(nodes) > 0):
            for node in nodes:
                if (node["type"] == "ACTION"):
                    action = FlexAction(node["action"]["id"], node["action"]["type"])
                    action_list.append(action)

        set_action_list = set(action_list) 
        unique_action_list = (list(set_action_list))

        args.type = "jobs"
        df_list = []
        for action in unique_action_list:
            action_id = action.id
            action_type = action.type
            if filters:
                new_filters = filters + f";actionId={action_id};actionType={action_type}"
            else:
                new_filters = f"actionId={action_id};actionType={action_type}"
            args.filters = new_filters
            args.name = None
            df_list.append(metadata_migration_tracker.export_by_batch(args))

        final_df = pd.concat(df_list, ignore_index=True)
        if getattr(args, 'header', None):
            header = args.header
        metadata_migration_tracker.export_csv(final_df, current_dir, type, name, header)
    else:
        if type == "assets":
            total_results = flex_api_client.get_total_results("assets", filters)
            if total_results > 10000 and 'metadata' in filters:
                assets = flex_api_client.get_objects_by_filters("assets", filters)
                df = pd.DataFrame(assets)
            else:
                df = metadata_migration_tracker.export_by_batch(args)
        else:
            df = metadata_migration_tracker.export_by_batch(args)
        if getattr(args, 'header', None):
            header = args.header
        if getattr(args, 'name', None):
            metadata_migration_tracker.export_csv(df, current_dir, type, name, header)
        else:
            metadata_migration_tracker.export_csv(df, current_dir, type, type, header)

    end_time = time.time()
    duration = end_time - start_time
    print(f"finished in {round(duration)}s.")

def retry(args):

    start_time = time.time()

    if getattr(args, 'env', None):
        (BASE_URL, USERNAME, PASSWORD) = connect(args.env)
    else:
        (BASE_URL, USERNAME, PASSWORD) = connect('default')
    
    flex_api_client = FlexApiClient(BASE_URL, USERNAME, PASSWORD)

    filters = args.filters
    type = args.type
    
    if getattr(args, 'delay', None):
        delay = args.delay

    if getattr(args, 'id', None):
        id = args.id
        if type == 'job' or type == 'jobs':
            if getattr(args, 'script_path', None):
                script_path = args.script_path
                push_job_configuration(flex_api_client, script_path, id)
            flex_api_client.retry_job(id)
        elif type == 'workflow' or type == 'workflows':
            flex_api_client.retry_workflow(id)
        return
    
    if getattr(args, 'ids', None):
        ids = args.ids.split(',')
        for id in ids:
            if type == 'job' or type == 'jobs':
                if getattr(args, 'script_path', None):
                    script_path = args.script_path
                    push_job_configuration(flex_api_client, script_path, id)
                flex_api_client.retry_job(id)
            elif type == 'workflow' or type == 'workflows':
                flex_api_client.retry_workflow(id)
        return
    
    # Only failed objects can be cancelled
    if getattr(args, 'filters', None):
        filters = args.filters
        if 'status' not in filters:
            filters += ";status=Failed"
    else:
        filters = "status=Failed"

    if getattr(args, 'name', None):
        name = args.name

        if type == "jobs":
            action_name = name
            action_id = flex_api_client.get_action_id(action_name)
            action = flex_api_client.get_action(action_id)
            action_type = action["type"]["name"]
            if filters:
                filters += f";actionId={action_id};actionType={action_type}"
            else: 
                filters = f"actionId={action_id};actionType={action_type}"
        elif type == "workflows":
            workflow_definition_name = name
            workflow_definition_id = flex_api_client.get_workflow_definition_id(workflow_definition_name)
            if filters:
                filters += f";definitionId={workflow_definition_id}"
            else: 
                filters = f"definitionId={workflow_definition_id}"

    total_number_of_results = flex_api_client.get_total_results(type, filters)

    print(f"Number of instances to retry : {total_number_of_results}")

    offset = 0
    limit = 100
    instances_to_retry = flex_api_client.get_next_objects(type, filters, offset, limit)[type]

    while offset < total_number_of_results:
        for instance in instances_to_retry:
            instance_id = instance["id"]
            if type == 'jobs':
                if getattr(args, 'script_path', None):
                    script_path = args.script_path
                    if getattr(args, 'keep_imports', None):
                        push_job_configuration(flex_api_client, script_path, instance_id, True)
                    else:
                        push_job_configuration(flex_api_client, script_path, instance_id, False)
                if getattr(args, 'errors', None):
                    errors = args.errors
                    job_history = flex_api_client.get_job_history(instance_id)
                    for event in job_history["events"]:
                        if event["eventType"] == "Failed":
                            exception_message = event["exceptionMessage"]
                            error = exception_message.split("\n")[0].replace('Exception: ', '')
                            for targetted_error in errors.split(','):
                                if targetted_error in error:
                                    print(f"Found job ID {instance_id} to retry with error {error}")
                                    try:
                                        flex_api_client.retry_job(instance_id)
                                    except Exception as e:
                                        print(f"Unable to retry job {instance_id}")
                else:
                    flex_api_client.retry_instance(instance_id, type)
                if delay:
                    time.sleep(delay)
            
        offset+=limit
        instances_to_retry = flex_api_client.get_next_objects(type, filters, offset, limit)[type]

    end_time = time.time()
    duration = end_time - start_time
    print(f"finished in {round(duration)}s.")

def cancel(args):

    if getattr(args, 'env', None):
        (BASE_URL, USERNAME, PASSWORD) = connect(args.env)
    else:
        (BASE_URL, USERNAME, PASSWORD) = connect('default')
        
    flex_api_client = FlexApiClient(BASE_URL, USERNAME, PASSWORD)

    type = args.type
    filters = args.filters

    if getattr(args, 'delay', None):
        delay = args.delay

    start_time = time.time()

    if getattr(args, 'id', None):
        id = args.id
        flex_api_client.cancel_instance(type, id)
    elif getattr(args, 'ids', None):
        ids = args.ids.split(',')
        for id in ids:
            flex_api_client.cancel_instance(type, id)

    elif type == "workflows":

        if getattr(args, 'name', None):
            name = args.name
            workflow_definition_name = name
            workflow_definition_id = flex_api_client.get_workflow_definition_id(workflow_definition_name)
            if filters:
                filters += f";definitionId={workflow_definition_id}"
        instances = flex_api_client.get_objects_by_filters(type, filters)
        print(f"Number of instances to cancel : {len(instances)}")
        for instance in instances:
            instance_id = instance["id"]
            flex_api_client.cancel_instance(type, instance_id)
            print(f"Cancel instance ID {instance_id}")
            if delay:
                time.sleep(delay)

    elif type == "jobs":
        if getattr(args, 'name', None):
            name = args.name
            action_name = name
            action_id = flex_api_client.get_action_id(action_name)
            filters = f"actionId={action_id}"
        if getattr(args, 'errors', None):
            cancel_failed_jobs(flex_api_client, args)
        else:
            # Cancel jobs regardless of their errors
            job_list = get_jobs(args, flex_api_client)
            print(f"Number of jobs to cancel : {len(job_list)}")
            for job in job_list:
                job_id = job["id"]
                try:
                    cancel_job(flex_api_client, None, job_id)
                except Exception as e:
                    print(f"Unable to cancel job {job_id} : ", e)
                if delay:
                    time.sleep(delay)
        end_time = time.time()
        duration = end_time - start_time
        print(f"finished in {round(duration)}s.")

def cancel_and_relaunch_cmd(args):

    if getattr(args, 'env', None):
        (BASE_URL, USERNAME, PASSWORD) = connect(args.env)
    else:
        (BASE_URL, USERNAME, PASSWORD) = connect('default')
        
    flex_api_client = FlexApiClient(BASE_URL, USERNAME, PASSWORD)

    type = args.type
    if getattr(args, 'filters', None):
        filters = args.filters

    start_time = time.time()

    if type == "workflows":
        if getattr(args, 'id', None):
            id = args.id
            cancel_and_relaunch_workflow(flex_api_client, id)
        elif getattr(args, 'ids', None):
            ids = args.ids.split(',')
            for id in ids:
                cancel_and_relaunch_workflow(flex_api_client, id)

        else:
            if getattr(args, 'name', None):
                name = args.name
                workflow_definition_name = name
                workflow_definition_id = flex_api_client.get_workflow_definition_id(workflow_definition_name)
                if filters:
                    filters += f";definitionId={workflow_definition_id}"
            instances = flex_api_client.get_objects_by_filters(type, filters)
            print(f"Number of instances to cancel : {len(instances)}")
            for instance in instances:
                instance_id = instance["id"]
                cancel_and_relaunch_workflow(flex_api_client, instance_id)

    elif type == "jobs":

        if getattr(args, 'id', None):
            id = args.id
            cancel_and_relaunch_job(flex_api_client, id)
        elif getattr(args, 'ids', None):
            ids = args.ids.split(',')
            for id in ids:
                cancel_and_relaunch_job(flex_api_client, id)
        else:
            if getattr(args, 'name', None):
                name = args.name
                action_name = name
                action_id = flex_api_client.get_action_id(action_name)
                filters = f"actionId={action_id}"
            if getattr(args, 'errors', None):
                cancel_failed_jobs(flex_api_client, args)
            else:
                # Cancel jobs regardless of their errors
                job_list = get_jobs(args, flex_api_client)
                print(f"Number of jobs to cancel and relaunch: {len(job_list)}")
                for job in job_list:
                    job_id = job["id"]
                    cancel_and_relaunch_job(flex_api_client, job_id)
        end_time = time.time()
        duration = end_time - start_time
        print(f"finished in {round(duration)}s.")

def cancel_and_relaunch_workflow(flex_api_client, instance_id):
    flex_api_client.cancel_instance('workflows', instance_id)
    print(f"Cancel instance ID {instance_id}")
    # Launch new workflow
    instance = flex_api_client.get_workflow(instance_id, 'true')
    variables = instance["variables"]
    if ("asset" in instance):
        asset_id = instance["asset"]["id"]
    else:
        asset_id = None
    flex_api_client.create_workflow(instance["definition"]["id"], asset_id, variables)

def cancel_and_relaunch_job(flex_api_client, instance_id):
    flex_api_client.cancel_instance('jobs', instance_id)
    print(f"Cancel instance ID {instance_id}")
    # Launch new workflow
    instance = flex_api_client.get_job(instance_id, 'true')
    variables = instance["variables"]
    if ("asset" in instance):
        asset_id = instance["asset"]["id"]
    else:
        asset_id = None
    flex_api_client.create_job(instance["action"]["id"], asset_id, variables)

def cancel_failed_jobs(flex_api_client, args):
    errors = args.errors
    filters = apply_default_filters(args, flex_api_client)

    # Get first total number of results
    result = flex_api_client.get_jobs_batch_by_filter(filters, 0, 1)
    total_results = result["totalCount"]

    if getattr(args, 'delay', None):
        delay = args.delay

    offset = 0
    limit = 100
    while (total_results > offset + limit):
        print(f"Getting next jobs from {offset} to {offset + limit}")
        jobs = flex_api_client.get_jobs_batch_by_filter(filters, offset, limit)["jobs"]
        cancel_jobs_by_errors(jobs, flex_api_client, errors, delay)
        offset += limit

def cancel_jobs_by_errors(jobs, flex_api_client, errors, delay = None):
    for job in jobs:
        job_id = job["id"]
        job_history = flex_api_client.get_job_history(job["id"])
        for event in job_history["events"]:
            if event["eventType"] == "Failed":
                exception_message = event["exceptionMessage"]
                error = exception_message.split("\n")[0].replace('Exception: ', '')
                for targetted_error in errors.split(','):
                    if targetted_error in error:
                        print(f"Found job ID {job_id} to cancel with error {error}")
                        try:
                            cancel_job(flex_api_client, None, job_id)
                        except Exception as e:
                            print(f"Unable to cancel job {job_id}")
        if delay:
            time.sleep(delay)

def get_jobs(args, flex_api_client):
    # only failed objects can be cancelled
    if getattr(args, 'filters', None):
        filters = args.filters
        if 'status' not in filters:
            filters += ";status=Failed"
    else:
        filters = "status=Failed"

    if getattr(args, 'name', None):
        name = args.name
        action_name = name
        action_id = flex_api_client.get_action_id(action_name)
        action = flex_api_client.get_action(action_id)
        action_type = action["type"]["name"]
        if filters:
            filters += f";actionId={action_id};actionType={action_type}"
        else: 
            filters = f"actionId={action_id};actionType={action_type}"

    job_list = flex_api_client.get_jobs_by_filter_df(filters)

    return job_list

def apply_default_filters(args, flex_api_client):
    # only failed objects can be cancelled
    if getattr(args, 'filters', None):
        filters = args.filters
        if 'status' not in filters:
            filters += ";status=Failed"
    else:
        filters = "status=Failed"

    if getattr(args, 'name', None):
        name = args.name
        action_name = name
        action_id = flex_api_client.get_action_id(action_name)
        action = flex_api_client.get_action(action_id)
        action_type = action["type"]["name"]
        if filters:
            filters += f";actionId={action_id};actionType={action_type}"
        else: 
            filters = f"actionId={action_id};actionType={action_type}"
            
    return filters


if __name__ == "__main__":
    main()