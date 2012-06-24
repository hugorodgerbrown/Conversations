#!/usr/bin/env python

''' Module that contains classes and code for the api (json) interface '''

import webapp2
import logging
import models
import json

from google.appengine.api import mail
from google.appengine.ext import db

API_PREFIX = '/api/v1/conversations'

class ApiConversationHandler(webapp2.RequestHandler):
    
    ''' API handler for conversations - handles GET and POST operations '''

    def get(self, id):
        conversation = models.Conversation.get_by_id(int(id))
        self.response.set_status(200, 'OK')
        self.response.out.write(json.dumps(conversation.to_json()))
        return

    def post(self):
        ''' Saves the conversation and returns the id '''
    
        data = json.loads(self.request.body)
        subject = data['subject']
        participants = [ str(data['to']) ]
        participants.append(data['from'])
        conversation = models.Conversation(subject = subject,
                                           participants = participants)
        conversation.put()

        # send mail only to the recipient
        mail.send_mail(sender='{0} <{1}>'.format('YunoJuno notifications','{0}@conversations-app.appspotmail.com'.format(conversation.key().id())),
                      to=data['to'],
                      reply_to='{0}@conversations-app.appspotmail.com'.format(conversation.key().id()),
                      subject=data['subject'],
                      body="This is a message")

        self.response.set_status(201, 'Created')
        self.response.headers.add_header("Location", '{0}/{1}'.format(API_PREFIX, conversation.key().id()))
        self.response.out.write(json.dumps(conversation.to_json()))
        return


app = webapp2.WSGIApplication([(API_PREFIX, ApiConversationHandler),
                              (API_PREFIX + '/(.*)', ApiConversationHandler)],
                              debug=True)
 