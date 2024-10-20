import mongoengine as me
from datetime import datetime

class Products(me.Document):
    title = me.StringField(required=True)
    description = me.StringField(required=True)
    price = me.FloatField(required=True)
    user_id = me.StringField(required=True)
    created_at = me.DateTimeField(default=datetime.utcnow)
    updated_at = me.DateTimeField(default=datetime.utcnow)

    meta = {'collection': 'products'}
