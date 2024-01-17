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
   - **Permissions**: Allow creating and updating actions & jobs.
   - **Note**: Additional permissions can be needed in future versions of FRE.

## Step 2: Create a Batch File
1. **Create a New Batch File**: Create a text file and save it with a `.bat` extension, such as `startIntelliJForMyEnv.bat`.
2. **Edit and Configure the Batch File**:
   - Open the file in a text editor.
   - Add commands to set environment variables and to start IntelliJ IDEA in a background process.
   - **Example**:
     ```batch
     @echo off
     SET BASE_URL=<environment_url>/api
     SET USERNAME=<username>
     SET PASSWORD=<password>
     start /B "" "C:\Path\To\IntelliJ IDEA\bin\idea64.exe"
     ```
   - Replace `"C:\Path\To\IntelliJ IDEA\bin\idea64.exe"` with the actual path to your IntelliJ IDEA executable.
   - The `@echo off` command is used to prevent displaying the executed commands.

## Notes
- These scripts set environment variables only for the instance of IntelliJ IDEA they start.
- Keep the batch file in a secure location.

## Step 3: Creating a VBScript to Run Your Batch File
1. **Create a VBScript File**:
   - Create a new text file and rename it with a `.vbs` extension, for example, `startIntelliJForMyEnv.vbs`.
   - Insert the following VBScript code:
     ```vbscript
     Set WshShell = CreateObject("WScript.Shell")
     WshShell.Run chr(34) & "C:\Path\To\Your\startIntelliJForMyEnv.bat" & Chr(34), 0
     Set WshShell = Nothing
     ```
   - Replace `C:\Path\To\Your\startIntelliJForMyEnv.bat` with the full path to your batch file.
2. **Run the VBScript**:
   - Double-click `startIntelliJForMyEnv.vbs` to run the batch file without displaying the command prompt window.

3. **Optional: Create a Shortcut**:
   - Create a shortcut for the VBScript and pin it to your desktop toolbar for easy access.
   - Customize the shortcut icon for better recognition.

## Step 4: Adapt the Settings for your IDE
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
    value="C:\Users\ggay\Documents\flex-remote-executor\main.py $FilePath$ $BASE_URL$ $USERNAME$ $PASSWORD$ create_action"
    value="C:/Users/ggay"
    ```
    - ZIP your `custom_settings` folder into `custom_settings.zip`

## Step 5: Import your Custom Settings to Create the Buttons in your IntelliJ
1. **Import Settings**
    - Click on `Menu`, `File`, `Manage IDE Settings`, `Import Settings` and select the file `custom_settings.zip` in the FRE repository.
    - Click on `OK`, and make sure that the components `Menus and Toolbars Customization` and `Tools` are selected.
    - Click on `OK` to import the settings. You should now see the FRE buttons in the `Run` menu.

For any further details or updates regarding the setup and usage of "flex-remote-executor", please feel free to reach out.
