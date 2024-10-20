import mongoengine as me
from datetime import datetime

class Auth(me.Document):
    email = me.StringField(required=True)
    password = me.StringField(required=True)
    photo_url = me.StringField(required=False)
    created_at = me.DateTimeField(default=datetime.utcnow)
    updated_at = me.DateTimeField(default=datetime.utcnow)

    meta = {'collection': 'auth'}
