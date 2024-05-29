import oracledb
from pymongo import MongoClient
import getpass
import traceback

# Solicitar a senha do usuário para Oracle
oracle_password = getpass.getpass("Enter Oracle password: ")

try:
    # Conectar ao banco de dados Oracle
    oracle_connection = oracledb.connect(
        user='nosql',
        password=oracle_password,
        dsn='localhost/xe'
    )

    # Conectar ao MongoDB (sem senha)
    mongo_client = MongoClient('mongodb://localhost:27017/')
    mongo_db = mongo_client['hospital']

    # Função para obter os dados de uma tabela Oracle
    def fetch_oracle_data(query):
        cursor = oracle_connection.cursor()
        cursor.execute(query)
        columns = [col[0].lower() for col in cursor.description]
        rows = cursor.fetchall()
        data = [dict(zip(columns, row)) for row in rows]
        cursor.close()
        return data

    # Migração para a coleção 'medicine'
    medicine_query = """
        SELECT idmedicine AS "_id", 
               m_name AS name, 
               m_quantity AS quantity, 
               m_cost AS cost 
        FROM medicine
    """
    medicine_data = fetch_oracle_data(medicine_query)
    mongo_db.medicine.insert_many(medicine_data)

    # Migração para a coleção 'department'
    department_query = """
        SELECT iddepartment AS "_id", 
               dept_head AS head, 
               dept_name AS name, 
               emp_count 
        FROM department
    """
    department_data = fetch_oracle_data(department_query)

    staff_query = """
        SELECT emp_id AS "_id", 
               is_active_status, 
               iddepartment 
        FROM staff
    """
    staff_data = fetch_oracle_data(staff_query)

    for dept in department_data:
        dept['active'] = [staff['_id'] for staff in staff_data if staff['iddepartment'] == dept['_id'] and staff['is_active_status'] == 'Y']
        dept['inactive'] = [staff['_id'] for staff in staff_data if staff['iddepartment'] == dept['_id'] and staff['is_active_status'] == 'N']

    mongo_db.department.insert_many(department_data)

    # Migração para a coleção 'staff'
    nurse_query = 'SELECT staff_emp_id AS "_id" FROM nurse'
    doctor_query = 'SELECT emp_id AS "_id" FROM doctor'
    technician_query = 'SELECT staff_emp_id AS "_id" FROM technician'
    
    positions = {
        'nurse': fetch_oracle_data(nurse_query),
        'doctor': fetch_oracle_data(doctor_query),
        'technician': fetch_oracle_data(technician_query)
    }

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
        FROM staff
    """
    staff_data = fetch_oracle_data(staff_query)

    for staff in staff_data:
        for position, ids in positions.items():
            if staff['_id'] in [p['_id'] for p in ids]:
                staff['position'] = position
                if position == 'doctor':
                    qualifications_query = f"SELECT qualifications FROM doctor WHERE emp_id = {staff['_id']}"
                    qualifications = fetch_oracle_data(qualifications_query)[0]
                    staff['qualifications'] = qualifications['qualifications']

    mongo_db.staff.insert_many(staff_data)

    # Migração para a coleção 'rooms'
    rooms_query = """
        SELECT idroom AS "_id", 
               room_type AS type, 
               room_cost AS cost 
        FROM room
    """
    rooms_data = fetch_oracle_data(rooms_query)
    mongo_db.rooms.insert_many(rooms_data)

    # Migração para a coleção 'insurance'
    insurance_query = """
        SELECT policy_number AS "_id", 
               provider, 
               insurance_plan AS plan, 
               co_pay, 
               coverage, 
               maternity, 
               dental, 
               optical 
        FROM insurance
    """
    insurance_data = fetch_oracle_data(insurance_query)
    mongo_db.insurance.insert_many(insurance_data)

    # Migração para a coleção 'bills'
    bills_query = """
        SELECT idbill AS "_id", 
               idepisode AS id_episode, 
               room_cost, 
               test_cost, 
               other_charges, 
               total, 
               registered_at, 
               payment_status 
        FROM bill
    """
    bills_data = fetch_oracle_data(bills_query)
    mongo_db.bills.insert_many(bills_data)

    # Migração para a coleção 'prescriptions'
    prescriptions_query = """
        SELECT idprescription AS "_id", 
               prescription_date AS prescription_date, 
               dosage, 
               idmedicine, 
               idepisode AS id_episode 
        FROM prescription
    """
    prescriptions_data = fetch_oracle_data(prescriptions_query)
    mongo_db.prescriptions.insert_many(prescriptions_data)

    # Migração para a coleção 'patients'
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
        FROM patient
    """
    patients_data = fetch_oracle_data(patients_query)

    for patient in patients_data:
        # Emergency Contacts
        emergency_contacts_query = f"""
            SELECT contact_name AS name, 
                   phone, 
                   relation 
            FROM emergency_contact 
            WHERE idpatient = {patient['_id']}
        """
        emergency_contacts = fetch_oracle_data(emergency_contacts_query)
        patient['emergency_contacts'] = emergency_contacts

        # Medical History
        medical_history_query = f"""
            SELECT record_id AS "_id", 
                   condition, 
                   record_date AS record_date 
            FROM MEDICAL_HISTORY 
            WHERE idpatient = {patient['_id']}
        """
        medical_history = fetch_oracle_data(medical_history_query)
        patient['medical_history'] = medical_history

        # Episodes and Events
        episodes_query = f"""
            SELECT idepisode AS "_id" 
            FROM episode 
            WHERE patient_idpatient = {patient['_id']}
        """
        episodes_data = fetch_oracle_data(episodes_query)

        episodes = []
        for episode in episodes_data:
            episode_id = episode['_id']

            # Appointments
            appointment_query = f"""
                SELECT 'appointment' AS type, 
                       scheduled_on, 
                       appointment_date, 
                       appointment_time, 
                       iddoctor AS doctor 
                FROM appointment 
                WHERE idepisode = {episode_id}
            """
            appointments = fetch_oracle_data(appointment_query)

            # Hospitalizations
            hospitalization_query = f"""
                SELECT 'hospitalization' AS type, 
                       admission_date, 
                       discharge_date, 
                       room_idroom AS room, 
                       responsible_nurse AS nurse 
                FROM hospitalization 
                WHERE idepisode = {episode_id}
            """
            hospitalizations = fetch_oracle_data(hospitalization_query)

            # Lab Screenings
            lab_screening_query = f"""
                SELECT 'lab_screening' AS type, 
                       test_cost, 
                       test_date, 
                       idtechnician AS technician 
                FROM lab_screening 
                WHERE episode_idepisode = {episode_id}
            """
            lab_screenings = fetch_oracle_data(lab_screening_query)

            events = appointments + hospitalizations + lab_screenings
            episode['events'] = events

            episodes.append(episode)

        patient['episodes'] = episodes
        
        # Bills
        patient_bills_query = f"""
            SELECT idbill AS "_id" 
            FROM bill 
            WHERE idepisode IN (SELECT idepisode FROM episode WHERE patient_idpatient = {patient['_id']})
        """
        
        patient_prescriptions_query = f"""
            SELECT idprescription AS "_id" 
            FROM prescription 
            WHERE idepisode IN (SELECT idepisode FROM episode WHERE patient_idpatient = {patient['_id']})
        """
        
        patient_bills = fetch_oracle_data(patient_bills_query)
        patient_prescriptions = fetch_oracle_data(patient_prescriptions_query)
        patient['bills'] = [bill['_id'] for bill in patient_bills]
        patient['prescriptions'] = [prescription['_id'] for prescription in patient_prescriptions]

    mongo_db.patients.insert_many(patients_data)

except oracledb.DatabaseError as e:
    error, = e.args
    print(f"Oracle Database error: {error.code} - {error.message}")
    print("".join(traceback.format_exception(None, e, e.__traceback__)))

except Exception as e:
    print(f"An error occurred: {e}")
    print("".join(traceback.format_exception(None, e, e.__traceback__)))

finally:
    # Fechar conexões
    try:
        if oracle_connection:
            oracle_connection.close()
    except NameError:
        pass
    
    try:
        if mongo_client:
            mongo_client.close()
    except NameError:
        pass
