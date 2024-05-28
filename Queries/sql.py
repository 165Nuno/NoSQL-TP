import oracledb

#oracle_connection = oracledb.connect(user="sys", password="<12345>",
oracle_connection = oracledb.connect(user="sys", password="password",
                              dsn="localhost:1521/xe", mode=oracledb.SYSDBA)
print("Conexão Oracle realizada com sucesso!")

# Lista por ordem descrescente os medicamentos mais caros
def run_query1_sql():
    sql_query = """
    SELECT 
        idmedicine AS id, 
        m_name AS name, 
        m_cost AS cost
    FROM 
        SYSTEM.medicine
    ORDER BY 
        m_cost DESC,
        idmedicine ASC
    """
    cursor = oracle_connection.cursor()
    cursor.execute(sql_query)
    results = []
    for row in cursor:
        results.append({
            'id': row[0],
            'name': row[1],
            'cost': row[2]
        })
    return results

# Listar pacientes que têm mais de 3 episodes por ordem descrescente
def run_query2_sql():
    sql_query = """
SELECT 
    p.idpatient AS id_patient, 
    p.patient_fname AS patient_fname, 
    p.patient_lname AS patient_lname, 
    COUNT(e.idepisode) AS episode_count
FROM 
    SYSTEM.patient p
JOIN 
    SYSTEM.episode e ON p.idpatient = e.patient_idpatient
GROUP BY 
    p.idpatient, p.patient_fname, p.patient_lname
HAVING 
    COUNT(e.idepisode) > 3
ORDER BY 
    episode_count DESC, 
    p.idpatient ASC
    """
    cursor = oracle_connection.cursor()
    cursor.execute(sql_query)
    results = []
    for row in cursor:
        results.append({
            'id_patient': row[0],
            'patient_fname': row[1],
            'patient_lname': row[2],
            'episode_count': row[3]
        })
    return results

# Listar pacientes e as seus contactos de emergência
def run_query3_sql():
    sql_query = """
SELECT 
    p.idpatient AS id_patient, 
    p.patient_fname AS patient_fname, 
    p.patient_lname AS patient_lname, 
    ec.contact_name AS contact_name, 
    ec.phone AS phone
FROM 
    SYSTEM.patient p
JOIN 
    SYSTEM.emergency_contact ec ON p.idpatient = ec.idpatient
ORDER BY 
    id_patient ASC
    """
    cursor = oracle_connection.cursor()
    cursor.execute(sql_query)
    results = []
    for row in cursor:
        results.append({
            'id_patient': row[0],
            'patient_fname': row[1],
            'patient_lname': row[2],
            'contact_name': row[3],
            'phone': row[4]
        })
    return results

# Listar as salas com o maior custo de hospitalização total
def run_query4_sql():
    sql_query = """
SELECT 
    r.idroom AS room_id, 
    r.room_type AS room_type, 
    SUM(b.total) AS total_cost
FROM 
    SYSTEM.room r
LEFT JOIN 
    SYSTEM.hospitalization h ON r.idroom = h.room_idroom
LEFT JOIN 
    SYSTEM.episode e ON h.idepisode = e.idepisode
LEFT JOIN 
    SYSTEM.bill b ON e.idepisode = b.idepisode
GROUP BY 
    r.idroom, r.room_type
HAVING 
    SUM(b.total) IS NOT NULL  -- É para remover os quatros que não tiveram custos
ORDER BY 
    total_cost DESC
    """
    cursor = oracle_connection.cursor()
    cursor.execute(sql_query)
    results = []
    for row in cursor:
        results.append({
            'room_id': row[0],
            'room_type': row[1],
            'total_cost': row[2],
        })
    return results

def run_query11_sql():
    sql_query = """
    SELECT p.idpatient, p.patient_fname, p.patient_lname, ec.contact_name, ec.phone, ec.relation
    FROM SYSTEM.patient p
    JOIN SYSTEM.emergency_contact ec ON p.idpatient = ec.idpatient
    ORDER BY p.idpatient ASC
    """
    cursor = oracle_connection.cursor()
    cursor.execute(sql_query)
    results = []
    for row in cursor:
        results.append({
            'idpatient': row[0],
            'patient_fname': row[1],
            'patient_lname': row[2],
            'contact_name': row[3],
            'phone': row[4],
            'relation': row[5]
        })
    return results

# Query to Get Patients with the Most Appointments
def run_query12_sql():
    sql_query = """
    SELECT 
        p.idpatient, 
        p.patient_fname, 
        p.patient_lname, 
        COUNT(a.iddoctor) AS appointment_count
    FROM 
        SYSTEM.patient p
    JOIN
        SYSTEM.episode e ON p.idpatient = e.patient_idpatient
    JOIN 
        SYSTEM.appointment a ON e.idepisode = a.idepisode
    GROUP BY 
        p.idpatient, p.patient_fname, p.patient_lname
    ORDER BY 
        appointment_count DESC
    """
    cursor = oracle_connection.cursor()
    cursor.execute(sql_query)
    results = []
    for row in cursor:
        results.append({
            'idpatient': row[0],
            'patient_fname': row[1],
            'patient_lname': row[2],
            'appointment_count': row[3]
        })
    return results

# Query to Get Total Bill Cost per Patient, ordered
def run_query13_sql():
    sql_query = """
    SELECT
        p.idpatient,
        p.patient_fname,
        p.patient_lname,
        SUM(b.total) as sum_total_bill
    FROM
        SYSTEM.patient p
    JOIN
        SYSTEM.episode e ON p.idpatient = e.patient_idpatient
    JOIN
        SYSTEM.bill b ON e.idepisode = b.idepisode
    GROUP BY
        p.idpatient, p.patient_fname, p.patient_lname
    ORDER BY
        sum_total_bill DESC
    """
    cursor = oracle_connection.cursor()
    cursor.execute(sql_query)
    results = []
    for row in cursor:
        results.append({
            "idpatient": row[0],
            "patient_fname": row[1],
            "patient_lname": row[2],
            "sum_total_bill": row[3]
        })
    return results

# Query to get average hospitalization stay
def run_query14_sql():
    sql_query = """
    SELECT
        ROUND(AVG(h.discharge_date - h.admission_date), 2) AS average_length_of_stay
    FROM
        SYSTEM.hospitalization h    
    """
    cursor = oracle_connection.cursor()
    cursor.execute(sql_query)
    results = []
    for row in cursor:
        results.append({
            "avg_hospitalization_stay": row[0]
        })
    return results

if __name__ == "__main__":
    run_query11_sql()