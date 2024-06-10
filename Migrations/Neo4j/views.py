from py2neo import Graph, Node, Relationship
from prettytable import PrettyTable
from datetime import datetime, date
from interchange.time import DateTime

uri = "bolt://localhost:7687"
user = "neo4j"
password = "12345678"

neo4j = Graph(uri, auth=(user, password))

print("Conexão Neo4j realizada com sucesso!")

# Create view
def get_patient_appointment_view():
    query = """
    MATCH (a:Appointment)-[:HAS_DOCTOR]->(d:Doctor)
    MATCH (d)<-[:IS_DOCTOR]-(s:Staff)-[:WORKS_IN_DEPARTMENT]->(dept:Department)
    MATCH (p:Patient)-[:HAS_EPISODE]->(e:Episode)
    RETURN 
        a.scheduled_on AS appointment_scheduled_date,
        a.appointment_date AS appointment_date,
        a.appointment_time AS appointment_time,
        d.emp_id AS doctor_id,
        d.qualifications AS doctor_qualifications,
        dept.dept_name AS department_name,
        p.patient_fname AS patient_first_name,
        p.patient_lname AS patient_last_name,
        p.blood_type AS patient_blood_type,
        p.phone AS patient_phone,
        p.email AS patient_email,
        p.gender AS patient_gender
    ORDER BY 
        a.scheduled_on
    """
    #    a.scheduled_on AS appointment_scheduled_date,
    #    a.appointment_date AS appointment_date,
    result = neo4j.run(query)
    return result.data()

# convert interchange.time.DateTime object to string with only year, month and year
def convert_datetime_to_string(value):
    if isinstance(value, DateTime):
        # Convert to ISO format and then extract the date part
        return value.iso_format().split('T')[0]
    return str(value) if value is not None else ''

# Print view
def print_patient_appointment_view():
    results = get_patient_appointment_view()
    table = PrettyTable()
    table.field_names = [
        "appointment_scheduled_date", "appointment_date", "appointment_time",
        "doctor_id", "doctor_qualifications", "department_name", 
        "patient_first_name", "patient_last_name", "patient_blood_type", 
        "patient_phone", "patient_email", "patient_gender"
    ]

    for record in results:
        table.add_row([
            convert_datetime_to_string(record["appointment_scheduled_date"]), convert_datetime_to_string(record["appointment_date"]),
            record["appointment_time"], record["doctor_id"], 
            record["doctor_qualifications"], record["department_name"],
            record["patient_first_name"], record["patient_last_name"],
            record["patient_blood_type"], record["patient_phone"],
            record["patient_email"], record["patient_gender"]
        ])

    print(table)

if __name__ == "__main__":
    # run view
    print_patient_appointment_view()