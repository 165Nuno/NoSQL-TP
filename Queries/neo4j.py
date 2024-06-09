from py2neo import Graph, Node, Relationship
from prettytable import PrettyTable
from datetime import datetime, date
from interchange.time import DateTime

uri = "bolt://localhost:7687"
user = "neo4j"
password = "12345678"

neo4j = Graph(uri, auth=(user, password))

print("Conexão Neo4j realizada com sucesso!")

# Lista por ordem descrescente os medicamentos mais caros
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

# Listar pacientes que têm mais de 3 episodes por ordem descrescente
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

# Listar pacientes e as seus contactos de emergência
def run_query3_neo4j():
    query = """
MATCH (p:Patient)-[:HAS_EMERGENCY_CONTACT]->(ec:Emergency_Contact)
RETURN p.id_patient AS id_patient, p.patient_fname AS patient_fname, p.patient_lname AS patient_lname, ec.contact_name AS contact_name, ec.phone AS phone
ORDER BY p.id_patient ASC
    """
    result = neo4j.run(query)
    neo4j_results = []
    for record in result:
        neo4j_results.append({
            'id_patient': record['id_patient'],
            'patient_fname': record['patient_fname'],
            'patient_lname': record['patient_lname'],
            'contact_name': record['contact_name'],
            'phone': record['phone']
        })
    return neo4j_results

# Listar as salas com o maior custo de hospitalização total
def run_query4_neo4j():
    query = """
MATCH (r:Room)<-[:HAS_ROOM]-(h:Hospitalization)<-[:HAS_HOSPITALIZATION]-(e:Episode)-[:HAS_BILL]->(b:Bill)
RETURN r.id_room AS room_id, r.room_type AS room_type, SUM(b.total) AS total_cost
ORDER BY total_cost DESC
    """
    result = neo4j.run(query)
    neo4j_results = []
    for record in result:
        neo4j_results.append({
            'room_id': record['room_id'],
            'room_type': record['room_type'],
            'total_cost': record['total_cost']
        })
    return neo4j_results

# Contar o número de pacientes únicos por tipo de sala
def run_query5_neo4j():
    query = """
MATCH (r:Room)<-[:HAS_ROOM]-(h:Hospitalization)<-[:HAS_HOSPITALIZATION]-(e:Episode)<-[:HAS_EPISODE]-(p:Patient)
RETURN r.room_type AS room_type, COUNT(DISTINCT p.id_patient) AS unique_patient_count
ORDER BY unique_patient_count DESC
    """
    result = neo4j.run(query)
    neo4j_results = []
    for record in result:
        neo4j_results.append({
            'room_type': record['room_type'],
            'unique_patient_count': record['unique_patient_count']
        })
    return neo4j_results

# Listar os tipos de sala e o custo médio por tipo
def run_query6_neo4j():
    query = """
MATCH (r:Room)
RETURN r.room_type AS room_type, AVG(r.room_cost) AS average_cost
ORDER BY average_cost DESC
    """
    result = neo4j.run(query)
    neo4j_results = []
    for record in result:
        neo4j_results.append({
            'room_type': record['room_type'],
            'average_cost': record['average_cost']
        })
    return neo4j_results

# Contar o número de funcionários por departamento, ordenado pelo número de funcionários
def run_query7_neo4j():
    query = """
MATCH (s:Staff)-[:WORKS_IN_DEPARTMENT]->(d:Department)
RETURN d.dept_name AS department_name, COUNT(s) AS staff_count
ORDER BY staff_count DESC
    """
    result = neo4j.run(query)
    neo4j_results = []
    for record in result:
        neo4j_results.append({
            'department_name': record['department_name'],
            'staff_count': record['staff_count']
        })
    return neo4j_results

# O funcionário com mais tempo de serviço ativo
def run_query8_neo4j():
    query = """
MATCH (s:Staff)
WHERE s.is_active_status = 'Y'
WITH s, duration.inDays(date(s.date_joining), date()).days AS days_at_hospital
RETURN s.emp_id AS emp_id, s.emp_fname AS first_name, s.emp_lname AS last_name, 
       ROUND(days_at_hospital / 365.25, 2) AS years_at_hospital
ORDER BY days_at_hospital DESC
LIMIT 1
    """
    result = neo4j.run(query)
    neo4j_results = []
    for record in result:
        neo4j_results.append({
            'emp_id': record['emp_id'],
            'first_name': record['first_name'],
            'last_name': record['last_name'],
            'years_at_hospital': record['years_at_hospital']
        })
    return neo4j_results

# O paciente com mais condições médicas e suas condições
def run_query9_neo4j():
    query = """
MATCH (p:Patient)-[:HAS_MEDICAL_HISTORY]->(mh:Medical_History)
WITH p, COUNT(mh) AS condition_count, COLLECT(mh.condition) AS conditions
RETURN p.id_patient AS id_patient, p.patient_fname AS first_name, p.patient_lname AS last_name,
       condition_count, REDUCE(s = '', condition IN conditions | s + CASE WHEN s = '' THEN '' ELSE ', ' END + condition) AS conditions
ORDER BY condition_count DESC
LIMIT 1
    """
    result = neo4j.run(query)
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

# Listar todas as hospitalizações em uma sala específica
def run_query10_neo4j():
    query = """
MATCH (r:Room)
OPTIONAL MATCH (r)<-[:HAS_ROOM]-(h:Hospitalization)
RETURN r.id_room AS room_id, r.room_type AS room_type, COUNT(h) AS hospitalization_count
ORDER BY hospitalization_count DESC, room_id ASC
    """
    result = neo4j.run(query)
    neo4j_results = []
    for record in result:
        neo4j_results.append({
            'room_id': record['room_id'],
            'room_type': record['room_type'],
            'hospitalization_count': record['hospitalization_count']
        })
    return neo4j_results

# Query to Get Patients with the Most Appointments
def run_query11_neo4j():
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
def run_query12_neo4j():
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
def run_query13_neo4j():
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

# Create procedure
def sp_update_bill_status(p_bill_id, p_paid_value):
    try:
        # Retrieve the total value of the bill
        query = """
        MATCH (b:Bill {id_bill: $p_bill_id})
        RETURN b.total AS total
        """
        v_total = neo4j.run(query, p_bill_id=p_bill_id).evaluate("total")
        if v_total is None:
            raise ValueError(f"No bill found with id {p_bill_id}")
        
        # Check if the paid value is less than the total value of the bill
        if p_paid_value < v_total:
            # If paid value is less than total, update status to FAILURE
            update_query = """
            MATCH (b:Bill {id_bill: $p_bill_id})
            SET b.payment_status = 'FAILURE'
            """
            neo4j.run(update_query, p_bill_id=p_bill_id)

            # Raise an error
            raise ValueError("Paid value is inferior to the total value of the bill.")
        else:
            # If paid value is equal to total, update status to PROCESSED
            update_query = """
            MATCH (b:Bill {id_bill: $p_bill_id})
            SET b.payment_status = 'PROCESSED'
            """
            neo4j.run(update_query, p_bill_id=p_bill_id)

        print("Bill status updated successfully.")
    
    except Exception as e:
        print("Error executing Cypher query:", e)

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
    # run procedure
    sp_update_bill_status(16, 2000)
    # run view
    print_patient_appointment_view()