from pyparsing import Word, alphas, alphanums, Suppress, Group, ZeroOrMore, oneOf, StringStart, StringEnd, \
    ParseException, Optional


def preprocess_plantuml(plantuml_code):
    lines = plantuml_code.splitlines()
    relevant_lines = [line for line in lines if line.strip() and not line.strip().startswith(("'", "@", "hide", "!"))]
    return "\n".join(relevant_lines)


def parse_plantuml_to_sql(preprocessed_code):
    # Basic definitions
    identifier = Word(alphas, alphanums + "_")

    # Class definition - simplified to only get class names
    class_def = Suppress("class") + identifier("class_name")

    # Overall parser structure
    parser = StringStart() + ZeroOrMore(class_def) + StringEnd()

    output = ""
    try:
        parsed_data = parser.parseString(preprocessed_code)
        for item in parsed_data:
            if 'class_name' in item:
                output += f"Found class: {item.class_name}\n"

    except ParseException as pe:
        output = f"Parse error: {pe}"

    return output


# Example usage
plantuml_input = """
@startuml
!define TABLE(text) class text << (T,orchid) >>
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

@enduml
"""

preprocessed_input = preprocess_plantuml(plantuml_input)
print(preprocessed_input)
print(parse_plantuml_to_sql(preprocessed_input))
