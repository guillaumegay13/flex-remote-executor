def create_job(flexApiClient, file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if 'actionId : ' in line:
                actionId = line.strip().split('actionId : ')[1]
                actionIdIndex = lines.index(line)
                # Index to insert the jobId, after actionUuid
                index = actionIdIndex + 2
                break
        
        for line in lines:
            if 'lastJobId : ' in line:
                lines.remove(line)
                break

    print("Launching job...")
    response = flexApiClient.create_job(actionId)

    jobId = response["id"]
    print(f"Launched job ID {jobId}")

    # Add job ID
    lines.insert(index, f'\tlastJobId : {jobId}\n')

    with open(file_path, 'w') as file:
        file.writelines(lines)

def push_job_configuration(flexApiClient, file_path, job_id = None, keep_imports = False):
    if not job_id:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if 'lastJobId : ' in line:
                    lastJobId = line.strip().split('lastJobId : ')[1]
                    job_id = lastJobId
        
        if not lastJobId:
            raise Exception("Last Job ID not found. Please create a new job first!")
    
    print(f"Updating job ID {job_id}...")
    flexApiClient.push_object_configuration(file_path, job_id, "job", keep_imports)

def update_and_retry_last_job(flexApiClient, file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    for line in lines:
        if 'lastJobId : ' in line:
            lastJobId = line.strip().split('lastJobId : ')[1]
    
    if not lastJobId:
        raise Exception("Last Job ID not found. Please create a new job first!")
    
    push_job_configuration(flexApiClient, file_path, lastJobId)

    print(f"Retrying job ID {lastJobId}...")
    flexApiClient.retry_job(lastJobId)

def retry_last_job(flexApiClient, file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    for line in lines:
        if 'lastJobId : ' in line:
            lastJobId = line.strip().split('lastJobId : ')[1]
    
    if not lastJobId:
        raise Exception("Last Job ID not found. Please create a new job first!")
    
    print(f"Retrying job ID {lastJobId}...")
    flexApiClient.retry_job(lastJobId)

def cancel_job(flexApiClient, file_path = None, job_id = None):
    if not job_id:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        for line in lines:
            if 'lastJobId : ' in line:
                lastJobId = line.strip().split('lastJobId : ')[1]
                job_id = lastJobId
        
        if not lastJobId:
            raise Exception("Last Job ID not found. Please create a new job first!")
    
    print(f"Cancelling job ID {job_id}...")
    flexApiClient.cancel_job(job_id)