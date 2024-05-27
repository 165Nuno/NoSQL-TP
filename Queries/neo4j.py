from py2neo import Graph, Node, Relationship
from prettytable import PrettyTable

uri = "bolt://localhost:7687"
user = "neo4j"
password = "12345678"

neo4j = Graph(uri, auth=(user, password))

query = """
    MATCH (p:Patient)-[r:HAS_EMERGENCY_CONTACT]->(ec:Emergency_Contact)
    RETURN p.id_patient AS idpatient, p.patient_fname AS patient_fname, p.patient_lname AS patient_lname, 
       ec.contact_name AS contact_name, ec.phone AS phone, ec.relation AS relation
    ORDER BY p.id_patient ASC
    """
result = neo4j.run(query)

table = PrettyTable()
table.field_names = ["Patient ID", "First Name", "Last Name", "Contact Name", "Phone", "Relation"]

for record in result:
    table.add_row([record['idpatient'], record['patient_fname'], record['patient_lname'], 
                   record['contact_name'], record['phone'], record['relation']])

print(table)

