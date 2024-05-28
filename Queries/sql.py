import oracledb

#oracle_connection = oracledb.connect(user="sys", password="<12345>",
oracle_connection = oracledb.connect(user="sys", password="password",
                              dsn="localhost:1521/xe", mode=oracledb.SYSDBA)
print("Conexão Oracle realizada com sucesso!")

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