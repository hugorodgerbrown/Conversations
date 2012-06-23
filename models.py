from google.appengine.ext import db
import json
import logging

class Conversation(db.Model):
    created_at = db.DateTimeProperty(auto_now_add=True)
    subject = db.StringProperty(required=True)
    participants = db.StringListProperty()

    def to_json(self):
        ''' converts model to a JSON representation - as returned by the API '''
        d = db.to_dict(self)
        d['created_at'] = str(d['created_at']) # dates aren't serializable, so need to convert to str
        d['id'] = self.key().id()
        return json.dumps({'conversation':d})

class Message(db.Model):
    index = db.IntegerProperty()
    created_at = db.DateTimeProperty(auto_now_add=True)
    conversation = db.ReferenceProperty(Conversation, collection_name="messages")
    sender = db.StringProperty(required=True)
    notifications = db.StringListProperty()
