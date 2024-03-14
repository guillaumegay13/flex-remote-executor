#!/usr/bin/env python3

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
import argparse
import os
import json

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
    export_command.add_argument('--include_error', action='store_true', help='Include error (only useful for failed jobs).')
    export_command.add_argument('--include_metadata', action='store_true', help='Include metadata (only useful for assets).')
    export_command.add_argument('--columns', type=str, help='Columns to export.')
    export_command.set_defaults(func=export)

    # Retry
    retry_command = subparsers.add_parser('retry', help='Retry failed jobs.')
    retry_command.add_argument('--env', type=str, help='Environment to use.')
    retry_command.add_argument('--type', type=str, help='Object type : jobs, assets, workflows, etc.')
    retry_command.add_argument('--name', type=str, help='Object name : action name, workflow definition name.')
    retry_command.add_argument('--filters', type=str, help='Filters to apply. Example : "status=Failed"')
    retry_command.set_defaults(func=retry)

    # Cancel
    cancel_command = subparsers.add_parser('cancel', help='Cancel failed jobs.')
    cancel_command.add_argument('--env', type=str, help='Environment to use.')
    cancel_command.add_argument('--type', type=str, help='Object type : jobs, workflows.')
    cancel_command.add_argument('--name', type=str, help='Object name : action name, workflow definition name.')
    cancel_command.add_argument('--filters', type=str, help='Filters to apply. Example : "status=Failed"')
    cancel_command.add_argument('--errors', type=str, help='Error message of jobs to cancel. Example : "Resource item named"')
    cancel_command.set_defaults(func=cancel)

    # Create
    create_command = subparsers.add_parser('create', help='Create new object or environment.')
    create_command.add_argument('--env', type=str, help='Environment to use.')
    create_command.add_argument('--set-default', action='store_true', help="Set environment as default.")
    create_command.add_argument('--type', type=str, help='Object type : env, action.')
    create_command.add_argument('--name', type=str, help='Object name.')
    create_command.add_argument('--url', type=str, help='Environment URL.')
    create_command.add_argument('--username', type=str, help='Username.')
    create_command.add_argument('--password', type=str, help='User password')
    create_command.set_defaults(func=create)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        # Call the function associated with the command
        args.func(args)
    else:
        # No command was provided, so you can print the help message
        parser.print_help()

def create(args):

    start_time = time.time()
    
    if not getattr(args, 'name', None):
        print("Please specify a name for the object to create.")
        return
    
    name = args.name

    if not getattr(args, 'type', None):
        print("Please specify a type for the object to create.")
        return
    
    type = args.type

    match type:
        case 'env':
            if getattr(args, 'url', None) and getattr(args, 'username', None) and getattr(args, 'password', None):
                url = args.url
                username = args.username
                password = args.password
                if getattr(args, 'set_default', None):
                    create_env('default', url, username, password)
                create_env(name, url, username, password)
            else:
                print('Please specify a url, username and password value to create a new environment!')
        case _:
            print(f"{name} object cannot be created.")
    
    end_time = time.time()
    duration = end_time - start_time
    print(f"finished in {round(duration)}s.")

def export(args):

    start_time = time.time()
    if getattr(args, 'env', None):
        (BASE_URL, USERNAME, PASSWORD) = connect(args.env)
    else:
        (BASE_URL, USERNAME, PASSWORD) = connect('default')
    
    flex_api_client = FlexApiClient(BASE_URL, USERNAME, PASSWORD)

    metadata_migration_tracker = MetadataMigrationTracker(flex_api_client)

    metadata_migration_tracker.export_by_batch(args, current_dir)

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
    instances_to_retry = flex_api_client.get_next_objects(type, filters, offset, limit)

    while offset < total_number_of_results:
        for instance in instances_to_retry:
            instance_id = instance["id"]
            flex_api_client.retry_instance(instance_id, type)
            
        offset+=limit
        instances_to_retry = flex_api_client.get_next_objects(type, filters, offset, limit)

    end_time = time.time()
    duration = end_time - start_time
    print(f"finished in {round(duration)}s.")

def cancel(args):

    start_time = time.time()

    if getattr(args, 'env', None):
        (BASE_URL, USERNAME, PASSWORD) = connect(args.env)
    else:
        (BASE_URL, USERNAME, PASSWORD) = connect('default')
        
    flex_api_client = FlexApiClient(BASE_URL, USERNAME, PASSWORD)

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
            time.sleep(0.05)

    end_time = time.time()
    duration = end_time - start_time
    print(f"finished in {round(duration)}s.")

def cancel_failed_jobs(flex_api_client, args):
    errors = args.errors
    filters = apply_default_filters(args, flex_api_client)

    # Get first total number of results
    result = flex_api_client.get_jobs_batch_by_filter(filters, 0, 1)
    total_results = result["totalCount"]

    offset = 0
    limit = 100
    while (total_results > offset + limit):
        print(f"Getting next jobs from {offset} to {offset + limit}")
        jobs = flex_api_client.get_jobs_batch_by_filter(filters, offset, limit)["jobs"]
        cancel_jobs_by_errors(jobs, flex_api_client, errors)
        offset += limit

def cancel_jobs_by_errors(jobs, flex_api_client, errors):
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