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


BASE_URL = os.environ.get('FRE_SOURCE_BASE_URL')
USERNAME = os.environ.get('FRE_SOURCE_USERNAME')
PASSWORD = os.environ.get('FRE_SOURCE_PASSWORD')

def main():

    parser = argparse.ArgumentParser(description='Flex Remote Executor (FRE) allows you to run commands remotely from your local terminal to Flex.')
    subparsers = parser.add_subparsers(help='Commands')

    # Export
    export_command = subparsers.add_parser('export', help='Export objects to a CSV.')
    export_command.add_argument('--type', type=str, help='Object type : jobs, assets, workflows, etc.')
    export_command.add_argument('--name', type=str, help='Object name : action name, workflow definition name.')
    export_command.add_argument('--filters', type=str, help='Export filters to apply. Example : "status=Failed"')
    export_command.add_argument('--include_error', type=bool, help='Include the job error message if failed.')
    export_command.set_defaults(func=export)

    # Retry
    export_command = subparsers.add_parser('retry', help='Retry failed jobs.')
    export_command.add_argument('--type', type=str, help='Object type : jobs, assets, workflows, etc.')
    export_command.add_argument('--name', type=str, help='Object name : action name, workflow definition name.')
    export_command.add_argument('--filters', type=str, help='Filters to apply. Example : "status=Failed"')
    export_command.set_defaults(func=retry)

    # Cancel
    export_command = subparsers.add_parser('cancel', help='Cancel failed jobs.')
    export_command.add_argument('--type', type=str, help='Object type : jobs, workflows.')
    export_command.add_argument('--name', type=str, help='Object name : action name, workflow definition name.')
    export_command.add_argument('--filters', type=str, help='Filters to apply. Example : "status=Failed"')
    export_command.add_argument('--errors', type=str, help='Error message of jobs to cancel. Example : "Resource item named"')
    export_command.set_defaults(func=cancel)

    args = parser.parse_args()

    #metadataDefinitionName = "Photo  PHO"
            
    # Target environment
    # target_base_url = os.environ.get('FRE_TARGET_BASE_URL')
    # target_username = os.environ.get('FRE_TARGET_USERNAME')
    #target_password = os.environ.get('FRE_TARGET_PASSWORD')

    # metadataDefinitionComparator = MetadataDefinitionComparator(baseUrl, username, password, target_base_url, target_username, target_password)
    # metadataDefinitionComparator.compare_metadata_definitions(metadataDefinitionName)

    if hasattr(args, 'func'):
        # Call the function associated with the command
        args.func(args)
    else:
        # No command was provided, so you can print the help message
        parser.print_help()

    # retry_failed_jobs(flex_api_client, "parse-rs2i-xml", "status=Failed")

    # metadata_migration_tracker.get_metadata_migration_jobs("parse-rs2i-xml", "createdFrom=08 Feb 2024 14:40:00")

    # metadata_migration_tracker.extract_jobs("status=Pending")

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
    errors = ["Resource item name"]
    """

    # retry_failed_jobs_from_workflow(metadata_migration_tracker, flex_api_client, "RS2i Metadata Migration", f"status=Failed")
    
    # cancel_failed_jobs(flex_api_client, "rs2i-xml-import", "status=Failed")

    # extract_published_assets(metadata_migration_tracker)

    # metadata_migration_tracker.get_jobs_errors("rs2i-xml-import", "status=Failed")

    # metadata_migration_tracker.get_assets_full("variant=MDA;metadataDefinitionId=884;metadata=archive-tier:44097265")

def export(args):
    
    flex_api_client = FlexApiClient(BASE_URL, USERNAME, PASSWORD)

    metadata_migration_tracker = MetadataMigrationTracker(flex_api_client)

    type = args.type
    filters = args.filters

    if type == 'jobs':
        include_error = args.include_error

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

        metadata_migration_tracker.export(type, filters, include_error)
    
    elif type == 'assets':
        metadata_migration_tracker.get_assets_full(filters)

def retry(args):
    
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
            time.sleep(1)
            
        offset+=limit
        instances_to_retry = flex_api_client.get_next_objects(type, filters, offset, limit)


def cancel(args):

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
    job_id_list_to_retry = metadata_migration_tracker.get_jobs_by_errors(workflow_definition_name, filters, errors)

    print(f"Number of jobs to retry : {len(job_id_list_to_retry)}")

    for job_id in job_id_list_to_retry:
        if script_path:
            push_job_configuration(flex_api_client, script_path, job_id)
        flex_api_client.retry_job(job_id)
        time.sleep(1)

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

def retry_failed_jobs(flex_api_client, action_name, filters = None, errors = None):
    action_name = action_name
    action_id = flex_api_client.get_action_id(action_name)
    action = flex_api_client.get_action(action_id)
    action_type = action["type"]["name"]
    if filters:
        filters += f";actionId={action_id};actionType={action_type}"
    else: 
        filters = f"actionId={action_id};actionType={action_type}"
    job_id_list_to_retry = flex_api_client.get_jobs_by_filter_df(filters)

    print(f"Number of jobs to retry : {len(job_id_list_to_retry)}")

    for job in job_id_list_to_retry:
        job_id = job["id"]
        try:
            flex_api_client.retry_job(job_id)
        except Exception as e:
            print(f"Unable to retry job {job_id} : ", e)
        time.sleep(1)

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

def get_instances(args, flex_api_client, limit):

    type = args.type
    # only failed objects can be cancelled
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

    instance_list = flex_api_client.get_objects_by_filters(type, filters, limit)

    return instance_list

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