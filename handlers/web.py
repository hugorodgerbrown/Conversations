#!/usr/bin/env python

''' Module that contains classes and code for the web (html) interface '''

from webapp2 import WSGIApplication, Route, RequestHandler
import logging
import models
import json

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

    def post_conversation(self):

        ''' Used to add messages to a conversation '''

        subject = self.request.get('subject')
        participants = [self.request.get('recipient')]
        participants.append(self.request.get('sender'))
        conversation = models.Conversation(subject = subject,
                                           participants = participants)
        conversation.put()

        msg = models.Message(sender=self.request.get('sender'),
                             text=self.request.get('text'),
                             conversation=conversation)
        notifications = msg.set_notifications()
        msg.put()

        # send mail only to the recipient
        mail.send_mail(sender='{0} <{1}>'.format('YunoJuno notifications','{0}@conversations-app.appspotmail.com'.format(conversation.key().id())),
                      to=self.request.get('recipient'),
                      reply_to='{0}@conversations-app.appspotmail.com'.format(conversation.key().id()),
                      subject=conversation.subject,
                      body=msg.text)

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
    Route('/conversations', methods=['POST'], handler='handlers.web.WebConversationHandler:post_conversation'),
    Route('/conversations/', methods=['GET'], handler='handlers.web.WebConversationHandler:get_all'),
    Route('/conversations/', methods=['POST'], handler='handlers.web.WebConversationHandler:post_conversation'),
    Route('/conversations/<cid>', methods=['GET'], handler='handlers.web.WebConversationHandler:get_conversation'),
    Route('/conversations/<cid>', methods=['POST'], handler='handlers.web.WebConversationHandler:post_message')],
    debug=True)
 