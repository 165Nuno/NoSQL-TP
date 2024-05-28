import oracledb

#oracle_connection = oracledb.connect(user="sys", password="<12345>",
oracle_connection = oracledb.connect(user="sys", password="password",
                              dsn="localhost:1521/xe", mode=oracledb.SYSDBA)
print("Conexão Oracle realizada com sucesso!")

def run_query1_sql():
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
def run_query2_sql():
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

if __name__ == "__main__":
    run_query1_sql()