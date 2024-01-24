from configurations.metadata_definition import get_metadata_definition_fields
from client.flexCmClient import FlexCmClient

# ANSI escape codes for some colors
RED = "\033[31m"     # Red color
GREEN = "\033[32m"   # Green color
YELLOW = "\033[33m"  # Yellow color
BLUE = "\033[34m"    # Blue color
RESET = "\033[0m"    # Reset to default color

class MetadataDefinitionComparator:
    def __init__(self, source_base_url, source_username, source_password, target_base_url, target_username, target_password):

        self.source_flexCmClient = FlexCmClient(source_base_url, source_username, source_password)
        self.target_flexCmClient = FlexCmClient(target_base_url, target_username, target_password)

    def compare_metadata_definitions(self, name):

        self.source_fields = get_metadata_definition_fields(self.source_flexCmClient, name)
        self.target_fields = get_metadata_definition_fields(self.target_flexCmClient, name)

        # Convert objects to sets directly
        source_field_set = {field.attributes for field in self.source_fields}
        target_field_set = {field.attributes for field in self.target_fields}

        # Create dictionaries mapping names to objects
        name_to_field_stg = {field.name: field for field in self.source_fields}
        name_to_field_prod = {field.name: field for field in self.target_fields}

        # Comparisons
        self.common_fields = source_field_set.intersection(target_field_set)
        self.source_unique_field_set = source_field_set.difference(target_field_set)
        self.target_unique_field_set = target_field_set.difference(source_field_set)
        # all_values = source_field_set.union(target_field_set)

        
        # TODO: print in get_fields_differences() is called twice below
        # Change the logic to call it once below, instead that in the get_fields_differences() method
        fields_to_add, differences = self.get_fields_differences(self.source_unique_field_set, name_to_field_stg, name_to_field_prod, True)
        for field_to_add in fields_to_add:
            print(GREEN + "field to add : " + str(field_to_add) + RESET)

        fields_to_remove, differences = self.get_fields_differences(self.target_unique_field_set, name_to_field_prod, name_to_field_stg, False)
        for field_to_remove in fields_to_remove:
            print(RED + "field to remove : " + str(field_to_remove) + RESET)


    # differences_between_lists will contain the differences between the unique objects
    def compare_fields(self, source_field, target_field):
        differences = {}
        # field_stg[-1] is the last attribute, corresponding to the attributesLength
        for attribute in source_field.attributeNames:
            if (attribute in target_field.attributeNames):
                if getattr(source_field, attribute) != getattr(target_field, attribute):
                    differences[attribute] = (getattr(source_field, attribute), getattr(target_field, attribute))
            else:
                differences[attribute] = (getattr(source_field, attribute), "None")

        return differences

    def get_fields_differences(self, source_field_set, source_name_to_field, target_name_to_field, print_differences):
        # Find corresponding objects for detailed comparison
        field_list = []
        for unique_field in source_field_set:
            # To check if an object with a certain name exists
            unique_field_name = unique_field[0]
            displayName = unique_field[1]
            source_field = source_name_to_field[unique_field_name]
            if unique_field_name in target_name_to_field:
                target_field = target_name_to_field[unique_field_name]
                differences = self.compare_fields(source_field, target_field)
                if (print_differences):
                    for attribute, difference in differences.items():
                        print(BLUE + displayName + RESET + ": change " + BLUE + str(attribute) + RESET + " from " + RED + str(difference[1]) + RESET + " to " + GREEN + str(difference[0]).strip() + RESET)
            else:
                field_list.append(unique_field)
        return field_list, differences