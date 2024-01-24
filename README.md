# flex-remote-executor
Automatize Flex scripts deployments using the B2B API in Python.

flex-remote-executor (FRE) allows you to remotely deploy your Groovy script to Flex from IntelliJ.

The current available actions are :
   - Create File : it creates a new Groovy file with the class name and folder specified in the prompts.
   - Create Action : it deploys your current script into a Flex action.
   - Update Action : it updates the action with the current script.
   - Create Job : it creates a new job in Flex from the action.
   - Retry last Job : it retries the current job in Flex.
   - Update Job : it updates the job with the current script.
   - Cancel Job : it cancels the current job.
   - ... and more to come. 

![image](https://github.com/guillaumegay13/flex-remote-executor/assets/141296636/61eb8b3b-96c3-4d7e-bc43-266749b41f9d)

# Contributions

Feel free to submit feature requests if you think about new actions for FRE.

# Installation Guide

Each environnement needs to be configured to work with FRE.

## Step 1: Create an API User in Flex
1. **Create a User with Limited Permissions**: In Flex, set up a new user specifically for API access. Ensure to restrict permissions:
   - **No access to Core**.
   - **Permissions**: Allow listing, creation, updating objects such as actions, jobs, metadata definitions, resources, etc.
   - **Note**: Additional permissions can be needed in future versions of FRE.

## Step 2: Add environment variables

   ```
   FRE_SOURCE_BASE_URL=<environment_url>/api
   FRE_SOURCE_USERNAME=<username>
   FRE_SOURCE_PASSWORD=<password>
   FRE_TARGET_BASE_URL=<environment_url>/api
   FRE_TARGET_USERNAME=<username>
   FRE_TARGET_PASSWORD=<password>
   ```

## Step 3: Adapt the Settings for your IDE
1. **Extract settings.zip files**
    - Create a new folder `custom_settings`
    - Double-click on `settings.zip` and extract the files in the `custom_settings` folder
2. **Customize the settings**
    - In the `tools` folder, adapt the `External Tools.xml` file to modify the following values :
        - Python executable file path
        - FRE main.py file path
        - Working directory
    - **Example**:
    ```External Tools.xml
    value="C:\Users\ggay\AppData\Local\Programs\Python\Python311\python.exe"
    value="C:\Users\ggay\Documents\flex-remote-executor\main.py $FilePath$ create_action"
    value="C:/Users/ggay"
    ```
    - ZIP your `custom_settings` folder into `custom_settings.zip`

## Note :
   - Unfortunately, it is not possible to use environment variables for those settings. It is a [feature request](https://youtrack.jetbrains.com/issue/IDEA-14429) (opened for 9 years..)

## Step 4: Import your Custom Settings to Create the Buttons in your IntelliJ
1. **Import Settings**
    - Click on `Menu`, `File`, `Manage IDE Settings`, `Import Settings` and select the file `custom_settings.zip` in the FRE repository.
    - Click on `OK`, and make sure that the components `Menus and Toolbars Customization` and `Tools` are selected.
    - Click on `OK` to import the settings. You should now see the FRE buttons in the `Run` menu.

## Optionnal : Automatize the External Tools XML File Generation

   - This section will be updated soon, stay tuned!

For any further details or updates regarding the setup and usage of "flex-remote-executor", please feel free to reach out.