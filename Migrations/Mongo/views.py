from pymongo import MongoClient

mongo_client = MongoClient('mongodb://localhost:27017/')
mongo_db = mongo_client['hospital']
appointment_collection = mongo_db['appointment']

def patient_appointment_view():

    # Define the pipeline to perform the join and shape the output
    pipeline = [
        {
            '$lookup': {
                'from': 'doctor',
                'localField': 'iddoctor',
                'foreignField': 'emp_id',
                'as': 'doctor'
            }
        },
        {
            '$unwind': '$doctor'
        },
        {
            '$lookup': {
                'from': 'staff',
                'localField': 'doctor.emp_id',
                'foreignField': 'emp_id',
                'as': 'staff'
            }
        },
        {
            '$unwind': '$staff'
        },
        {
            '$lookup': {
                'from': 'department',
                'localField': 'staff.iddepartment',
                'foreignField': 'iddepartment',
                'as': 'department'
            }
        },
        {
            '$unwind': '$department'
        },
        {
            '$lookup': {
                'from': 'episode',
                'localField': 'idepisode',
                'foreignField': 'idepisode',
                'as': 'episode'
            }
        },
        {
            '$unwind': '$episode'
        },
        {
            '$lookup': {
                'from': 'patient',
                'localField': 'episode.patient_idpatient',
                'foreignField': 'idpatient',
                'as': 'patient'
            }
        },
        {
            '$unwind': '$patient'
        },
        {
            '$project': {
                'appointment_scheduled_date': '$scheduled_on',
                'appointment_date': '$appointment_date',
                'appointment_time': '$appointment_time',
                'doctor_id': '$doctor.emp_id',
                'doctor_qualifications': '$doctor.qualifications',
                'department_name': '$department.dept_name',
                'patient_first_name': '$patient.patient_fname',
                'patient_last_name': '$patient.patient_lname',
                'patient_blood_type': '$patient.blood_type',
                'patient_phone': '$patient.phone',
                'patient_email': '$patient.email',
                'patient_gender': '$patient.gender'
            }
        }
    ]

    view_data = appointment_collection.aggregate(pipeline)

    return view_data

if __name__ == '__main__':
    view_results = patient_appointment_view()
    for item in view_results:
        print(item)
