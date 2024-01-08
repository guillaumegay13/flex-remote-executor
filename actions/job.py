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

def update_job(flexApiClient, file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if 'lastJobId : ' in line:
                lastJobId = line.strip().split('lastJobId : ')[1]
    
    if not lastJobId:
        raise Exception("Last Job ID not found. Please create a new job first!")
    
    print(f"Updating job ID {lastJobId}...")
    flexApiClient.update_config(file_path, lastJobId, "job")

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
