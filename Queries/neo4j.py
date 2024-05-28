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

if __name__ == "__main__":
    run_query1_neo4j()