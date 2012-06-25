'''

Module used to handle inbound mail to the application

Classes: EmailReceivedHandler

'''

import os
import webapp2
import logging
import models
from api import ApiConversationHandler

from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler 

from google.appengine.api import mail

class EmailReceivedHandler(InboundMailHandler):
    
    def receive(self, mail_message):
        ''' Receives incoming email, and adds message to conversation thread

        This method does a number of things:
        - Parse conversation id out from the incoming address
        - Fetch the conversation
        - Add the email message to the messages collection
        - Send email to other recipients
        '''

        cid = mail_message.to.split('@')[0]
        logging.info('Received message for conversation {0}'.format(cid))
        conversation = models.Conversation.get_by_id(int(cid))

        if not conversation:
            logging.error('Not matching conversation, id={0}'.format(cid))
            return

        # Email addr comes in in "bob jones <bob@example.com>" format
        # convert it into just the email - don't need the name for now
        sender = email.utils.parseaddr(mail_message.sender)[1]
        message = models.Message(sender=sender,
                                 text=mail_message.body.decode(),
                                 conversation=conversation)
        message.put()
        logging.info('Message stored, sending notifications')
        message.send_notifications()
        return

app = webapp2.WSGIApplication([EmailReceivedHandler.mapping()],
                              debug=True)
 