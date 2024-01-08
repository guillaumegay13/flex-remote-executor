import sys
import os

def main():

    # Project source path
    project_path = sys.argv[1]
    # Path to the current file in IntelliJ
    className = sys.argv[2]
    file_name = className + ".groovy"

    # Folder name
    if len(sys.argv) == 4:
        folder_name = sys.argv[3]
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
        if (len(sys.argv) == 4):
            file.write(f"package {folder_name}\n\n")
        file.write("import com.ooyala.flex.plugins.GroovyScriptContext\nimport com.ooyala.flex.sdk.FlexSdkClient\n\n")
        file.write(f"class {className} " + '{\n\n')
        file.write("\tGroovyScriptContext context\n\tFlexSdkClient flexSdkClient\n\n")
        file.write("\tdef execute() " + '{\n\t\t\n\t\t\n\t}\n}')

if __name__ == "__main__":
    main()