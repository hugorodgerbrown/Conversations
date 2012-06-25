#!/usr/bin/env python

''' Module that contains classes and code for the web (html) interface '''

from webapp2 import WSGIApplication, Route, RequestHandler
import logging
import models
import json
from email import utils

from google.appengine.api import mail
from google.appengine.ext.webapp import template

API_PREFIX = '/api/v1/conversations'

class MainHandler(RequestHandler):
    
    ''' Default HTML handler - used for testing API '''

    def get(self):
        self.response.out.write(template.render('templates/index.html',{}))

class WebConversationHandler(RequestHandler):
    
    ''' web handler for a single conversation '''

    def get_all(self):
        ''' Fetches all stored conversations and prints them in a list '''
        conversations = models.Conversation.all()
        self.response.out.write(template.render('templates/conversations.html',{'conversations':conversations}))
        return


    def get_conversation(self, cid):
        ''' renders a single conversation as a web page '''
        try:
           val = int(cid)
        except ValueError:
           self.error(400)
           self.response.out.write('Invalid input ({0}) - conversation id must be an integer.'.format(cid))
           return
        conversation = models.Conversation.get_by_id(val)
        logging.info(conversation)
        if conversation is None:
            self.error(404)
            self.response.out.write("No such conversation: {0}".format(val))
            return 
        logging.info(conversation)
        self.response.set_status(200, 'OK')
        self.response.out.write(template.render(
                                'templates/conversation.html',
                                {'conversation':conversation}))
        return

    def _validate_missing_field(self, field_value, field_name):
        ''' Helper function to throw a 400 if a required field is missing '''
        if (field_value==''):
            self.error(400)
            err_msg = 'Missing or invalid \'{0}\' field: {1}'.format(field_name, field_value)
            self.response.out.write(err_msg)
            logging.error(err_msg)
            return False
        else:
            return True

    def post_conversation(self):

        ''' Used to add messages to a conversation '''
        subject = self.request.get('subject')
        if not self._validate_missing_field(subject, 'subject'):
            return

        sender = utils.parseaddr(self.request.get('sender'))[1]
        if not self._validate_missing_field(sender, 'sender'):
            return

        recipient = utils.parseaddr(self.request.get('recipient'))[1]
        if not self._validate_missing_field(recipient, 'recipient'):
            return

        participants = [recipient, sender]
        conversation = models.Conversation(subject = subject,
                                           participants = participants)
        conversation.put()

        msg = models.Message(sender=sender,
                             text=self.request.get('text'),
                             conversation=conversation)
        notifications = msg.set_notifications()
        msg.put()

        # send mail only to the recipient
        mail.send_mail(sender = '{0} <{1}>'.format('YunoJuno notifications','{0}@conversations-app.appspotmail.com'.format(conversation.key().id())),
                      to = recipient    ,
                      reply_to = '{0}@conversations-app.appspotmail.com'.format(conversation.key().id()),
                      subject = conversation.subject,
                      body = msg.text)

        self.response.set_status(201, 'Created')
        self.response.out.write(json.dumps(conversation.to_json()))
        return


    def post_message(self, cid):
        ''' adds a new message to the thread, and sends notifications '''
        logging.info('Posting new message to conversation {0}'.format(cid))
        conversation = models.Conversation.get_by_id(int(cid))
        logging.info(self.request.get('sender'))
        msg = models.Message(sender=self.request.get('sender'),
                     text=self.request.get('text'),
                     conversation=conversation)
        notifications = msg.set_notifications()
        msg.put()

        return

app = WSGIApplication([('/', MainHandler),
    Route('/conversations', methods=['GET'], handler='handlers.web.WebConversationHandler:get_all'),
    Route('/conversations/', methods=['GET'], handler='handlers.web.WebConversationHandler:get_all'),
    Route('/conversations', methods=['POST'], handler='handlers.web.WebConversationHandler:post_conversation'),
    Route('/conversations/', methods=['POST'], handler='handlers.web.WebConversationHandler:post_conversation'),
    Route('/conversations/<cid>', methods=['GET'], handler='handlers.web.WebConversationHandler:get_conversation'),
    Route('/conversations/<cid>', methods=['POST'], handler='handlers.web.WebConversationHandler:post_message')],
    debug=True)
 