<p align="center">
  <img src="https://raw.githubusercontent.com/PKief/vscode-material-icon-theme/ec559a9f6bfd399b82bb44393651661b08aaf7ba/icons/folder-markdown-open.svg" width="100" alt="project-logo">
</p>
<p align="center">
    <h1 align="center">FLEX-REMOTE-EXECUTOR</h1>
</p>
<p align="center">
    <em>Elevate Flex workflows with dynamic remote execution!</em>
</p>
<p align="center">
	<img src="https://img.shields.io/github/license/guillaumegay13/flex-remote-executor?style=default&logo=opensourceinitiative&logoColor=white&color=0080ff" alt="license">
	<img src="https://img.shields.io/github/last-commit/guillaumegay13/flex-remote-executor?style=default&logo=git&logoColor=white&color=0080ff" alt="last-commit">
	<img src="https://img.shields.io/github/languages/top/guillaumegay13/flex-remote-executor?style=default&color=0080ff" alt="repo-top-language">
	<img src="https://img.shields.io/github/languages/count/guillaumegay13/flex-remote-executor?style=default&color=0080ff" alt="repo-language-count">
<p>
<p align="center">
	<!-- default option, no dependency badges. -->
</p>

<br><!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary><br>

- [ Overview](#-overview)
- [ Features](#-features)
- [ Repository Structure](#-repository-structure)
- [ Modules](#-modules)
- [ Getting Started](#-getting-started)
  - [ Installation](#-installation)
  - [ Usage](#-usage)
  - [ Tests](#-tests)
- [ Project Roadmap](#-project-roadmap)
- [ Contributing](#-contributing)
- [ License](#-license)
- [ Acknowledgments](#-acknowledgments)
</details>
<hr>

##  Overview

Flex Remote Executor is a comprehensive software project that facilitates seamless remote job execution and workflow management on the Flex platform. Leveraging robust APIs and efficient handling of JSON configurations, it empowers users to create, update, and cancel jobs, manage metadata, and migrate workflows effortlessly. With dynamic action creation and Groovy script generation capabilities, the project ensures efficient backend task execution. Flex Remote Executors value proposition lies in its ability to streamline job operations, enhance workflow migration accuracy, and provide flexible monitoring and tracking features, making it an indispensable tool for Flex users.

---

##  Features

|    | Feature            | Description                                                                                                                                                                                                                                          |
|----|---------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ⚙️  | **Architecture**    | The project has a modular architecture that efficiently interacts with Flex APIs for remote job execution. It handles JSON configurations seamlessly and supports a robust execution workflow.                                                            |
| 🔩 | **Code Quality**    | The codebase maintains good quality and style standards ensuring readability and maintainability. It follows best practices and conventions, making it easier for developers to contribute to the project.                                        |
| 📄 | **Documentation**   | The project has detailed and comprehensive documentation covering various aspects such as project structure, API communication, and workflow actions. The documentation aids in understanding and using the project effectively.                       |
| 🔌 | **Integrations**    | Key integrations include Requests library for HTTP requests, allowing seamless interaction with Flex APIs. External dependencies like Python are utilized for efficient execution of remote operations.                                            |
| 🧩 | **Modularity**      | The codebase exhibits high modularity and reusability by defining specific classes for objects and fields, facilitating structured representation and comparison of various instances in the system.                                              |
| 🧪 | **Testing**         | Testing frameworks and tools used for ensuring code quality are not explicitly mentioned in the details provided.                                                                                                                                    |
| ⚡️  | **Performance**     | The project demonstrates efficiency in handling job executions, API interactions, and resource management. It includes functionality for handling large datasets efficiently, ensuring optimal performance.                                       |
| 🛡️ | **Security**        | Measures for data protection and access control are not explicitly mentioned in the details provided. It is recommended to ensure secure communication with APIs and sensitive data handling.                                                       |
| 📦 | **Dependencies**    | Key external libraries and dependencies include Requests for HTTP requests and Python for executing operations. The project also maintains a `requirements.txt` file listing the necessary dependencies.                                      |
| 🚀 | **Scalability**     | The project showcases scalability by efficiently managing workflow actions, job executions, and API interactions. It can handle increased traffic and load with its structured architecture and robust execution workflow.                      |

---

##  Repository Structure

```sh
└── flex-remote-executor/
    ├── LICENSE
    ├── README.md
    ├── actions
    │   ├── action.py
    │   ├── file.py
    │   └── job.py
    ├── client
    │   ├── flex_api_client.py
    │   └── flex_cm_client.py
    ├── configurations
    │   ├── metadata_definition.py
    │   ├── metadata_definition_comparator.py
    │   └── workflow_migrator.py
    ├── main.py
    ├── monitoring
    │   └── metadata_migration_tracker.py
    ├── objects
    │   └── flex_objects.py
    ├── requirements.txt
    ├── run.py
    └── settings.zip
```

---

##  Modules

<details closed><summary>.</summary>

| File                                                                                                    | Summary                                                                                                                                                                                                                                                                                                      |
| ---                                                                                                     | ---                                                                                                                                                                                                                                                                                                          |
| [run.py](https://github.com/guillaumegay13/flex-remote-executor/blob/master/run.py)                     | Executes operations to export, retry, and cancel jobs remotely on Flex. Supports creating new objects/environments, connecting to specified environments, and managing workflow actions effectively. Efficient handling of JSON configurations and seamless integration with Flex APIs for robust execution. |
| [requirements.txt](https://github.com/guillaumegay13/flex-remote-executor/blob/master/requirements.txt) | Lists dependencies for the project.                                                                                                                                                                                                                                                                          |
| [main.py](https://github.com/guillaumegay13/flex-remote-executor/blob/master/main.py)                   | Executes IntelliJ actions dynamically based on user input, handling various actions including creating, pushing, and comparing metadata and workflows. Retrieves credentials and account info to interact with Flex API and CM clients.                                                                      |

</details>

<details closed><summary>client</summary>

| File                                                                                                               | Summary                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| ---                                                                                                                | ---                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| [flex_cm_client.py](https://github.com/guillaumegay13/flex-remote-executor/blob/master/client/flex_cm_client.py)   | Retrieves workflow and metadata info via HTTP requests. Maps received data to specific objects in the system, aiding in fetching references and structured data efficiently. Empowers the parent repositorys client module with essential retrieval capabilities.                                                                                                                                                                           |
| [flex_api_client.py](https://github.com/guillaumegay13/flex-remote-executor/blob/master/client/flex_api_client.py) | The code file `flex_api_client.py` in the repository `flex-remote-executor` contains a FlexApiClient class that facilitates communication with a remote API using requests. It provides methods for interacting with FlexInstances and FlexAssets, handling authentication with a given base URL, username, and password. The class also includes functionality for increasing the recursion limit for handling large datasets efficiently. |

</details>

<details closed><summary>objects</summary>

| File                                                                                                          | Summary                                                                                                                                                                                                                                                                                                   |
| ---                                                                                                           | ---                                                                                                                                                                                                                                                                                                       |
| [flex_objects.py](https://github.com/guillaumegay13/flex-remote-executor/blob/master/objects/flex_objects.py) | Defines various classes for objects and fields, extending the base FlexObject class. Enables structured representation and comparison of FlexJob, FlexAsset, FlexCmObject, FlexCmResource, FlexMetadataField, FlexTaxonomyField, FlexObjectField, and FlexInstance instances based on defined attributes. |

</details>

<details closed><summary>actions</summary>

| File                                                                                              | Summary                                                                                                                                                                            |
| ---                                                                                               | ---                                                                                                                                                                                |
| [action.py](https://github.com/guillaumegay13/flex-remote-executor/blob/master/actions/action.py) | Implements action creation, configuration, pushing, and pulling for Flex API client in managing actions. Facilitates updating and enabling actions in the repository architecture. |
| [job.py](https://github.com/guillaumegay13/flex-remote-executor/blob/master/actions/job.py)       | Creates, updates, retries, or cancels a job using Flex API based on configuration file content. Critical for managing job executions in the Flex Remote Executor system.           |
| [file.py](https://github.com/guillaumegay13/flex-remote-executor/blob/master/actions/file.py)     | Generates Groovy files with specified class name and package structure in the Flex Remote Executor, facilitating dynamic script creation for backend tasks.                        |

</details>

<details closed><summary>configurations</summary>

| File                                                                                                                                                     | Summary                                                                                                                                                                                                                                              |
| ---                                                                                                                                                      | ---                                                                                                                                                                                                                                                  |
| [metadata_definition.py](https://github.com/guillaumegay13/flex-remote-executor/blob/master/configurations/metadata_definition.py)                       | Retrieves metadata definition fields and creates a text file based on the definition, facilitating data management and storage.                                                                                                                      |
| [metadata_definition_comparator.py](https://github.com/guillaumegay13/flex-remote-executor/blob/master/configurations/metadata_definition_comparator.py) | Compares and identifies field differences between metadata definitions from two systems. Utilizes Flex API and ANSI escape codes for visual feedback.                                                                                                |
| [workflow_migrator.py](https://github.com/guillaumegay13/flex-remote-executor/blob/master/configurations/workflow_migrator.py)                           | Extracts dependencies for workflow migration, ensuring correct order and removing duplicates. Creates dependency files based on workflow objects for project directory. Can handle various action types including transcode, launch, import, script. |

</details>

<details closed><summary>monitoring</summary>

| File                                                                                                                                         | Summary                                                                                                                                                                                                                                                   |
| ---                                                                                                                                          | ---                                                                                                                                                                                                                                                       |
| [metadata_migration_tracker.py](https://github.com/guillaumegay13/flex-remote-executor/blob/master/monitoring/metadata_migration_tracker.py) | Generates CSV exports of jobs, workflows, and assets with flexible filtering options. Enables tracking errors, retrying failed jobs, and batch processing API results in parallel for efficient data extraction in the Flex Remote Executor architecture. |

</details>

---

##  Getting Started

**System Requirements:**

* **Python**: `version x.y.z`

###  Installation

<h4>From <code>source</code></h4>

> 1. Clone the flex-remote-executor repository:
>
> ```console
> $ git clone https://github.com/guillaumegay13/flex-remote-executor
> ```
>
> 2. Change to the project directory:
> ```console
> $ cd flex-remote-executor
> ```
>
> 3. Install the dependencies:
> ```console
> $ pip install -r requirements.txt
> ```

###  Usage

> Run flex-remote-executor using the command below:
> ```console
> $ python run.py
> ```

> [OPTIONAL] Create an alias and add it to your .bashrc file:
> ```
> alias fre='python run.py'
> ```

---

### Commands

#### Create
Creates a new object or environment.
Note: you need to create an environment first to use the other commands!

```
python run.py create --env <ENV> [--set-default] --type <TYPE> --name <NAME> --value <VALUE> [--definitionId <DEFINITION_ID>] [--assetId <ASSET_ID>] [--assetIds <ASSET_IDS>] [--url <URL>] [--username <USERNAME>] [--password <PASSWORD>]
```

**Arguments:**

> --type: Object type (e.g., env, action, header, workflow, job).  
> --set-default: Set environment as default (only compatible with --type env).  
> --env: Environment to use.  
> --name: Object name.  
> --value: Object value.  
> --definitionId: Workflow definition ID.  
> --assetId: Asset ID to launch the job or workflow on.  
> --assetIds: Asset IDs to launch the job or workflow on.  
> --url: Environment URL.  
> --username: Username.  
> --password: User password.  

#### Export
Exports objects to a CSV.

```
python run.py export --env <ENV> --type <TYPE> --name <NAME> [--filters <FILTERS>] [--include-error] [--include-metadata] [--header <HEADER>] [--uuid <UUID>]
```

**Arguments:**

> --env: Environment to use.  
> --type: Object type (e.g., jobs, assets, workflows).  
> --name: Object name (e.g., action name, workflow definition name).  
> --filters: Export filters to apply (e.g., "status=Failed").  
> --include-error: Include error details (only useful for failed jobs).  
> --include-metadata: Include metadata (only useful for assets).  
> --header: Header for columns to export.  
> --uuid: Object UUID to export.  


#### Retry
Retries failed jobs.

```
python run.py retry --env <ENV> --type <TYPE> --name <NAME> [--filters <FILTERS>] [--id <ID>] [--script-path <SCRIPT_PATH>] [--keep-imports]
```

**Arguments:**

> --env: Environment to use.  
> --type: Object type (e.g., jobs, workflows).  
> --name: Object name (e.g., action name, workflow definition name).  
> --filters: Filters to apply (e.g., "status=Failed").  
> --id: Object ID to retry.  
> --script-path: Script path to update the job or action.  
> --keep-imports: Keep the import section of the job without updating it with classes from the script (only available with the --script-path flag).  


#### Cancel
Cancels failed jobs.

```
python run.py cancel --env <ENV> --type <TYPE> --name <NAME> [--filters <FILTERS>] [--errors <ERRORS>]
```

# Arguments:

> --env: Environment to use.  
> --type: Object type (e.g., jobs, workflows).  
> --name: Object name (e.g., action name, workflow definition name).  
> --filters: Filters to apply (e.g., "status=Failed").  
> --errors: Error message of jobs to cancel (e.g., "Resource item named").  

#### Update
Updates an object.

```
python run.py update --env <ENV> --type <TYPE> --id <ID> --script-path <SCRIPT_PATH>
```

**Arguments:**

> --env: Environment to use.  
> --type: Object type (e.g., job, action).  
> --id: Object ID.  
> --script-path: Script path to update the job or action.  

#### Examples

Create a new environment and set it as default:

```
python run.py create --env dev --set-default --type env --name new_environment --url "http://newenv.local" --username admin --password secret
```

Export jobs with specific filters:

```
python run.py export --env production --type jobs --filters "status=Failed" --include-error --header "Job ID,Status,Error"
```

Retry a failed job with a specific ID:

```
python run.py retry --env production --type jobs --id 12345 --script-path /path/to/script.groovy
```

Cancel jobs with a specific error message:

```
python run.py cancel --env production --type jobs --errors "Resource item named"
```

Update an action with a new script:

```
python run.py update --env production --type action --id action123 --script-path /path/to/new/script.groovy
```

---

##  Project Roadmap

- [X] `► INSERT-TASK-1`
- [ ] `► INSERT-TASK-2`
- [ ] `► ...`

---

##  Contributing

Contributions are welcome! Here are several ways you can contribute:

- **[Report Issues](https://github.com/guillaumegay13/flex-remote-executor/issues)**: Submit bugs found or log feature requests for the `flex-remote-executor` project.
- **[Submit Pull Requests](https://github.com/guillaumegay13/flex-remote-executor/blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.
- **[Join the Discussions](https://github.com/guillaumegay13/flex-remote-executor/discussions)**: Share your insights, provide feedback, or ask questions.

<details closed>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your github account.
2. **Clone Locally**: Clone the forked repository to your local machine using a git client.
   ```sh
   git clone https://github.com/guillaumegay13/flex-remote-executor
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to github**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.
8. **Review**: Once your PR is reviewed and approved, it will be merged into the main branch. Congratulations on your contribution!
</details>

<details closed>
<summary>Contributor Graph</summary>
<br>
<p align="center">
   <a href="https://github.com{/guillaumegay13/flex-remote-executor/}graphs/contributors">
      <img src="https://contrib.rocks/image?repo=guillaumegay13/flex-remote-executor">
   </a>
</p>
</details>

---

##  License

This project is protected under the [SELECT-A-LICENSE](https://choosealicense.com/licenses) License. For more details, refer to the [LICENSE](https://choosealicense.com/licenses/) file.

---

##  Acknowledgments

- List any resources, contributors, inspiration, etc. here.

[**Return**](#-overview)

---
