from pymongo import MongoClient
from datetime import datetime
import time
from prettytable import PrettyTable

# Conectar ao MongoDB
client = MongoClient("mongodb://localhost:27017/")

# Selecionar o banco de dados
db = client["hospital"]

# Lista por ordem decrescente dos medicamentos mais caros
def run_query1_mongo():
    medicine_collection = db['medicine']

    # Query para ordenar os medicamentos por custo em ordem decrescente
    medicamentos = medicine_collection.find().sort('cost', -1)
    results = []
    for medicamento in medicamentos:
        results.append({
            'id': medicamento['_id'],
            'name': medicamento['name'],
            'cost': medicamento['cost']
        })
    return results

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
    results = []
    for paciente in pacientes:
        results.append({
            'id_patient': paciente['_id'],
            'patient_fname': paciente['first_name'],
            'patient_lname': paciente['last_name'],
            'episode_count': paciente['num_episodes']
        })
    return results

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
   patients = db.patients.find(query, projection)
   results = []
   for patient in patients:
     for emergency_contact in patient['emergency_contacts']:
         results.append({
             'id_patient': patient['_id'], 
             'patient_fname': patient['first_name'], 
             'patient_lname': patient['last_name'],
             'contact_name': emergency_contact['name'], 
             'phone': emergency_contact['phone']
         })
   return results

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
    results = []

    for resultado in resultados:
        room_id = resultado['_id']
        room_type = db.rooms.find_one({'_id': room_id})['type']
        total_cost = resultado['total_cost']
        results.append({
            'room_id': room_id,
            'room_type': room_type,
            'total_cost': total_cost
        })

    return results

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

    results = []
    for resultado in resultados:
        results.append({
            'room_type': resultado['_id'], 
            'unique_patient_count': resultado['num_pacientes']})

    return results
    
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

    results = []
    for resultado in resultados:
        results.append({
            'room_type': resultado['_id'],
            'average_cost': round(resultado['custo_medio'], 2)
        })
        

    return results

    
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

    results = []
    for resultado in resultados:
        results.append({
            'department_name': resultado['name'], 
            'staff_count': resultado['total_count']
        })
        

    return results
    
    
    
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

    results = []
    if resultado:
        funcionario = resultado[0]
        results.append({
            'emp_id': funcionario["_id"], 
            'first_name': funcionario["first_name"], 
            'last_name': funcionario["last_name"], 
            'years_at_hospital': round(funcionario["tempo_ativo_anos"], 2)
        })
        
    return results
    
    
    
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

    results = []
    if resultado:
        paciente = resultado[0]
        medical_conditions = ", ".join(paciente["medical_history_conditions"])
        results.append({
            'id_patient': paciente["_id"], 
            'first_name': paciente["first_name"], 
            'last_name': paciente["last_name"], 
            'condition_count': paciente["medical_history_count"], 
            'conditions': medical_conditions
        })
    
    return results
    

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

    results = []
    for room in result:
        room_id = room["_id"]
        room_type = room["type"]
        hospitalizacoes = room["hospitalizations"]
        results.append({
            'room_id': room_id,
            'room_type':room_type,
            'hospitalization_count': hospitalizacoes
        })

    return results
    

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

    results = []
    for patient in result:
        results.append({
            'idpatient': patient["_id"],
            'patient_fname': patient["first_name"],
            'patient_lname': patient["last_name"],
            'appointment_count': patient["num_appointments"]
        })

    return results


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

    results = []
    for patient in result:
        results.append({
            'idpatient': patient["_id"],
            'patient_fname': patient["first_name"],
            'patient_lname': patient["last_name"],
            'sum_total_bill': patient["total_bill_cost"]
        })

    return results
    
    
    
    

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
    results = []
    # Exibir a média total da duração da estadia de hospitalização
    if result:
        media_total = result[0]["media_total_duracao_estadia"]
        results.append({
            'avg_hospitalization_stay': media_total
        })
    return results
    
    
def tempo(func):
    inicio = time.time()
    func()
    fim = time.time()
    return fim - inicio
    

# Executar todas as consultas
if __name__ == "__main__":
   tempos = {}
   
   for i in range(1, 14):  # De 1 a 13
    func_name = f'run_query{i}_mongo'
    func = globals().get(func_name)
    if func is not None:
         tempos[f'{i}'] = tempo(func)
    else:
        print(f"Função {func_name} não encontrada.")
  
   table = PrettyTable()
   table.field_names = ["Query", "Tempo de Execução (segundos)"]
   
   for nome, tempo in tempos.items():
       table.add_row([nome, f"{tempo:.4f}"])
   
   print(table)
   