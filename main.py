#!/usr/bin/env python

import webapp2
import logging
import models
import json

from google.appengine.ext import db
from google.appengine.ext.webapp import template

API_PREFIX = '/api/v1/conversations'

class MainHandler(webapp2.RequestHandler):
    
    ''' Default HTML handler - used for testing API '''

    def get(self):
        self.response.out.write(template.render('templates/index.html',{}))


class ConversationsHandler(webapp2.RequestHandler):
    
    ''' API handler for conversations- handles GET and POST, PUT operations '''

    def get(self, id):
        conversation = models.Conversation.get_by_id(int(id))
        self.response.set_status(200, 'OK')
        self.response.headers.add_header("Location", '{0}/{1}'.format(API_PREFIX, conversation.key().id()))
        self.response.out.write(json.dumps(conversation.to_json()))
        return

    def post(self):
        ''' Saves the conversation and returns the id '''
    
        if (self.request.headers.get("Content-Type")=='application/x-www-form-urlencoded'):
            subject = self.request.get('subject')
            participants = self.request.get('participants').split(',')
        else:
            logging.info(self.request.body)
            data = json.loads(self.request.body)
            subject = data['subject']
            participants = data['to']
            participants.append(data['from'])
            
        conversation = models.Conversation(subject = subject,
                                           participants = participants)
        conversation.put()


        self.response.set_status(201, 'Created')
        self.response.headers.add_header("Location", '{0}/{1}'.format(API_PREFIX, conversation.key().id()))
        self.response.out.write(json.dumps(conversation.to_json()))

app = webapp2.WSGIApplication([('/', MainHandler),
                              (API_PREFIX, ConversationsHandler),
                              (API_PREFIX + '/(.*)', ConversationsHandler)],
                              debug=True)
 