'''

Module used to handle inbound mail to the application

Classes: EmailReceivedHandler

'''

import os
import webapp2
import logging
import models

from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler 

from google.appengine.api import mail

DEBUG_IGNORE_ATTACHMENTS = True

class EmailReceivedHandler(InboundMailHandler):
    
    def receive(self, mail_message):
        ''' Receives incoming email, and adds message to conversation thread

        This method does a number of things:
        - Parse conversation id out from the incoming address
        - Fetch the conversation
        - Add the email message to the messages collection
        - Send email to other recipients
        '''

        id = mail_message.to.split('@')[0]
        conversation = models.Conversation.get_by_id(int(id))
        conversation.id = id
        logging.info(mail_message.body.decode())
        msg = models.Message(sender=mail_message.sender,
                             text=mail_message.body.decode(),
                             conversation=conversation)
        msg.put()

        
app = webapp2.WSGIApplication([EmailReceivedHandler.mapping()],
                              debug=True)
 