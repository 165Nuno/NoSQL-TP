from py2neo import Graph, Node, Relationship
from prettytable import PrettyTable

uri = "bolt://localhost:7687"
user = "neo4j"
password = "12345678"

neo4j = Graph(uri, auth=(user, password))

print("Conexão Neo4j realizada com sucesso!")

def run_query1_neo4j():
    query = """
    MATCH (p:Patient)-[r:HAS_EMERGENCY_CONTACT]->(ec:Emergency_Contact)
    RETURN p.id_patient AS idpatient, p.patient_fname AS patient_fname, p.patient_lname AS patient_lname, 
       ec.contact_name AS contact_name, ec.phone AS phone, ec.relation AS relation
    ORDER BY p.id_patient ASC
    """
    result = neo4j.run(query)
    neo4j_results = []
    for record in result:
        neo4j_results.append({
            'idpatient': record['idpatient'],
            'patient_fname': record['patient_fname'],
            'patient_lname': record['patient_lname'],
            'contact_name': record['contact_name'],
            'phone': record['phone'],
            'relation': record['relation']
        })
    return neo4j_results

# Query to Get Patients with the Most Appointments
def run_query2_neo4j():
    query = """
    MATCH (p:Patient)-[:HAS_EPISODE]->(e:Episode)-[:HAS_APPOINTMENT]->(a:Appointment)
    RETURN p.id_patient AS idpatient, p.patient_fname AS patient_fname, p.patient_lname AS patient_lname, COUNT(a) AS appointment_count
    ORDER BY appointment_count DESC
    """
    result = neo4j.run(query)
    neo4j_results = []
    for record in result:
        neo4j_results.append({
            'idpatient': record['idpatient'],
            'patient_fname': record['patient_fname'],
            'patient_lname': record['patient_lname'],
            'appointment_count': record['appointment_count']
        })
    return neo4j_results

def run_query3_neo4j():
    query = """
    MATCH (p:Patient)-[:HAS_EPISODE]->(e:Episode)-[:HAS_BILL]->(b:Bill)
    RETURN p.id_patient AS idpatient, p.patient_fname AS patient_fname, p.patient_lname AS patient_lname, SUM(b.total) AS sum_total_bill
    ORDER BY sum_total_bill DESC    
    """
    result = neo4j.run(query)
    neo4j_results = []
    for record in result:
        neo4j_results.append({
            'idpatient': record['idpatient'],
            'patient_fname': record['patient_fname'],
            'patient_lname': record['patient_lname'],
            'sum_total_bill': record['sum_total_bill']
        })
    return neo4j_results

if __name__ == "__main__":
    run_query1_neo4j()