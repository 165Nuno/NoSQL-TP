from pymongo import MongoClient, UpdateOne
from bson import ObjectId
import datetime

mongo_client = MongoClient('mongodb://localhost:27017/')
mongo_db = mongo_client['hospital']
hospitalization_collection = mongo_db['hospitalization']
room_collection = mongo_db['rooms']
lab_screening_collection = mongo_db['lab_screening']
prescription_collection = mongo_db['prescriptions']
bill_collection = mongo_db['bills']

def calculate_bill(episode_id, room_id):
    v_room_cost = room_collection.find_one({'_id': ObjectId(room_id)}).get('room_cost', 0)
    v_test_cost = lab_screening_collection.aggregate([
        {'$match': {'episode_idepisode': ObjectId(episode_id)}},
        {'$group': {'_id': None, 'total': {'$sum': '$test_cost'}}}
    ])
    v_other_charges = prescription_collection.aggregate([
        {'$match': {'idepisode': ObjectId(episode_id)}},
        {'$lookup': {
            'from': 'medicine',
            'localField': 'idmedicine',
            'foreignField': '_id',
            'as': 'medicine'
        }},
        {'$unwind': '$medicine'},
        {'$group': {'_id': None, 'total': {'$sum': {'$multiply': ['$medicine.m_cost', '$dosage']}}}}
    ])
    
    v_total_cost = v_room_cost + next(v_test_cost, {}).get('total', 0) + next(v_other_charges, {}).get('total', 0)
    
    bill_collection.insert_one({
        'idepisode': ObjectId(episode_id),
        'room_cost': v_room_cost,
        'test_cost': next(v_test_cost, {}).get('total', 0),
        'other_charges': next(v_other_charges, {}).get('total', 0),
        'total': v_total_cost,
        'payment_status': 'PENDING',
        'registered_at': datetime.datetime.now()
    })

if __name__ == '__main__':
    with hospitalization_collection.watch([{'$match': {'operationType': 'update'}}]) as stream:
        for change in stream:
            updated_fields = change['updateDescription']['updatedFields']
            if 'discharge_date' in updated_fields:
                old_doc = hospitalization_collection.find_one({'_id': change['documentKey']['_id']})
                if old_doc.get('discharge_date') is None and updated_fields['discharge_date'] is not None:
                    calculate_bill(old_doc['idepisode'], old_doc['room_idroom'])
