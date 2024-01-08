import os

def create_file(project_path, className, folder_name=None):

    file_name = className + ".groovy"

    # Folder name
    if folder_name:
        file_path = project_path + '/' + folder_name + '/' + file_name

        # Extract the directory path from the file path
        directory = os.path.dirname(file_path)

        # Create the directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)
    else:
        file_path = project_path + '/' + file_name

    # Create new file
    with open(file_path, "w") as file:
        if (folder_name):
            file.write(f"package {folder_name}\n\n")
        file.write("import com.ooyala.flex.plugins.GroovyScriptContext\nimport com.ooyala.flex.sdk.FlexSdkClient\n\n")
        file.write(f"class {className} " + '{\n\n')
        file.write("\tGroovyScriptContext context\n\tFlexSdkClient flexSdkClient\n\n")
        file.write("\tdef execute() " + '{\n\t\t\n\t\t\n\t}\n}')