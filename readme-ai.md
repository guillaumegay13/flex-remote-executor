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
- [ Getting Started](#-getting-started)
  - [ Installation](#-installation)
  - [ Usage](#-usage)
  - [ Tests](#-tests)
- [ Contributing](#-contributing)
- [ License](#-license)
- [ Acknowledgments](#-acknowledgments)
</details>
<hr>

##  Overview

Flex Remote Executor is a comprehensive software project that facilitates seamless remote job execution and workflow management on the Flex platform. Leveraging robust APIs and efficient handling of JSON configurations, it empowers users to create, update, and cancel jobs, manage metadata, and migrate workflows effortlessly. With dynamic action creation and Groovy script generation capabilities, the project ensures efficient backend task execution. Flex Remote Executors value proposition lies in its ability to streamline job operations, enhance workflow migration accuracy, and provide flexible monitoring and tracking features, making it an indispensable tool for Flex users.

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

Arguments  

> --type: *object type (e.g., env, action, header, workflow, job)*  
> --set-default: *set environment as default (only compatible with --type env)*  
> --env: *environment to use*  
> --name: *object name*  
> --value: *object value*  
> --definitionId: *workflow definition ID*  
> --assetId: *asset ID to launch the job or workflow on*   
> --assetIds: *asset IDs to launch the job or workflow on*  
> --url: *environment URL*  
> --username: *username*  
> --password: *user password*  

#### Export
Exports objects to a CSV.

```
python run.py export --env <ENV> --type <TYPE> --name <NAME> [--filters <FILTERS>] [--include-error] [--include-metadata] [--header <HEADER>] [--uuid <UUID>]
```

Arguments:

> --env: *environment to use*  
> --type: *object type (e.g., jobs, assets, workflows)*  
> --name: *object name (e.g., action name, workflow definition name)*  
> --filters: *export filters to apply (e.g., "status=Failed")*  
> --include-error: *include error details (only useful for failed jobs)*  
> --include-metadata: *include metadata (only useful for assets)*  
> --header: *header for columns to export*  
> --uuid: *object UUID to export*  


#### Retry
Retries failed jobs.

```
python run.py retry --env <ENV> --type <TYPE> --name <NAME> [--filters <FILTERS>] [--id <ID>] [--script-path <SCRIPT_PATH>] [--keep-imports]
```

Arguments  

> --env: *environment to use*  
> --type: *object type (e.g., jobs, workflows)*  
> --name: *object name (e.g., action name, workflow definition name)*  
> --filters: *filters to apply (e.g., "status=Failed")*  
> --id: *object ID to retry*  
> --script-path: *script path to update the job or action*  
> --keep-imports: *keep the import section of the job without updating it with classes from the script (only available with the --script-path flag)*  


#### Cancel
Cancels failed jobs.

```
python run.py cancel --env <ENV> --type <TYPE> --name <NAME> [--filters <FILTERS>] [--errors <ERRORS>]
```

Arguments  

> --env: *environment to use*  
> --type: *object type (e.g., jobs, workflows)*  
> --name: *object name (e.g., action name, workflow definition name)*  
> --filters: *filters to apply (e.g., "status=Failed")*  
> --errors: *error message of jobs to cancel (e.g., "Resource item named")*  

#### Update
Updates an object.

```
python run.py update --env <ENV> --type <TYPE> --id <ID> --script-path <SCRIPT_PATH>
```

Arguments  

> --env: *environment to use*  
> --type: *object type (e.g., job, action)*  
> --id: *pbject ID*  
> --script-path: *script path to update the job or action*  

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
