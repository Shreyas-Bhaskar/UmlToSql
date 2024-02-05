from pyparsing import (Word, alphas, alphanums, Suppress, Group, ZeroOrMore,
                       Optional, delimitedList, LineStart, restOfLine,
                       StringStart, StringEnd, ParseException, Combine,
                       OneOrMore, Literal, oneOf,Empty)


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


def parse_plantuml_class_to_sql(preprocessed_code):
    """
    Parse the preprocessed PlantUML code to generate SQL create queries for multiple classes.

    Args:
    preprocessed_code (str): The preprocessed PlantUML code as a string.

    Returns:
    str: SQL create queries generated from the PlantUML code.
    """
    # Split the preprocessed input into individual class definitions
    class_defs = preprocessed_code.split("class")[1:]  # Skip the first split as it will be empty
    class_defs = ["class" + class_def for class_def in class_defs]  # Re-add the 'class' keyword

    output = ""
    for class_def in class_defs:
        # Check if the segment is a class definition and not a relationship or other UML element
        if "{" in class_def and "}" in class_def:
            output += parse_plantuml_class_to_sql(class_def)
        # Future enhancement can be done here to handle relationships

    return output


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
sql_output = parse_plantuml_class_to_sql(preprocessed_input)
print(sql_output)


