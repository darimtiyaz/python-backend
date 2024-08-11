import mongoengine as me

class Auth(me.Document):
    username = me.StringField()
    email = me.StringField(required=True)
    password = me.StringField(required=True)

    meta = {'collection': 'auth'}
