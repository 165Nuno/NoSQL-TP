from pymongo import MongoClient
from prettytable import PrettyTable
from datetime import datetime

# Conectar ao MongoDB
client = MongoClient("mongodb://localhost:27017/")

# Selecionar o banco de dados
db = client["hospital"]

# Lista por ordem decrescente dos medicamentos mais caros
def run_query1_mongo():
    medicine_collection = db['medicine']

    # Query para ordenar os medicamentos por custo em ordem decrescente
    medicamentos = medicine_collection.find().sort('cost', -1)

    # Crie uma tabela para exibir os resultados
    tabela = PrettyTable()
    tabela.field_names = ["ID", "Nome", "Quantidade", "Custo"]

    # Adicione os dados dos medicamentos na tabela
    for medicamento in medicamentos:
        tabela.add_row([medicamento['_id'], medicamento['name'], medicamento['quantity'], medicamento['cost']])

    # Imprima a tabela
    print(tabela)

# Listar pacientes que têm mais de 3 episodes por ordem descrescente
def run_query2_mongo():
    patients_collection = db['patients']

    # Agregação para contar o número de episódios por paciente e filtrar os que têm mais de 3
    pipeline = [
        {
            '$project': {
                'first_name': 1,
                'last_name': 1,
                'num_episodes': {'$size': '$episodes'}
            }
        },
        {
            '$match': {
                'num_episodes': {'$gt': 3}
            }
        },
        {
            '$sort': {
                'num_episodes': -1
            }
        }
    ]
    
    pacientes = patients_collection.aggregate(pipeline)

    # Crie uma tabela para exibir os resultados
    tabela = PrettyTable()
    tabela.field_names = ["ID", "Primeiro Nome", "Último Nome", "Número de Episódios"]

    # Adicione os dados dos pacientes na tabela
    for paciente in pacientes:
        tabela.add_row([paciente['_id'], paciente['first_name'], paciente['last_name'], paciente['num_episodes']])

    # Imprima a tabela
    print(tabela)

# Listar pacientes e as seus contactos de emergência
def run_query3_mongo():
   
   query = {}
   # Projetar apenas os campos relevantes
   projection = {
       '_id': 1,
       'first_name': 1,
       'last_name': 1,
       'emergency_contacts': 1
   }
   # Executar a consulta
   results = db.patients.find(query, projection)
   # Criar uma tabela bonita para exibir os resultados
   table = PrettyTable()
   table.field_names = ["ID", "First Name", "Last Name", "Emergency Contact Name", "Emergency Contact Phone"]   
   for patient in results:
       for emergency_contact in patient['emergency_contacts']:
           table.add_row([patient['_id'], patient['first_name'], patient['last_name'], emergency_contact['name'], emergency_contact['phone']])   
   print(table)

# Listar as salas com o maior custo de hospitalização total
def run_query4_mongo():
    pipeline = [
        {
            '$unwind': '$episodes'
        },
        {
            '$unwind': '$episodes.events'
        },
        {
            '$match': {
                'episodes.events.type': 'hospitalization'
            }
        },
        {
            '$lookup': {
                'from': 'bills',
                'localField': 'episodes._id',
                'foreignField': 'id_episode',
                'as': 'hospital_bills'
            }
        },
        {
            '$unwind': {
                'path': '$hospital_bills',
                'preserveNullAndEmptyArrays': True
            }
        },
        {
            '$group': {
                '_id': '$episodes.events.room',
                'total_cost': {'$sum': '$hospital_bills.total'}
            }
        },
        {
            '$sort': {
                'total_cost': -1
            }
        }
    ]

    # Executar a agregação
    resultados = db.patients.aggregate(pipeline)

    # Criar uma tabela bonita
    table = PrettyTable()
    table.field_names = ["ID da Sala", "Tipo da Sala", "Total de Custo"]

    # Adicionar os resultados à tabela
    for resultado in resultados:
        room_id = resultado['_id']
        room_type = db.rooms.find_one({'_id': room_id})['type']
        total_cost = resultado['total_cost']
        table.add_row([room_id, room_type, total_cost])

    # Exibir a tabela
    print(table)

def run_query5_mongo():
    pipeline = [
        { '$unwind': '$episodes' },
        { '$unwind': '$episodes.events' },
        { 
            '$match': {
                'episodes.events.type': 'hospitalization'
            } 
        },
        {
            '$lookup': {
                'from': 'rooms',
                'localField': 'episodes.events.room',
                'foreignField': '_id',
                'as': 'room'
            }
        },
        { '$unwind': '$room' },
        {
            '$group': {
                '_id': '$room.type',
                'pacientes': { '$addToSet': '$_id' }
            }
        },
        {
            '$project': {
                '_id': 1,
                'num_pacientes': { '$size': '$pacientes' }
            }
        },
        {
            '$sort': {
                'num_pacientes': -1
            }
        }
    ]

    resultados = db.patients.aggregate(pipeline)

    # Criar uma tabela bonita
    table = PrettyTable()
    table.field_names = ["Tipo de Sala", "Número de Pacientes Únicos"]

    # Adicionar os resultados à tabela
    for resultado in resultados:
        table.add_row([resultado['_id'], resultado['num_pacientes']])

    # Exibir a tabela
    print(table)
    
# Listar os tipos de sala e o custo médio por tipo
def run_query6_mongo():
    pipeline = [
        {
            '$group': {
                '_id': '$type',
                'custo_medio': { '$avg': '$cost' }
            }
        },
        {
            '$sort': {
                'custo_medio': -1
            }
        }
    ]

    resultados = db.rooms.aggregate(pipeline)

    # Criar uma tabela bonita
    table = PrettyTable()
    table.field_names = ["Tipo de Sala", "Custo Médio"]

    # Adicionar os resultados à tabela
    for resultado in resultados:
        table.add_row([resultado['_id'], round(resultado['custo_medio'], 2)])

    # Exibir a tabela
    print(table)

    
# Contar o número de funcionários por departamento, ordenado pelo número de funcionários
def run_query7_mongo():
    pipeline = [
        {
            '$project': {
                '_id': 1,
                'name': 1,
                'total_count': {
                    '$sum': [
                        { '$size': '$active' },
                        { '$size': '$inactive' }
                    ]
                }
            }
        },
        {
            '$sort': { 'total_count': -1 }
        }
    ]

    resultados = db.department.aggregate(pipeline)

    # Criar uma tabela bonita
    table = PrettyTable()
    table.field_names = ["Departamento", "Total de Funcionários"]

    # Adicionar os resultados à tabela
    for resultado in resultados:
        table.add_row([resultado['name'], resultado['total_count']])

    # Exibir a tabela
    print(table)
    
    
    
#O funcionário com mais tempo de serviço ativo
def run_query8_mongo():
    
    pipeline = [
        {
            "$match": {
                "date_separation": None
            }
        },
        {
            "$project": {
                "_id": 1,
                "first_name": 1,
                "last_name": 1,
                "date_joining": 1
            }
        },
        {
            "$addFields": {
                "tempo_ativo_dias": {
                    "$divide": [
                        {
                            "$subtract": [
                                datetime.now(),
                                "$date_joining"
                            ]
                        },
                        1000 * 60 * 60 * 24
                    ]
                }
            }
        },
        {
            "$addFields": {
                "tempo_ativo_anos": {
                    "$divide": ["$tempo_ativo_dias", 365]
                }
            }
        },
        {
            "$sort": {
                "tempo_ativo_anos": -1
            }
        },
        {
            "$limit": 1
        }
    ]

    # Executar a pipeline de agregação
    resultado = list(db.staff.aggregate(pipeline))

    # Criar uma tabela para exibir os resultados
    table = PrettyTable()
    table.field_names = ["ID", "First Name", "Last Name", "Years of Service"]

    # Adicionar os resultados à tabela
    if resultado:
        funcionario = resultado[0]
        table.add_row([funcionario["_id"], funcionario["first_name"], funcionario["last_name"], round(funcionario["tempo_ativo_anos"], 2)])

    # Exibir a tabela
    print("Funcionário com mais tempo de serviço ativo:")
    print(table)
    
    
    
# O paciente com mais condições médicas e suas condições
def run_query9_mongo():
    pipeline = [
        {
            "$project": {
                "_id": 1,
                "first_name": 1,
                "last_name": 1,
                "medical_history_count": {
                    "$size": "$medical_history"
                },
                "medical_history_conditions": "$medical_history.condition"
            }
        },
        {
            "$sort": {
                "medical_history_count": -1
            }
        },
        {
            "$limit": 1
        }
    ]

    # Executar a pipeline de agregação
    resultado = list(db.patients.aggregate(pipeline))

    # Criar uma tabela para exibir os resultados
    table = PrettyTable()
    table.field_names = ["ID", "First Name", "Last Name", "Medical History Count", "Medical Conditions"]

    # Adicionar os resultados à tabela
    if resultado:
        paciente = resultado[0]
        medical_conditions = ", ".join(paciente["medical_history_conditions"])
        table.add_row([paciente["_id"], paciente["first_name"], paciente["last_name"], paciente["medical_history_count"], medical_conditions])

    # Exibir a tabela
    print("Paciente com mais condições médicas e suas condições:")
    print(table)
    

#  Listar todas as hospitalizações em uma sala específica
def run_query10_mongo():
    rooms_collection = db['rooms']
    
    pipeline = [
        {
            "$lookup": {
                "from": "patients",
                "let": { "room_id": "$_id" },
                "pipeline": [
                    { "$unwind": "$episodes" },
                    { "$unwind": "$episodes.events" },
                    {
                        "$match": {
                            "$expr": {
                                "$and": [
                                    { "$eq": ["$episodes.events.room", "$$room_id"] },
                                    { "$eq": ["$episodes.events.type", "hospitalization"] }
                                ]
                            }
                        }
                    },
                    { "$count": "count" }
                ],
                "as": "hospitalizations"
            }
        },
        {
            "$project": {
                "_id": 1,
                "type": 1,
                "hospitalizations": { "$ifNull": [{ "$arrayElemAt": ["$hospitalizations.count", 0] }, 0] }
            }
        },
        {
            "$sort": {
                "hospitalizations": -1
            }
        }
    ]

    # Executar a query
    result = list(rooms_collection.aggregate(pipeline))

    # Criar uma tabela para exibir os resultados
    table = PrettyTable()
    table.field_names = ["Room", "Room Type", "Hospitalizações"]

    # Adicionar os resultados à tabela
    for room in result:
        room_id = room["_id"]
        room_type = room["type"]
        hospitalizacoes = room["hospitalizations"]
        table.add_row([room_id, room_type, hospitalizacoes])

    # Exibir a tabela
    print("Hospitalizações por Sala:")
    print(table)
    

# Pacientes com maior quantidade de appointments
def run_query11_mongo():
    patients_collection = db['patients']

    # Query em MongoDB
    pipeline = [
        {
            "$project": {
                "_id": 1,
                "first_name": 1,
                "last_name": 1,
                "num_appointments": {
                    "$sum": {
                        "$map": {
                            "input": "$episodes",
                            "as": "episode",
                            "in": {
                                "$size": {
                                    "$filter": {
                                        "input": "$$episode.events",
                                        "as": "event",
                                        "cond": { "$eq": ["$$event.type", "appointment"] }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        { "$sort": { "num_appointments": -1 } },
        {"$limit": 10}
    ]

    # Executar a query
    result = list(patients_collection.aggregate(pipeline))

    # Criar uma tabela para exibir os resultados
    table = PrettyTable()
    table.field_names = ["ID", "First Name", "Last Name", "Número de Appointments"]

    # Adicionar os resultados à tabela
    for patient in result:
        patient_id = patient["_id"]
        first_name = patient["first_name"]
        last_name = patient["last_name"]
        num_appointments = patient["num_appointments"]
        table.add_row([patient_id, first_name, last_name, num_appointments])

    # Exibir a tabela
    print("Pacientes com Maior Quantidade de Appointments:")
    print(table)


# Custo total de bill por paciente
def run_query12_mongo():
    patients_collection = db['patients']

    # Pipeline de agregação para calcular o custo total de bill por paciente
    pipeline = [
        {
            "$unwind": "$bills"
        },
        {
            "$lookup": {
                "from": "bills",
                "localField": "bills",
                "foreignField": "_id",
                "as": "bill_details"
            }
        },
        {
            "$unwind": "$bill_details"
        },
        {
            "$group": {
                "_id": "$_id",
                "first_name": { "$first": "$first_name" },
                "last_name": { "$first": "$last_name" },
                "total_bill_cost": { "$sum": "$bill_details.total" }
            }
        },
        {
            "$sort": {
                "total_bill_cost": -1
            }
        }
    ]


    # Executar a agregação
    result = list(patients_collection.aggregate(pipeline))

    # Criar uma tabela para exibir os resultados
    table = PrettyTable()
    table.field_names = ["ID", "First Name", "Last Name", "Custo Total de Bills"]

    # Adicionar os resultados à tabela
    for patient in result:
        patient_id = patient["_id"]
        first_name = patient["first_name"]
        last_name = patient["last_name"]
        total_bill_cost = patient["total_bill_cost"]
        table.add_row([patient_id, first_name, last_name, total_bill_cost])

    # Exibir a tabela
    print("Custo Total de Bill por Paciente:")
    print(table)
    
    
    
    

# Média da duração da estadia de hospitalização
def run_query13_mongo():
    patients_collection = db['patients']

    # Pipeline de agregação para calcular a média total da duração da estadia de hospitalização
    pipeline = [
        {
            "$unwind": "$episodes"
        },
        {
            "$unwind": "$episodes.events"
        },
        {
            "$match": {
                "episodes.events.type": "hospitalization",
                "episodes.events.admission_date": { "$exists": True },
                "episodes.events.discharge_date": { "$exists": True }
            }
        },
        {
            "$project": {
                "duracao_estadia": {
                    "$divide": [
                        {
                            "$subtract": [
                                { "$toDate": "$episodes.events.discharge_date" },
                                { "$toDate": "$episodes.events.admission_date" }
                            ]
                        },
                        86400000  # Converter milissegundos para dias
                    ]
                }
            }
        },
        {
            "$group": {
                "_id": None,
                "media_total_duracao_estadia": { "$avg": "$duracao_estadia" }
            }
        },
        {
            "$project": {
                "_id": 0,
                "media_total_duracao_estadia": { "$round": ["$media_total_duracao_estadia", 2] }
            }
        }
    ]

    # Executar a agregação
    result = list(patients_collection.aggregate(pipeline))

    # Exibir a média total da duração da estadia de hospitalização
    if result:
        media_total = result[0]["media_total_duracao_estadia"]
        print("Média Total da Duração da Estadia de Hospitalização (em dias):", media_total)
    else:
        print("Não há dados disponíveis para calcular a média total.")
    
    
    
    
    
    
# Executar todas as consultas
if __name__ == "__main__":
    print("1. Lista por ordem decrescente dos medicamentos mais caros")
    run_query1_mongo()
    print("\n2. Listar pacientes que têm mais de 3 episódios por ordem decrescente")
    run_query2_mongo()
    print("\n3. Listar pacientes e seus contatos de emergência")
    run_query3_mongo()
    print("\n4. Listar as salas com o maior custo de hospitalização total")
    run_query4_mongo()
    print("\n5. Contar o número de pacientes únicos por tipo de sala")
    run_query5_mongo()
    print("\n6. Listar os tipos de sala e o custo médio por tipo")
    run_query6_mongo()
    print("\n7. Contar o número de funcionários por departamento")
    run_query7_mongo()
    print("\n8. O funcionário com mais tempo de serviço ativo")
    run_query8_mongo()
    print("\n9. O paciente com mais condições médicas e suas condições")
    run_query9_mongo()
    print("\n10. Listar todas as hospitalizações em uma sala específica")
    run_query10_mongo()
    print("\n11. Obter pacientes com mais consultas")
    run_query11_mongo()
    print("\n12. Obter custo total da conta por paciente, ordenado")
    run_query12_mongo()
    print("\n13. Obter média de estadia hospitalar")
    run_query13_mongo()
