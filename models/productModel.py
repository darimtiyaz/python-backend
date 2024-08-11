import mongoengine as me

class Product(me.Document):
    user_id = me.StringField(required=True)
    name = me.StringField(required=True)
    description = me.StringField()
    qty = me.IntField(required=True)

    meta = {'collection': 'products'}
