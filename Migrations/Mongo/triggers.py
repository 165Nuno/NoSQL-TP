import pymongo
from pymongo import MongoClient
from datetime import datetime

# Connect to MongoDB
mongo_client = MongoClient('mongodb://localhost:27017/')
mongo_db = mongo_client['hospital']

# Function to calculate the bill and insert it into the bills collection
def generate_bill(change):
    if 'updateDescription' in change and 'updatedFields' in change['updateDescription']:
        updated_fields = change['updateDescription']['updatedFields']
        if 'episodes' in updated_fields:
            # Get the updated patient document
            patient = mongo_db.patients.find_one({'_id': change['documentKey']['_id']})
            if patient:
                for episode in patient.get('episodes', []):
                    for event in episode.get('events', []):
                        if 'discharge_date' in event:
                            episode_id = episode['_id']
                            room_id = event.get('room')

                            # Calculate room cost
                            room = mongo_db.rooms.find_one({'_id': room_id})
                            room_cost = room['cost'] if room else 0

                            # Calculate test cost
                            test_cost = mongo_db.lab_screening.aggregate([
                                {'$match': {'episode_idepisode': episode_id}},
                                {'$group': {'_id': None, 'total_test_cost': {'$sum': '$test_cost'}}}
                            ])
                            test_cost = list(test_cost)[0]['total_test_cost'] if test_cost else 0

                            # Calculate other charges
                            other_charges = mongo_db.prescriptions.aggregate([
                                {'$match': {'id_episode': episode_id}},
                                {'$lookup': {
                                    'from': 'medicine',
                                    'localField': 'idmedicine',
                                    'foreignField': '_id',
                                    'as': 'medicine'
                                }},
                                {'$unwind': '$medicine'},
                                {'$group': {'_id': None, 'total_other_charges': {'$sum': {'$multiply': ['$dosage', '$medicine.cost']}}}}
                            ])
                            other_charges = list(other_charges)[0]['total_other_charges'] if other_charges else 0

                            # Calculate total cost
                            total_cost = room_cost + test_cost + other_charges

                            # Insert bill
                            bill = {
                                'id_episode': episode_id,
                                'room_cost': room_cost,
                                'test_cost': test_cost,
                                'other_charges': other_charges,
                                'total': total_cost,
                                'payment_status': 'PENDING',
                                'registered_at': datetime.now()
                            }
                            mongo_db.bills.insert_one(bill)
                            print(f"Bill generated for episode {episode_id}")

# Set up change stream listener
with mongo_db.patients.watch([{'$match': {'operationType': 'update'}}]) as stream:
    for change in stream:
        generate_bill(change)
