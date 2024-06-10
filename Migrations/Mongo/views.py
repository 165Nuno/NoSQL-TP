from pymongo import MongoClient
import csv 
def create_patient_appointment_view():
    # Connect to MongoDB
    mongo_client = MongoClient('mongodb://localhost:27017/')
    mongo_db = mongo_client['hospital']

    # Define the pipeline to perform the join and shape the output
    pipeline = [
        {
            '$unwind': '$episodes'
        },
        {
            '$unwind': '$episodes.events'
        },
        {
            '$match': {
                'episodes.events.type': 'appointment'
            }
        },
        {
            '$lookup': {
                'from': 'staff',
                'localField': 'episodes.events.doctor',
                'foreignField': '_id',
                'as': 'doctor'
            }
        },
        {
            '$unwind': '$doctor'
        },
        {
            '$lookup': {
                'from': 'department',
                'localField': 'doctor.iddepartment',
                'foreignField': '_id',
                'as': 'department'
            }
        },
        {
            '$unwind': '$department'
        },
        {
            '$project': {
                'appointment_scheduled_date': '$episodes.events.scheduled_on',
                'appointment_date': '$episodes.events.appointment_date',
                'appointment_time': '$episodes.events.appointment_time',
                'doctor_id': '$doctor._id',
                'doctor_qualifications': '$doctor.qualifications',
                'department_name': '$department.name',
                'patient_first_name': '$first_name',
                'patient_last_name': '$last_name',
                'patient_blood_type': '$blood_type',
                'patient_phone': '$phone',
                'patient_email': '$email',
                'patient_gender': '$gender'
            }
        }
    ]

    # Perform aggregation to create the view
    view_data = mongo_db.patients.aggregate(pipeline)

    # Convert the cursor to a list and return
    return list(view_data)

# Example usage:
view_results = create_patient_appointment_view()
filename = "patient_appointments.csv"

field_names = ["Id", "Scheduled Date", "Appointment Date", "Appointment Time", "Doctor Id", "Doctor Qualifications", "Department", "Patient First Name", "Patient Last Name", "Patient Blood Type", "Patient Phone", "Patient Email", "Patient Gender"]

key_mapping = {
    "_id": "Id",
    "appointment_scheduled_date": "Scheduled Date",
    "appointment_date": "Appointment Date",
    "appointment_time": "Appointment Time",
    "doctor_id": "Doctor Id",
    "doctor_qualifications": "Doctor Qualifications",
    "department_name": "Department",
    "patient_first_name": "Patient First Name",
    "patient_last_name": "Patient Last Name",
    "patient_blood_type": "Patient Blood Type",
    "patient_phone": "Patient Phone",
    "patient_email": "Patient Email",
    "patient_gender": "Patient Gender"
}

with open(filename, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=field_names)
    

    writer.writeheader()
    
    for item in view_results:
        # Crie um novo dicionário com as chaves mapeadas para os nomes das colunas desejados
        mapped_item = {key_mapping[key]: value for key, value in item.items() if key in key_mapping}
        writer.writerow(mapped_item)