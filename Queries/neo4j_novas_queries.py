from py2neo import Graph, Node, Relationship
from prettytable import PrettyTable
from datetime import datetime, date
from interchange.time import DateTime
import json

uri = "bolt://localhost:7687"
user = "neo4j"
password = "12345678"

neo4j = Graph(uri, auth=(user, password))

print("Conexão Neo4j realizada com sucesso!")

def run_query1_neo4j_nova():
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
    print(neo4j_results)
    return neo4j_results

#run_query1_neo4j()

def run_query2_neo4j_nova():
    query = """
    MATCH (p:Patient)-[:HAS_EPISODE]->(e:Episode)
    WITH p, COUNT(e) AS episode_count
    WHERE episode_count > 3
    RETURN p.idpatient AS id_patient, p.patient_fname AS patient_fname, p.patient_lname AS patient_lname, episode_count
    ORDER BY episode_count DESC, p.idpatient ASC
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
    print(neo4j_results)
    return neo4j_results

#run_query2_neo4j()

def run_query3_neo4j_nova():
    query = """
    MATCH (p:Patient)
    RETURN p.idpatient AS id_patient, 
           p.patient_fname AS patient_fname, 
           p.patient_lname AS patient_lname, 
           p.emergency_contacts AS emergency_contacts
    ORDER BY id_patient ASC
    """
    
    results = neo4j.run(query).data()
    final_results = []
    for result in results:
        id_patient = result['id_patient']
        patient_fname = result['patient_fname']
        patient_lname = result['patient_lname']
        emergency_contacts = json.loads(result['emergency_contacts'])
        if emergency_contacts:
            for contact in emergency_contacts:
                final_results.append({
                    'id_patient': id_patient,
                    'patient_fname': patient_fname,
                    'patient_lname': patient_lname,
                    'contact_name': contact['NAME'],
                    'phone': contact['PHONE']
                })
    print(final_results)
    return final_results

#run_query3_neo4j()

def run_query4_neo4j_nova():
    cypher_query = """
    MATCH (r:Room)<-[:HOSPITALIZED_IN]-(e:Episode)-[:HAS_BILL]->(b:Bill)
    WITH r, SUM(b.total) AS total_cost
    WHERE total_cost IS NOT NULL
    RETURN r.idroom AS room_id, r.type AS room_type, total_cost
    ORDER BY total_cost DESC
    """

    result = neo4j.run(cypher_query)
    neo4j_results = []
    for record in result:
        neo4j_results.append({
            'room_id': record['room_id'],
            'room_type': record['room_type'],
            'total_cost': record['total_cost']
        })
    return neo4j_results


def run_query5_neo4j_nova():
    cypher_query = """
    MATCH (r:Room)<-[:HOSPITALIZED_IN]-(e:Episode)<-[:HAS_EPISODE]-(p:Patient)
    RETURN r.type AS room_type, COUNT(DISTINCT p.idpatient) AS unique_patient_count
    ORDER BY unique_patient_count DESC
    """

    result = neo4j.run(cypher_query)
    neo4j_results = []
    for record in result:
        neo4j_results.append({
            'room_type': record['room_type'],
            'unique_patient_count': record['unique_patient_count']
        })
    return neo4j_results

def run_query6_neo4j_nova():
    cypher_query = """
    MATCH (r:Room)
    RETURN r.type AS room_type, AVG(r.cost) AS average_cost
    ORDER BY average_cost DESC
    """

    result = neo4j.run(cypher_query)
    neo4j_results = []
    for record in result:
        neo4j_results.append({
            'room_type': record['room_type'],
            'average_cost': record['average_cost']
        })
    return neo4j_results


def run_query7_neo4j_nova():
    cypher_query = """
    MATCH (s:Staff)-[:WORKS_IN_DEPARTMENT]->(d:Department)
    RETURN d.name AS department_name, COUNT(s) AS staff_count
    ORDER BY staff_count DESC
    """

    result = neo4j.run(cypher_query)
    neo4j_results = []
    for record in result:
        neo4j_results.append({
            'department_name': record['department_name'],
            'staff_count': record['staff_count']
        })
    return neo4j_results


def run_query8_neo4j_nova():
    cypher_query = """
    MATCH (s:Staff)
    WHERE s.is_active_status = 'Y'
    WITH s, duration.inDays(date(s.date_joining), date()).days AS days_at_hospital
    RETURN s.emp_id AS emp_id, s.first_name AS first_name, s.last_name AS last_name, 
        ROUND(days_at_hospital / 365.25, 1) AS years_at_hospital
    ORDER BY days_at_hospital DESC
    LIMIT 1
    """

    result = neo4j.run(cypher_query)
    neo4j_results = []
    for record in result:
        neo4j_results.append({
            'emp_id': record['emp_id'],
            'first_name': record['first_name'],
            'last_name': record['last_name'],
            'years_at_hospital': record['years_at_hospital']
        })
    return neo4j_results


def run_query9_neo4j_nova():
    cypher_query = """
    MATCH (p:Patient)-[:HAS_MEDICAL_HISTORY]->(mh:Medical_History)
    WITH p, COUNT(mh) AS condition_count, COLLECT(mh.condition) AS conditions
    RETURN p.idpatient AS id_patient, p.patient_fname AS first_name, p.patient_lname AS last_name,
        condition_count, REDUCE(s = '', condition IN conditions | s + CASE WHEN s = '' THEN '' ELSE ', ' END + condition) AS conditions
    ORDER BY condition_count DESC
    LIMIT 1
    """

    result = neo4j.run(cypher_query)
    neo4j_results = []
    for record in result:
        neo4j_results.append({
            'id_patient': record['id_patient'],
            'first_name': record['first_name'],
            'last_name': record['last_name'],
            'condition_count': record['condition_count'],
            'conditions': record['conditions']
        })
    return neo4j_results

def run_query10_neo4j_nova():
    cypher_query = """
    MATCH (r:Room)
    OPTIONAL MATCH (r)<-[:HOSPITALIZED_IN]-(e:Episode)
    RETURN r.idroom AS room_id, r.type AS room_type, COUNT(e) AS hospitalization_count
    ORDER BY hospitalization_count DESC, r.idroom ASC
    """

    result = neo4j.run(cypher_query)
    neo4j_results = []
    for record in result:
        neo4j_results.append({
            'room_id': record['room_id'],
            'room_type': record['room_type'],
            'hospitalization_count': record['hospitalization_count']
        })
    return neo4j_results


def run_query11_neo4j_nova():
    query = """
MATCH (p:Patient)-[:HAS_EPISODE]->(e:Episode)
WHERE e.appointment_time IS NOT NULL
RETURN p.idpatient AS idpatient, p.patient_fname AS patient_fname, p.patient_lname AS patient_lname, COUNT(e) AS appointment_count
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
def run_query12_neo4j_nova():
    query = """
MATCH (p:Patient)-[:HAS_EPISODE]->(e:Episode)-[:HAS_BILL]->(b:Bill)
RETURN p.idpatient AS idpatient, p.patient_fname AS patient_fname, p.patient_lname AS patient_lname, SUM(b.total) AS sum_total_bill
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

def run_query13_neo4j_nova():
    query = """
MATCH (e:Episode)
WHERE e.room IS NOT NULL
RETURN ROUND(AVG(TOFLOAT(duration.inDays(e.admission_date, e.discharge_date).days)), 2) as avg_hospitalization_stay
    """
    result = neo4j.run(query)
    neo4j_results = []
    for record in result:
        neo4j_results.append({
            'avg_hospitalization_stay': record['avg_hospitalization_stay']
        })
    return neo4j_results



