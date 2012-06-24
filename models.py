from google.appengine.api import mail
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

        d = self.to_dict()
        return json.dumps({'conversation':d})

    def to_dict(self):
        ''' Converts the current object to dictionary, including all messages.
        Returns: a serializable dictionary

        This method is required in order to manage the marshalling of data in 
        and out of JSON, and some of the implicit GAE data types are not 
        serializable. 
        '''

        d = db.to_dict(self)
        d['id'] = self.key().id()
        d['created_at'] = str(d['created_at'])
        d['messages'] = self.get_messages_as_list()
        
        return d

    def get_messages_as_list(self):
        ''' Converts the related messages to a serializable list.
        Returns: a serializable list of messages.
        '''

        messages = list()
        for message in self.messages:
            messages.append(message.to_dict())
        return messages


class Message(db.Model):

    ''' Represents a message added to a conversational thread '''

    created_at = db.DateTimeProperty(auto_now_add=True)
    conversation = db.ReferenceProperty(Conversation, collection_name="messages")
    sender = db.StringProperty(required=True)
    text = db.TextProperty()
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

    def to_dict(self):
        ''' Creates serializable dictionary object from the message
        Returns: Serializable dictionary object
        '''

        d = db.to_dict(self)
        d['id'] = str(self.key().id())
        d['created_at'] = str(d['created_at']) # dates aren't serializable
        del d['conversation'] # remove as it f's up serialization
        return d

    def to_json(self):
        ''' Serializes the message as JSON '''

        d = self.to_dict()
        return json.dumps({'message':d})

    def send_notifications(self):
        ''' Sends emails to all those being notified of the message 
        HACK: this really shouldn't be here, but in the interests of getting
        the thing done, it is.'''

        self.set_notifications()

        mail_reply_to = '{0}@conversations-app.appspotmail.com'.format(self.conversation.key().id())
        mail_sender = 'YunoJuno notifications <{0}>'.format(mail_reply_to)

        for recipient in self.notifications:
            logging.info('Sending notification of message [{0}] to {1}'.format(
                         self.key().id(),
                         recipient))
            mail.send_mail(sender = mail_sender,
                           to = recipient,
                           reply_to = mail_reply_to,
                           subject = self.conversation.subject,
                           body = self.text)
