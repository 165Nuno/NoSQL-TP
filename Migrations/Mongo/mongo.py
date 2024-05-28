import oracledb
import getpass

# Solicitar a senha do usuário
password = getpass.getpass("Enter password: ")

try:
    # Estabelecer conexão com o banco de dados Oracle
    connection = oracledb.connect(
        user='nosql', 
        password=password, 
        dsn='localhost/xe'
    )

    # Criação de um cursor
    cursor = connection.cursor()

    # Consulta para recuperar os nomes das tabelas acessíveis pelo usuário
    sql_query = "SELECT table_name FROM user_tables"
    cursor.execute(sql_query)

    # Imprimir os nomes das tabelas
    for table_name in cursor:
        print(table_name[0])

except oracledb.DatabaseError as e:
    # Tratar erros do banco de dados
    error, = e.args
    print(f"Database error: {error.code} - {error.message}")

finally:
    # Fechar o cursor e a conexão
    if cursor:
        cursor.close()
    if connection:
        connection.close()
