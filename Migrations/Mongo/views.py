from pymongo import MongoClient

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
for item in view_results:
    print(item)
