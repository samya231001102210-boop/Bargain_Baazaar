from bson import ObjectId
from datetime import datetime, date
from decimal import Decimal

def serialize(value):
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, list):
        return [serialize(v) for v in value]
    if isinstance(value, dict):
        return {k: serialize(v) for k, v in value.items() if k != "_id"} | ({"id": str(value["_id"])} if "_id" in value else {})
    return value
