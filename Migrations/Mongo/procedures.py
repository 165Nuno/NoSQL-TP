from pymongo import MongoClient, ReturnDocument
from bson import ObjectId

# Connect to MongoDB
mongo_client = MongoClient('mongodb://localhost:27017/')
mongo_db = mongo_client['hospital']
bills_collection = mongo_db['bills']

def sp_update_bill_status(p_bill_id, p_paid_value):
    try:
        bill = bills_collection.find_one({'_id': ObjectId(p_bill_id)})
        if not bill:
            raise ValueError("Bill not found")
        
        v_total = bill['total']
        
        if p_paid_value < v_total:
            # Update status to FAILURE
            bills_collection.find_one_and_update(
                {'_id': ObjectId(p_bill_id)},
                {'$set': {'payment_status': 'FAILURE'}},
                return_document=ReturnDocument.AFTER
            )
            raise ValueError("Paid value is inferior to the total value of the bill.")
        else:
            # Update status to PROCESSED
            updated_bill = bills_collection.find_one_and_update(
                {'_id': ObjectId(p_bill_id)},
                {'$set': {'payment_status': 'PROCESSED'}},
                return_document=ReturnDocument.AFTER
            )
            return updated_bill
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    bill_id = input("Enter the bill ID: ")
    paid_value = float(input("Enter the paid value: "))
    updated_bill = sp_update_bill_status(bill_id, paid_value)
    print(updated_bill)