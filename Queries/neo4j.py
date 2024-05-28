from py2neo import Graph, Node, Relationship
from prettytable import PrettyTable

uri = "bolt://localhost:7687"
user = "neo4j"
password = "12345678"

neo4j = Graph(uri, auth=(user, password))

print("Conexão Neo4j realizada com sucesso!")

def run_query1_neo4j():
    query = """
    MATCH (m:Medicine)
    RETURN m.id_medicine AS id, m.m_name AS name, m.m_cost AS cost
    ORDER BY m.m_cost DESC
    """
    result = neo4j.run(query)
    neo4j_results = []
    for record in result:
        neo4j_results.append({
            'id': record['id'],
            'name': record['name'],
            'cost': record['cost']
        })
    return neo4j_results

def run_query2_neo4j():
    query = """
MATCH (p:Patient)-[:HAS_EPISODE]->(e:Episode)
WITH p, COUNT(e) AS episode_count
WHERE episode_count > 3
RETURN p.id_patient AS id_patient, p.patient_fname AS patient_fname, p.patient_lname AS patient_lname, episode_count
ORDER BY episode_count DESC, id_patient ASC
    """
    result = neo4j.run(query)
    neo4j_results = []
    for record in result:
        neo4j_results.append({
            'id_patient': record['id_patient'],
            'patient_fname': record['patient_fname'],
            'patient_lname': record['patient_lname'],
            'episode_count': record['episode_count']
        })
    return neo4j_results

def run_query11_neo4j():
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
def run_query12_neo4j():
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

# Query to Get Total Bill Cost per Patient, ordered
def run_query13_neo4j():
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

# Query to get average hospitalization stay
def run_query14_neo4j():
    query = """
    MATCH (h:Hospitalization)
    RETURN ROUND(AVG(TOFLOAT(duration.inDays(h.admission_date, h.discharge_date).days)), 2) as avg_hospitalization_stay
    """
    result = neo4j.run(query)
    neo4j_results = []
    for record in result:
        neo4j_results.append({
            'avg_hospitalization_stay': record['avg_hospitalization_stay']
        })
    return neo4j_results

if __name__ == "__main__":
    run_query11_neo4j()