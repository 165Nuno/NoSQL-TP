import oracledb
from py2neo import Graph, Node, Relationship

# Criada a ligação com a base de dados Oracle
oracle_connection = oracledb.connect(user="sys", password="<12345>",
                              dsn="localhost:1521/xe", mode=oracledb.SYSDBA)

print("CONEXAO ORACLE FEITA\n")
# Informações de conexão para o Neo4j
uri = "bolt://localhost:7687"
user = "neo4j"
password = "12345678"

# Criada a conexão com a base de dados Neo4j
neo4j = Graph(uri, auth=(user, password))
print("CONEXAO NEO FEITA\n")

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

with oracle_connection.cursor() as cursor:

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


    staff_nodes = neo4j.nodes.match("Staff")

    for staff_node in staff_nodes:

        technician_node = neo4j.nodes.match("Technician", emp_id=staff_node["emp_id"]).first()

        if technician_node:
            relationship = Relationship(staff_node, "WORKS_AS_TECHNICIAN", technician_node)
            neo4j.create(relationship)

print("boas")

