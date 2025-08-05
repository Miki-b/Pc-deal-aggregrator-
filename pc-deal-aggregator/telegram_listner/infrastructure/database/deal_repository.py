from infrastructure.database.mongo_client import db
from app.entities.deal import Deal
from datetime import datetime

class DealRepository:
    collection = db["deals"]

    @staticmethod
    def insert(deal_dict: dict):
        deal_dict["timestamp"] = datetime.utcnow()
        result = DealRepository.collection.insert_one(deal_dict)
        return result.inserted_id
