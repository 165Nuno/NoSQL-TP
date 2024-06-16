from py2neo import Graph, Node, Relationship
import time
import getpass
import oracledb
import json

# Solicitar a user e senha do utilizador para Oracle
#oracle_username = getpass.getpass("Enter Oracle username: ")
#oracle_password = getpass.getpass("Enter Oracle password: ")

print("Inicio da migração para Neo4j")
inicio = time.time()
oracle_connection = oracledb.connect(user="sys", password="<12345>",
                                      dsn="localhost:1521/xe", mode=oracledb.SYSDBA)

print("Conexão Oracle realizada com sucesso!")
uri = "bolt://localhost:7687"
user = "neo4j"
password = "12345678"

neo4j = Graph(uri, auth=(user, password))
print("Conexão Neo4j realizada com sucesso!")

# Consultas SQL para obter os dados das tabelas desejadas
nurse_query = 'SELECT staff_emp_id AS "_id" FROM SYSTEM.nurse'
doctor_query = 'SELECT emp_id AS "_id" FROM SYSTEM.doctor'
technician_query = 'SELECT staff_emp_id AS "_id" FROM SYSTEM.technician'

staff_query = """
    SELECT emp_id AS "_id", 
           emp_fname AS first_name, 
           emp_lname AS last_name, 
           date_joining, 
           date_seperation AS date_separation, 
           email, 
           address, 
           ssn, 
           iddepartment 
    FROM SYSTEM.staff
"""

def fetch_oracle_data(query):
    with oracle_connection.cursor() as cursor:
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return data

def clear_neo4j_database(neo4j):
    """Delete all nodes and relationships in the Neo4j database."""
    apagar_query = """
    MATCH (n) DETACH DELETE n
    """
    neo4j.run(apagar_query)
    print("Dados presentes na base de dados Neo4j apagados!")


def create_nodes(neo4j):

    ## [NODOS ROOM]
    rooms_query = """
        SELECT idroom AS "_id", 
            room_type AS type, 
            room_cost AS cost 
        FROM SYSTEM.room
        """
    rooms_data = fetch_oracle_data(rooms_query)
    #print(rooms_data)

    for room in rooms_data:
            room_node = Node("Room",
                             idroom=room['_id'],
                             type=room['TYPE'],
                             cost=room['COST'])
            neo4j.create(room_node)

    # [NODOS MEDICINE]
    medicine_query = """
        SELECT idmedicine AS "_id", 
               m_name AS name, 
               m_quantity AS quantity, 
               m_cost AS cost 
        FROM SYSTEM.medicine
    """
    medicine_data = fetch_oracle_data(medicine_query)

    for medicine in medicine_data:
        medicine_node = Node("Medicine",
                         id_medicine=medicine['_id'],
                         m_name=medicine['NAME'],
                         m_quantity=medicine['QUANTITY'],
                         m_cost=medicine['COST'])
        neo4j.create(medicine_node)

    # [NODOS EPISODES]
    episodes_query = f"""
            SELECT idepisode AS "_id",
                   patient_idpatient AS id_patient
            FROM SYSTEM.episode 
        """
    episodes_data = fetch_oracle_data(episodes_query)
    for episode in episodes_data:
        episode_node = Node("Episode",
                         id_episode=episode['_id'],
                         id_patient=episode['ID_PATIENT'])
        neo4j.create(episode_node)


    # [NODOS MEDICAL_HISTORY]
    medical_history_query = """
            SELECT record_id AS "_id", 
                   condition, 
                   record_date AS record_date,
                   idpatient AS id_patient 
            FROM SYSTEM.medical_history
     """
    
    medical_data = fetch_oracle_data(medical_history_query)
    for medical in medical_data:
        medical_node = Node("Medical_History",
                            record_id=medical['_id'],
                            condition=medical['CONDITION'],
                            record_date=medical['RECORD_DATE'],
                            id_patient=medical['ID_PATIENT'])
        neo4j.create(medical_node)

    # [NODOS INSURANCE]
    insurance_query = """
        SELECT policy_number AS "_id", 
               provider, 
               insurance_plan AS plan, 
               co_pay, 
               coverage, 
               maternity, 
               dental, 
               optical 
        FROM SYSTEM.insurance
    """
    insurance_data = fetch_oracle_data(insurance_query)

    for insurance in insurance_data:
        insurance_node = Node("Insurance",
                         id_insurance=insurance['_id'],
                         provider=insurance['PROVIDER'],
                         plan=insurance['PLAN'],
                         co_pay=insurance['CO_PAY'],
                         coverage=insurance['COVERAGE'],
                         maternity=insurance['MATERNITY'],
                         dental=insurance['DENTAL'],
                         optical=insurance['OPTICAL'])
        neo4j.create(insurance_node)

    # [NODOS BILLS]
    bills_query = """
        SELECT idbill AS "_id", 
               idepisode AS id_episode, 
               room_cost, 
               test_cost, 
               other_charges, 
               total, 
               registered_at, 
               payment_status 
        FROM SYSTEM.bill
    """

    bills_data = fetch_oracle_data(bills_query)
    for bill in bills_data:
        bill_node = Node("Bill",
                         id_bill=bill['_id'],
                         idepisode=bill['ID_EPISODE'],
                         room_cost=bill['ROOM_COST'],
                         test_cost=bill['TEST_COST'],
                         other_charges=bill['OTHER_CHARGES'],
                         total=bill['TOTAL'],
                         registered_at=bill['REGISTERED_AT'],
                         payment_status=bill['PAYMENT_STATUS'])
        neo4j.create(bill_node)

    
    # [NODOS DEPARTMENT]
    department_query = """
        SELECT iddepartment AS "_id", 
               dept_head AS head, 
               dept_name AS name, 
               emp_count 
        FROM SYSTEM.department
    """
    department_data = fetch_oracle_data(department_query)
    for dept in department_data:

        department_node = Node("Department",
                                   iddepartment=dept['_id'],
                                   head=dept['HEAD'],
                                   name=dept['NAME'],
                                   emp_count=dept['EMP_COUNT'])
        neo4j.create(department_node)

    # [NODOS STAFF]
    staff_query = """
    SELECT emp_id AS "_id", 
           emp_fname AS first_name, 
           emp_lname AS last_name, 
           date_joining, 
           date_seperation AS date_separation, 
           email, 
           address, 
           ssn,
           is_active_status, 
           iddepartment 
    FROM SYSTEM.staff
    """
    positions = {
        'nurse': fetch_oracle_data(nurse_query),
        'doctor': fetch_oracle_data(doctor_query),
        'technician': fetch_oracle_data(technician_query)
    }
    #print(positions.items())

    staff_data = fetch_oracle_data(staff_query)
    for staff in staff_data:
        #print(staff)
        for position, ids in positions.items():
            if staff['_id'] in [p['_id'] for p in ids]:
                staff['position'] = position
                if position == 'doctor':
                    qualifications_query = f"SELECT qualifications FROM SYSTEM.doctor WHERE emp_id = {staff['_id']}"
                    qualifications = fetch_oracle_data(qualifications_query)[0]
                    staff['qualifications'] = qualifications['QUALIFICATIONS']
                else:
                    staff['qualifications'] = None

        staff_node = Node("Staff",
                          emp_id=staff['_id'],
                          first_name=staff['FIRST_NAME'],
                          last_name=staff['LAST_NAME'],
                          date_joining=staff['DATE_JOINING'],
                          date_separation=staff['DATE_SEPARATION'],
                          email=staff['EMAIL'],
                          address=staff['ADDRESS'],
                          ssn=staff['SSN'],
                          is_active_status=staff['IS_ACTIVE_STATUS'],
                          iddepartment=staff['IDDEPARTMENT'],
                          position=staff['position'],
                          qualifications=staff['qualifications'])
        neo4j.create(staff_node)

    # Passar a tabela prescriptions para uma relação com propriedades
    prescriptions_query = """
        SELECT idprescription AS "_id", 
               prescription_date AS prescription_date, 
               dosage, 
               idmedicine, 
               idepisode AS id_episode 
        FROM SYSTEM.prescription
    """
    prescriptions_data = fetch_oracle_data(prescriptions_query)
    for prescription in prescriptions_data:
                episode_node = neo4j.nodes.match("Episode", id_episode=prescription['ID_EPISODE']).first()
                medicine_node = neo4j.nodes.match("Medicine", id_medicine=prescription['IDMEDICINE']).first()
                relationship = Relationship(episode_node, "PRESCRIBED", medicine_node, dosage=prescription['DOSAGE'],prescription_date=prescription['PRESCRIPTION_DATE'])
                neo4j.create(relationship)


    # Passar a tabela lab_screening para uma relação com propriedades
    lab_screening_query = f"""
                SELECT lab_id, 
                       test_cost, 
                       test_date, 
                       idtechnician AS technician,
                       episode_idepisode as id_episode
                FROM SYSTEM.lab_screening 
            """
    lab_screenings = fetch_oracle_data(lab_screening_query)
    #print(lab_screenings)
    for lab_screening in lab_screenings:
                episode_node = neo4j.nodes.match("Episode", id_episode=lab_screening['ID_EPISODE']).first()
                staff_node = neo4j.nodes.match("Staff", emp_id=lab_screening['TECHNICIAN']).first()
                relationship = Relationship(episode_node, "PERFORMED", staff_node, test_cost=lab_screening['TEST_COST'],test_date=lab_screening['TEST_DATE'])
                neo4j.create(relationship)


    # Passar os atributos da tabela appointment para os nodos episode
    appointment_query = f"""
                SELECT scheduled_on, 
                       appointment_date, 
                       appointment_time, 
                       iddoctor AS doctor, 
                       idepisode AS id_episode
                FROM SYSTEM.appointment 
            """
    appointments = fetch_oracle_data(appointment_query)
    #print(appointments)
    for appointment in appointments:
                episode_node = neo4j.nodes.match("Episode", id_episode=appointment['ID_EPISODE']).first()
                if episode_node:
                # Adiciona novos atributos ao nó do episódio
                    episode_node['scheduled_on'] = appointment['SCHEDULED_ON']
                    episode_node['appointmente_date'] = appointment['APPOINTMENT_DATE']
                    episode_node['appointment_time'] = appointment['APPOINTMENT_TIME']
        
                # Atualiza o nó no Neo4j
                    neo4j.push(episode_node)
                staff_node = neo4j.nodes.match("Staff", emp_id=appointment['DOCTOR']).first()
                relationship = Relationship(episode_node, "ATTEND_BY", staff_node)
                neo4j.create(relationship)
    
    hospitalization_query = """
                SELECT admission_date, 
                       discharge_date, 
                       room_idroom AS room, 
                       responsible_nurse AS nurse,
                       idepisode AS id_episode
                FROM SYSTEM.hospitalization 
    """
    hospitalizations = fetch_oracle_data(hospitalization_query)
    for hospitalization in hospitalizations:
                episode_node = neo4j.nodes.match("Episode", id_episode=hospitalization['ID_EPISODE']).first()
                if episode_node:
                    # Adiciona novos atributos ao nó do episódio
                    episode_node['admission_date'] = hospitalization['ADMISSION_DATE']
                    episode_node['discharge_date'] = hospitalization['DISCHARGE_DATE']
                    episode_node['room'] = hospitalization['ROOM']
        
                    # Atualiza o nó no Neo4j
                    neo4j.push(episode_node)
                staff_node = neo4j.nodes.match("Staff", emp_id=hospitalization['NURSE']).first()
                relationship = Relationship(episode_node, "RESPONSIBLE_NURSE", staff_node)
                neo4j.create(relationship)
                room_node = neo4j.nodes.match("Room", idroom=hospitalization['ROOM']).first()
                relationship2 = Relationship(episode_node, "HOSPITALIZED_IN", room_node)
                neo4j.create(relationship2)


    # [NODOS PATIENT]
    patients_query = """
        SELECT idpatient AS "_id", 
               patient_fname AS first_name, 
               patient_lname AS last_name, 
               blood_type, 
               phone, 
               email, 
               gender, 
               policy_number, 
               birthday 
        FROM SYSTEM.patient
    """
    # -> Criar uma lista de contactos de emergência
    emergency_contacts_query = """
            SELECT contact_name AS name, 
                   phone, 
                   relation,
                   idpatient
            FROM SYSTEM.emergency_contact 
    """

    patients_data = fetch_oracle_data(patients_query)
    emergency_data = fetch_oracle_data(emergency_contacts_query)

    for patient in patients_data:
        patient_contacts = [contact for contact in emergency_data if contact['IDPATIENT'] == patient['_id']]
        emergency_contacts_json = json.dumps(patient_contacts)
        #print(emergency_contacts_json)
        patient_node = Node("Patient",
                            idpatient=patient['_id'],
                            patient_fname=patient['FIRST_NAME'],
                            patient_lname=patient['LAST_NAME'],
                            blood_type=patient['BLOOD_TYPE'],
                            phone=patient['PHONE'],
                            email=patient['EMAIL'],
                            gender=patient['GENDER'],
                            policy_number=patient['POLICY_NUMBER'],
                            birthday=patient['BIRTHDAY'],
                            emergency_contacts = emergency_contacts_json)
        neo4j.create(patient_node)

    # [PATIENT] -> [EPISODE]
    patient_nodes = neo4j.nodes.match("Patient")
    for patient_node in patient_nodes:
        episode_nodes = neo4j.nodes.match("Episode", id_patient=patient_node["idpatient"])

        for episode_node in episode_nodes:
            relationship = Relationship(patient_node, "HAS_EPISODE", episode_node)
            neo4j.create(relationship)
    
    # [EPISODE] -> [BILL]
    bill_nodes = neo4j.nodes.match("Bill")
    for bill_node in bill_nodes:
        episode_node = neo4j.nodes.match("Episode", id_episode=bill_node["idepisode"]).first()
        
        if episode_node:
            relationship = Relationship(episode_node, "HAS_BILL", bill_node)
            neo4j.create(relationship)

    # [PATIENT] -> [INSURANCE]
    patient_nodes = neo4j.nodes.match("Patient")
    for patient_node in patient_nodes:
        insurance_node = neo4j.nodes.match("Insurance", id_insurance=patient_node["policy_number"]).first()
        
        if insurance_node:
            relationship = Relationship(patient_node, "HAS_INSURANCE", insurance_node)
            neo4j.create(relationship)
             

def initialize_neo4j(neo4j):
    clear_neo4j_database(neo4j)
    create_nodes(neo4j)
    #create_relationships(neo4j)

def check_relationship_counts(neo4j):
    """Check and print the number of pairs for each relationship in the Neo4j database."""
    # Implementar conforme necessário

with oracle_connection.cursor() as cursor:
    initialize_neo4j(neo4j)

fim = time.time()
tempo = fim - inicio
tempo_arredondado = round(tempo, 2)
print("Fim da Migração, tudo realizado com sucesso!")
print(f"Tempo utilizado para realizar a migração: {tempo_arredondado} segundos")
