from google.appengine.ext import db
import json
import logging

class Conversation(db.Model):
    
    ''' Represents the shell container for a list of messages '''
    
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

    ''' Represents a message added to a conversational thread '''

    created_at = db.DateTimeProperty(auto_now_add=True)
    conversation = db.ReferenceProperty(Conversation, collection_name="messages")
    sender = db.StringProperty(required=True)
    text = db.StringProperty()
    notifications = db.StringListProperty()

    def set_notifications(self):
        ''' Works out who should be notified '''

        sender_is_known = False

        for p in self.conversation.participants:
            if (p==self.sender):
                logging.info('Ignoring sender {0}'.format(p))
                sender_is_known = True
            else:
                logging.info('Adding {0} to list of notifications'.format(p))
                self.notifications.append(p)

        if not sender_is_known:
            logging.info('Adding sender to list of participants: {0}'.format(self.sender))
            self.conversation.participants.append(self.sender)
            self.conversation.put()

        logging.info('Participants: {0}'.format(self.conversation.participants))
        logging.info('Notifications: {0}'.format(self.notifications))

        return self.notifications