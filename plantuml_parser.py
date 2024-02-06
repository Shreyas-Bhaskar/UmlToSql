# Full code for the PlantUML to SQL parser

from pyparsing import (Word, alphas, alphanums, Suppress, Group, ZeroOrMore,
                       Optional, StringStart, StringEnd, ParseException, Combine,
                       oneOf, Empty)
import re


def parse_foreign_keys(foreign_keys):
    """
    Revised parsing of foreign key relationships to correctly format SQL foreign key constraints.

    Args:
    foreign_keys (list): A list of strings representing foreign key relationships.

    Returns:
    dict: A dictionary mapping tables to their foreign key constraints.
    """
    fk_dict = {}
    for fk in foreign_keys:
        # Parsing based on the line structure:
        # Department "1" -up- "*" Employee : "< employs"
        parts = fk.split(" ")
        target_table, source_table = parts[0], parts[-2]

        # Assuming foreign key field name is the lowercase table name followed by 'id'
        fk_field = source_table.lower() + "_id"
        if target_table not in fk_dict:
            fk_dict[target_table] = []
        fk_dict[target_table].append(fk_field)

    return fk_dict

def preprocess_plantuml(plantuml_code):
    """
    Preprocess the PlantUML code to extract relevant class definitions and relationships.

    Args:
    plantuml_code (str): The PlantUML code as a string.

    Returns:
    str: Preprocessed PlantUML code with only relevant lines.
    """
    # Keep only class definitions, attribute declarations, and relationships
    lines = plantuml_code.splitlines()
    relevant_lines = []

    class_definition = ""
    capturing = False

    for line in lines:
        stripped_line = line.strip()

        # Start capturing if it's the start of a class definition
        if stripped_line.startswith("class"):
            capturing = True
            class_definition = stripped_line
        elif capturing:
            class_definition += " " + stripped_line
            # End capturing if it's the end of a class definition
            if "}" in stripped_line:
                relevant_lines.append(class_definition)
                class_definition = ""
                capturing = False

    return " ".join(relevant_lines)

def parse_plantuml_class_to_sql_individual(class_def, fk_constraints):
    """
    Parse a single PlantUML class definition to generate an SQL create query, including foreign key constraints.

    Args:
    class_def (str): A string containing a single PlantUML class definition.
    fk_constraints (dict): A dictionary of foreign key constraints.

    Returns:
    str: An SQL create query for the given class definition.
    """
    # Basic definitions for parsing
    identifier = Word(alphas, alphanums + "_")
    datatype = Combine(Word(alphas, alphanums + "_") + Optional(Word(alphanums)))
    visibility = oneOf("+ -").setParseAction(lambda tokens: tokens[0].strip()) | Empty().setParseAction(lambda: "")
    attribute = Group(Optional(visibility) + identifier + Suppress(":") + datatype)
    class_parser = (Suppress("class") + identifier("class_name") + Suppress("{") +
                    Group(ZeroOrMore(attribute))("attributes") + Suppress("}"))

    output = ""
    primary_keys = []  # List to store primary keys
    try:
        parsed_data = class_parser.parseString(class_def)
        class_name = parsed_data.class_name
        output += f"CREATE TABLE {class_name} (\n"
        for attr in parsed_data.attributes:
            visibility, attr_name, attr_type = attr[0], attr[1], attr[2]
            output += f"  {attr_name} {attr_type.upper()},\n"
            if visibility == '+':
                primary_keys.append(attr_name)

        # Remove last comma and add primary key clause if primary keys exist
        output = output.rstrip(',\n')
        if primary_keys:
            output += ",\n  PRIMARY KEY (" + ", ".join(primary_keys) + ")"

        # Add foreign key constraints if any
        if class_name in fk_constraints:
            for fk_field in fk_constraints[class_name]:
                # Assuming the referenced table name is the first part of the foreign key field name
                ref_table = fk_field.rsplit('id', 1)[0].capitalize()
                output += f",\n  FOREIGN KEY ({fk_field}) REFERENCES {ref_table}({fk_field})"

        output += "\n);\n\n"

    except ParseException as pe:
        output = f"Parse error in class definition: {pe}"

    return output

def parse_plantuml_to_sql(preprocessed_code):
    """
    Parse the preprocessed PlantUML code to generate SQL create queries for multiple classes.
    """
    # Extract class definitions and foreign key relationships
    class_defs = re.findall(r'class\s+[\w\s\+\-:]*\{.*?\}', preprocessed_code, re.DOTALL)
    foreign_key_relations = re.findall(r'\w+\s+".*"\s+-[a-z-]+\s+"\*"\s+\w+\s+:.*', preprocessed_code)

    # Parse foreign keys
    fk_constraints = parse_foreign_keys(foreign_key_relations)

    output = ""
    for class_def in class_defs:
        output += parse_plantuml_class_to_sql_individual(class_def, fk_constraints)

    return output
# Example usage:
# plantuml_input = "..."  # Your PlantUML code goes here
# preprocessed_input = preprocess_plantuml(plantuml_input)
# sql_output = parse_plantuml_to_sql(preprocessed_input)
# print(sql_output)


# Example usage
plantuml_input = """
@startuml
hide methods
hide stereotypes

'Top-level entities
class Employee {
  + employee_id : int
  - first_name : varchar
  - last_name : varchar
  - email : varchar
}

class Department {
  + department_id : int
  - department_name : varchar
}

class Project {
  + project_id : int
  - project_name : varchar
}

'Subclasses
class Manager {
  + employee_id : int
}

class Engineer {
  + employee_id : int
}

'Subclass relationships
Employee <|-- Manager
Employee <|-- Engineer


'Aggregation and Composition
Department "1" -up- "*" Employee : "< employs"
Project "*" -right- "*" Employee : "< works on"
Manager "1" -down- "*" Department : "< manages"

@enduml
"""
#Commenting out the execution to prevent it in the PCI
preprocessed_input = preprocess_plantuml(plantuml_input)
print(preprocessed_input)
sql_output = parse_plantuml_to_sql(preprocessed_input)
print(sql_output)


