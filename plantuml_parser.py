# Full code for the PlantUML to SQL parser

from pyparsing import (Word, alphas, alphanums, Suppress, Group, ZeroOrMore,
                       Optional, StringStart, StringEnd, ParseException, Combine,
                       oneOf, Empty)
import re

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

def parse_plantuml_class_to_sql_individual(class_def):
    """
    Parse a single PlantUML class definition to generate an SQL create query, identifying primary keys.

    Args:
    class_def (str): A string containing a single PlantUML class definition.

    Returns:
    str: An SQL create query for the given class definition.
    """
    # Basic definitions for parsing
    identifier = Word(alphas, alphanums + "_")
    datatype = Combine(Word(alphas, alphanums + "_") + Optional(Word(alphanums)))

    # Visibility definition: '+' or '-' or absent
    visibility = oneOf("+ -").setParseAction(lambda tokens: tokens[0].strip()) | Empty().setParseAction(lambda: "")

    # Attribute definition with handling for visibility symbols
    attribute = Group(Optional(visibility) + identifier + Suppress(":") + datatype)

    # Class definition parser
    class_parser = (Suppress("class") + identifier("class_name") + Suppress("{") +
                    Group(ZeroOrMore(attribute))("attributes") + Suppress("}"))

    output = ""
    primary_keys = []  # List to store primary keys
    try:
        parsed_data = class_parser.parseString(class_def)
        output += f"CREATE TABLE {parsed_data.class_name} (\n"
        for attr in parsed_data.attributes:
            # Extracting attribute name, type, and visibility
            visibility, attr_name, attr_type = attr[0], attr[1], attr[2]
            output += f"  {attr_name} {attr_type.upper()},\n"
            # If visibility is '+', it's a primary key
            if visibility == '+':
                primary_keys.append(attr_name)

        # Remove last comma and add primary key clause if primary keys exist
        output = output.rstrip(',\n')
        if primary_keys:
            output += ",\n  PRIMARY KEY (" + ", ".join(primary_keys) + ")\n);\n\n"
        else:
            output += "\n);\n\n"

    except ParseException as pe:
        output = f"Parse error in class definition: {pe}"

    return output

def parse_plantuml_to_sql(preprocessed_code):
    """
    Parse the preprocessed PlantUML code to generate SQL create queries for multiple classes.

    Args:
    preprocessed_code (str): The preprocessed PlantUML code as a string.

    Returns:
    str: SQL create queries generated from the PlantUML code.
    """
    # Use regex to accurately identify class definitions
    class_pattern = re.compile(r'class\s+[\w\s\+\-:]*\{.*?\}', re.DOTALL)
    class_defs = class_pattern.findall(preprocessed_code)

    output = ""
    for class_def in class_defs:
        # Parse each class definition
        output += parse_plantuml_class_to_sql_individual(class_def)

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

'Other Relationships
class Assignment {
  + { employee_id, project_id } : varchar
  - hours_worked : int
}

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


