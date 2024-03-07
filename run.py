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
    export_command.add_argument('--filters', type=str, help='Export filters to apply. Example : "status=Failed"')
    export_command.set_defaults(func=export)


    # Retry
    export_command = subparsers.add_parser('retry', help='Retry failed jobs.')
    export_command.add_argument('--type', type=str, help='Object type : jobs, assets, workflows, etc.')
    export_command.add_argument('--name', type=str, help='Object name : action name, workflow definition name.')
    export_command.add_argument('--filters', type=str, help='Filters to apply. Example : "status=Failed"')
    export_command.set_defaults(func=retry)

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

    metadata_migration_tracker.export(type, filters, True)

def retry(args):
    
    flex_api_client = FlexApiClient(BASE_URL, USERNAME, PASSWORD)

    # metadata_migration_tracker = MetadataMigrationTracker(flex_api_client)

    type = args.type

    # Only failed objects can be retried
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

    print(f"Number of jobs to retry : {len(job_list)}")

    for job in job_list:
        job_id = job["id"]
        flex_api_client.retry_job(job_id)
        time.sleep(0.1)


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

def cancel_failed_jobs(flex_api_client, action_name, filters = None, errors = None):
    action_name = action_name
    action_id = flex_api_client.get_action_id(action_name)
    action = flex_api_client.get_action(action_id)
    action_type = action["type"]["name"]
    if filters:
        filters += f";actionId={action_id};actionType={action_type}"
    else: 
        filters = f"actionId={action_id};actionType={action_type}"
    jobs = flex_api_client.get_jobs_by_filter_df(filters)

    print(f"Number of jobs to cancel : {len(jobs)}")

    for job in jobs:
        job_id = job["id"]
        try:
            cancel_job(flex_api_client, None, job_id)
        except Exception as e:
            print(f"Unable to cancel job {job_id} : ", e)
        time.sleep(0.05)

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


if __name__ == "__main__":
    main()