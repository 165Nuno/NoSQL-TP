import oracledb
from py2neo import Graph, Node, Relationship
import time
print("Inicio da migração para Neo4j")
inicio = time.time()
oracle_connection = oracledb.connect(user="sys", password="<12345>",
#oracle_connection = oracledb.connect(user="sys", password="password",
                              dsn="localhost:1521/xe", mode=oracledb.SYSDBA)

print("Conexão Oracle realizada com sucesso!")
uri = "bolt://localhost:7687"
user = "neo4j"
password = "12345678"

neo4j = Graph(uri, auth=(user, password))
print("Conexão Neo4j realizada com sucesso!")

# Consultas SQL para obters os dados das tabelas
sql_medical_history = "SELECT * FROM SYSTEM.MEDICAL_HISTORY"
sql_medicine = "SELECT * FROM SYSTEM.MEDICINE"
sql_room = "SELECT * FROM SYSTEM.ROOM"
sql_patient = "SELECT * FROM SYSTEM.PATIENT"
sql_prescription = "SELECT * FROM SYSTEM.PRESCRIPTION"
sql_hospitalization = "SELECT * FROM SYSTEM.HOSPITALIZATION"
sql_nurse = "SELECT * FROM SYSTEM.NURSE"
sql_department = "SELECT * FROM SYSTEM.DEPARTMENT"
sql_insurance = "SELECT * FROM SYSTEM.INSURANCE"
sql_episode = "SELECT * FROM SYSTEM.EPISODE"
sql_appointment = "SELECT * FROM SYSTEM.APPOINTMENT"
sql_doctor = "SELECT * FROM SYSTEM.DOCTOR"
sql_staff = "SELECT * FROM SYSTEM.STAFF"
sql_emergency_contact = "SELECT * FROM SYSTEM.EMERGENCY_CONTACT"
sql_bill = "SELECT * FROM SYSTEM.BILL"
sql_lab_screening = "SELECT * FROM SYSTEM.LAB_SCREENING"
sql_technician = "SELECT * FROM SYSTEM.TECHNICIAN"


def clear_neo4j_database(neo4j):
    """Delete all nodes and relationships in the Neo4j database."""
    apagar_query = """
    MATCH (n) DETACH DELETE n
    """
    neo4j.run(apagar_query)
    print("Dados presentes na base de dados Neo4j apagados!")

def create_relationships(neo4j):
    """Create relationships between nodes in the Neo4j database."""
    patient_nodes = neo4j.nodes.match("Patient")
    for patient_node in patient_nodes:
        medical_history_nodes = neo4j.nodes.match("Medical_History", id_patient=patient_node["id_patient"])

        for medical_history_node in medical_history_nodes:
            relationship = Relationship(patient_node, "HAS_MEDICAL_HISTORY", medical_history_node)
            neo4j.create(relationship)

    patient_nodes = neo4j.nodes.match("Patient")
    for patient_node in patient_nodes:
        insurance_node = neo4j.nodes.match("Insurance", policy_number=patient_node["policy_number"]).first()
        
        if insurance_node:
            relationship = Relationship(patient_node, "HAS_INSURANCE", insurance_node)
            neo4j.create(relationship)


    # [STAFF] -> [DOCTOR]
    doctor_nodes = neo4j.nodes.match("Doctor")
    for doctor_node in doctor_nodes:
        staff_node = neo4j.nodes.match("Staff", emp_id=doctor_node["emp_id"]).first()
        
        if staff_node:
            relationship = Relationship(staff_node, "IS_DOCTOR", doctor_node)
            neo4j.create(relationship)

    # [STAFF] -> [NURSE]
    nurse_nodes = neo4j.nodes.match("Nurse")
    for nurse_node in nurse_nodes:
        staff_node = neo4j.nodes.match("Staff", emp_id=nurse_node["emp_id"]).first()
        
        if staff_node:
            relationship = Relationship(staff_node, "IS_NURSE", nurse_node)
            neo4j.create(relationship)

    # [STAFF] -> [TECHNICIAN]
    staff_nodes = neo4j.nodes.match("Staff")
    for staff_node in staff_nodes:
        technician_node = neo4j.nodes.match("Technician", emp_id=staff_node["emp_id"]).first()

        if technician_node:
            relationship = Relationship(staff_node, "IS_TECHNICIAN", technician_node)
            neo4j.create(relationship)


    # [PATIENT] -> [EPISODE]
    patient_nodes = neo4j.nodes.match("Patient")
    for patient_node in patient_nodes:
        episode_nodes = neo4j.nodes.match("Episode", id_patient=patient_node["id_patient"])

        for episode_node in episode_nodes:
            relationship = Relationship(patient_node, "HAS_EPISODE", episode_node)
            neo4j.create(relationship)

    # [PATIENT] -> [EMERGENCY_CONTACT]
    patient_nodes = neo4j.nodes.match("Patient")
    for patient_node in patient_nodes:
        emergency_contact_nodes = neo4j.nodes.match("Emergency_Contact", id_patient=patient_node["id_patient"])
        
        for emergency_node in emergency_contact_nodes:
            relationship = Relationship(patient_node, "HAS_EMERGENCY_CONTACT", emergency_node)
            neo4j.create(relationship)
       

    # [EPISODE] -> [BILL]
    bill_nodes = neo4j.nodes.match("Bill")
    for bill_node in bill_nodes:
        episode_node = neo4j.nodes.match("Episode", id_episode=bill_node["ip_episode"]).first()
        
        if episode_node:
            relationship = Relationship(episode_node, "HAS_BILL", bill_node)
            neo4j.create(relationship)

    # [EPISODE] -> [PRESCRIPTION]
    prescription_nodes = neo4j.nodes.match("Prescription")
    for prescription_node in prescription_nodes:
        episode_node = neo4j.nodes.match("Episode", id_episode=prescription_node["id_episode"]).first()
        
        if episode_node:
            relationship = Relationship(episode_node, "HAS_PRESCRIPTION", prescription_node)
            neo4j.create(relationship)

    # [PRESCRIPTION] -> [MEDICINE]
    prescription_nodes = neo4j.nodes.match("Prescription")
    for prescription_node in prescription_nodes:
        medicine_node = neo4j.nodes.match("Medicine", id_medicine=prescription_node["id_medicine"]).first()
        
        if medicine_node:
            relationship = Relationship(prescription_node, "PRESCRIBED_MEDICINE", medicine_node)
            neo4j.create(relationship)

    
    # [EPISODE] -> [HOSPITALIZATION]
    hospitalization_nodes = neo4j.nodes.match("Hospitalization")
    for hospitalization_node in hospitalization_nodes:
        episode_node = neo4j.nodes.match("Episode", id_episode=hospitalization_node["id_episode"]).first()
        
        if episode_node:
            relationship = Relationship(episode_node, "HAS_HOSPITALIZATION", hospitalization_node)
            neo4j.create(relationship)
    
    # [HOSPITALIZATION] -> [ROOM]
    hospitalization_nodes = neo4j.nodes.match("Hospitalization")
    for hospitalization_node in hospitalization_nodes:
        room_node = neo4j.nodes.match("Room", id_room=hospitalization_node["id_room"]).first()
        
        if room_node:
            relationship = Relationship(hospitalization_node, "HAS_ROOM", room_node)
            neo4j.create(relationship)

    # [HOSPITALIZATION] -> [NURSE]
    hospitalization_nodes = neo4j.nodes.match("Hospitalization")
    for hospitalization_node in hospitalization_nodes:
        nurse_node = neo4j.nodes.match("Nurse", emp_id=hospitalization_node["responsible_nurse"]).first()
        
        if nurse_node:
            relationship = Relationship(hospitalization_node, "HAS_NURSE", nurse_node)
            neo4j.create(relationship)
        
    # [EPISODE] -> [APPOINTMENT]  
    episode_nodes = neo4j.nodes.match("Episode")
    for episode_node in episode_nodes:
        appointment_node = neo4j.nodes.match("Appointment", id_episode=episode_node["id_episode"]).first()
        
        if appointment_node:
            relationship = Relationship(episode_node, "HAS_APPOINTMENT", appointment_node)
            neo4j.create(relationship)

    # [APPOINTMENT] -> [DOCTOR]  
    appointment_nodes = neo4j.nodes.match("Appointment")
    for appointment_node in appointment_nodes:
        doctor_node = neo4j.nodes.match("Doctor", emp_id=appointment_node["id_doctor"]).first()
        
        if doctor_node:
            relationship = Relationship(appointment_node, "HAS_DOCTOR", doctor_node)
            neo4j.create(relationship)

    # [STAFF] -> [DEPARTMENT]  
    department_nodes = neo4j.nodes.match("Department")
    for department_node in department_nodes:
        staff_nodes = neo4j.nodes.match("Staff", id_department=department_node["id_department"])

        for staff_node in staff_nodes:
            relationship = Relationship(staff_node, "WORKS_IN_DEPARTMENT", department_node)
            neo4j.create(relationship)

    # [LAB_SCREENING] -> [TECHNICIAN]  
    lab_screening_nodes = neo4j.nodes.match("Lab_Screening")
    for lab_screening_node in lab_screening_nodes:
        technician_node = neo4j.nodes.match("Technician", emp_id=lab_screening_node["id_technician"]).first()
        if technician_node:
            relationship = Relationship(lab_screening_node, "PERFORMED_BY", technician_node)
            neo4j.create(relationship)

    # [LAB_SCREENING] -> [EPISODE]  
    for lab_screening_node in lab_screening_nodes:
        episode_node = neo4j.nodes.match("Episode", id_episode=lab_screening_node["id_episode"]).first()
        if episode_node:
            relationship = Relationship(lab_screening_node, "BELONGS_TO_EPISODE", episode_node)
            neo4j.create(relationship)

def create_nodes(neo4j):
    # Dados da tabela medical_history
    cursor.execute(sql_medical_history)
    for row in cursor:
        medical_history_node = Node("Medical_History",
                         record_id=row[0],
                         condition=row[1],
                         record_date=row[2],
                         id_patient=row[3])
        neo4j.create(medical_history_node)

    # Dados da tabela medicine
    cursor.execute(sql_medicine)
    for row in cursor:
        medicine_node = Node("Medicine",
                         id_medicine=row[0],
                         m_name=row[1],
                         m_quantity=row[2],
                         m_cost=row[3])
        neo4j.create(medicine_node)

    # Dados da tabela room
    cursor.execute(sql_room)
    for row in cursor:
        room_node = Node("Room",
                         id_room=row[0],
                         room_type=row[1],
                         room_cost=row[2])
        neo4j.create(room_node)

    # Dados da tabela patient
    cursor.execute(sql_patient)
    for row in cursor:
        patient_node = Node("Patient",
                         id_patient=row[0],
                         patient_fname=row[1],
                         patient_lname=row[2],
                         blood_type=row[3],
                         phone=row[4],
                         email=row[5],
                         gender=row[6],
                         policy_number=row[7],
                         birthday=row[8])
        neo4j.create(patient_node)

    # Dados da tabela prescription
    cursor.execute(sql_prescription)
    for row in cursor:
        prescription_node = Node("Prescription",
                         id_prescription=row[0],
                         prescription_date=row[1],
                         dosage=row[2],
                         id_medicine=row[3],
                         id_episode=row[4])
        neo4j.create(prescription_node)

    # Dados da tabela hospitalization
    cursor.execute(sql_hospitalization)
    for row in cursor:
        hospitalization_node = Node("Hospitalization",
                         admission_date=row[0],
                         discharge_date=row[1],
                         id_room=row[2],
                         id_episode=row[3],
                         responsible_nurse=row[4])
        neo4j.create(hospitalization_node)

    # Dados da tabela nurse
    cursor.execute(sql_nurse)
    for row in cursor:
        nurse_node = Node("Nurse",
                         emp_id=row[0])
        neo4j.create(nurse_node)
    
    # Dados da tabela insurance
    cursor.execute(sql_insurance)
    for row in cursor:
        insurance_node = Node("Insurance",
                         policy_number=row[0],
                         provider=row[1],
                         insurance_plan=row[2],
                         co_pay=row[3],
                         coverage=row[4],
                         maternity=row[5],
                         dental=row[6],
                         optical=row[7])
        neo4j.create(insurance_node)
    
    # Dados da tabela episode
    cursor.execute(sql_episode)
    for row in cursor:
        episode_node = Node("Episode",
                         id_episode=row[0],
                         id_patient=row[1])
        neo4j.create(episode_node)
    
    # Dados da tabela appointment
    cursor.execute(sql_appointment)
    for row in cursor:
        appointment_node = Node("Appointment",
                         scheduled_on=row[0],
                         appointment_date=row[1],
                         appointment_time=row[2],
                         id_doctor=row[3],
                         id_episode=row[4])
        neo4j.create(appointment_node)

    # Dados da tabela doctor
    cursor.execute(sql_doctor)
    for row in cursor:
        doctor_node = Node("Doctor",
                         emp_id=row[0],
                         qualifications=row[1])
        neo4j.create(doctor_node)

    # Dados da tabela staff
    cursor.execute(sql_staff)
    for row in cursor:
        staff_node = Node("Staff",
                         emp_id=row[0],
                         emp_fname=row[1],
                         emp_lname=row[2],
                         date_joining=row[3],
                         date_seperation=row[4],
                         email=row[5],
                         address=row[6],
                         ssn=row[7],
                         id_department=row[8],
                         is_active_status=row[9])
        neo4j.create(staff_node)

    # Dados da tabela emergency_contact
    cursor.execute(sql_emergency_contact)
    for row in cursor:
        emergency_contact_node = Node("Emergency_Contact",
                         contact_phone=row[0],
                         phone=row[1],
                         relation=row[2],
                         id_patient=row[3])
        neo4j.create(emergency_contact_node)

    # Dados da tabela bill
    cursor.execute(sql_bill)
    for row in cursor:
        bill_node = Node("Bill",
                         id_bill=row[0],
                         room_cost=row[1],
                         test_cost=row[2],
                         other_charges=row[3],
                         total=row[4],
                         ip_episode=row[5],
                         registered_at=row[6],
                         payment_status=row[7])
        neo4j.create(bill_node)

    # Dados da tabela lab_screening
    cursor.execute(sql_lab_screening)
    for row in cursor:
        lab_screening_node = Node("Lab_Screening",
                         lab_id=row[0],
                         test_cost=row[1],
                         test_date=row[2],
                         id_technician=row[3],
                         id_episode=row[4])
        neo4j.create(lab_screening_node)

    # Dados da tabela technician
    cursor.execute(sql_technician)
    for row in cursor:
        techincian_node = Node("Technician",
                         emp_id=row[0])
        neo4j.create(techincian_node)

    # Dados da tabela department
    cursor.execute(sql_department)
    for row in cursor:
        department_node = Node("Department",
                               id_department=row[0],
                               dept_head=row[1],
                               dept_name=row[2],
                               emp_count=row[3])
        neo4j.create(department_node)

def initialize_neo4j(neo4j):
    clear_neo4j_database(neo4j)
    create_nodes(neo4j)
    create_relationships(neo4j)

def check_relationship_counts(neo4j):
    """Check and print the number of pairs for each relationship in the Neo4j database."""
    queries = [
        ("Patient HAS_MEDICAL_HISTORY Medical_History", "MATCH (p:Patient)-[:HAS_MEDICAL_HISTORY]->(mh:Medical_History) RETURN COUNT(*) AS count"),
        ("Episode HAS_PRESCRIPTION Prescription", "MATCH (e:Episode)-[:HAS_PRESCRIPTION]->(pr:Prescription) RETURN COUNT(*) AS count"),
        ("Lab_Screening PERFORMED_BY Technician", "MATCH (ls:Lab_Screening)-[:PERFORMED_BY]->(t:Technician) RETURN COUNT(*) AS count"),
        ("Lab_Screening BELONGS_TO_EPISODE Episode", "MATCH (ls:Lab_Screening)-[:BELONGS_TO_EPISODE]->(e:Episode) RETURN COUNT(*) AS count"),
        ("Staff IS_DOCTOR Doctor", "MATCH (s:Staff)-[:IS_DOCTOR]->(d:Doctor) RETURN COUNT(*) AS count"),
        ("Staff IS_NURSE Nurse", "MATCH (s:Staff)-[:IS_NURSE]->(n:Nurse) RETURN COUNT(*) AS count"),
        ("Patient HAS_INSURANCE Insurance", "MATCH (p:Patient)-[:HAS_INSURANCE]->(i:Insurance) RETURN COUNT(*) AS count"),
        ("Hospitalization HAS_ROOM Room", "MATCH (h:Hospitalization)-[:HAS_ROOM]->(r:Room) RETURN COUNT(*) AS count"),
        ("Episode HAS_BILL Bill", "MATCH (e:Episode)-[:HAS_BILL]->(b:Bill) RETURN COUNT(*) AS count"),
        ("Appointment HAS_DOCTOR Doctor", "MATCH (a:Appointment)-[:HAS_DOCTOR]->(d:Doctor) RETURN COUNT(*) AS count"),
        ("Prescription PRESCRIBED_MEDICINE Medicine", "MATCH (pr:Prescription)-[:PRESCRIBED_MEDICINE]->(m:Medicine) RETURN COUNT(*) AS count"),
        ("Episode HAS_HOSPITALIZATION Hospitalization", "MATCH (e:Episode)-[:HAS_HOSPITALIZATION]->(h:Hospitalization) RETURN COUNT(*) AS count"),
        ("Hospitalization HAS_NURSE Nurse", "MATCH (h:Hospitalization)-[:HAS_NURSE]->(n:Nurse) RETURN COUNT(*) AS count"),
        ("Episode HAS_APPOINTMENT Appointment", "MATCH (e:Episode)-[:HAS_APPOINTMENT]->(a:Appointment) RETURN COUNT(*) AS count"),
        ("Staff WORKS_IN_DEPARTMENT Department", "MATCH (s:Staff)-[:WORKS_IN_DEPARTMENT]->(d:Department) RETURN COUNT(*) AS count"),
        ("Patient HAS_EMERGENCY_CONTACT Emergency_Contact", "MATCH (p:Patient)-[:HAS_EMERGENCY_CONTACT]->(ec:Emergency_Contact) RETURN COUNT(*) AS count"),
        ("Patient HAS_EPISODE Episode", "MATCH (p:Patient)-[:HAS_EPISODE]->(e:Episode) RETURN COUNT(*) AS count"),
        ("Staff IS_TECHNICIAN Technician", "MATCH (s:Staff)-[:IS_TECHNICIAN]->(t:Technician) RETURN COUNT(*) AS count"),
    ]
    
    total_count = 0
    for label, query in queries:
        result = neo4j.run(query).data()
        print(f"{label}: {result[0]['count']}")


with oracle_connection.cursor() as cursor:
    initialize_neo4j(neo4j)
    #check_relationship_counts(neo4j)
    
fim = time.time()
tempo = fim - inicio
tempo_arredondado = round(tempo, 2)
print("Fim da Migração, tudo realizado com sucesso!")
print(f"Tempo utilizado para realizar a migração:{tempo_arredondado} segundos") 