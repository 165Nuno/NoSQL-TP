from py2neo import Graph, Node, Relationship
from prettytable import PrettyTable
from datetime import datetime, date
from interchange.time import DateTime

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
    print(neo4j_results)
    return neo4j_results

run_query1_neo4j()

def run_query2_neo4j():
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

run_query2_neo4j()

