#!/usr/bin/env python

''' Module that contains classes and code for the api (json) interface '''

import logging
import models
import json
from webapp2 import WSGIApplication, Route, RequestHandler
from google.appengine.api import mail


API_PREFIX = '/api/v1/conversations'


class ApiConversationHandler(RequestHandler):

    ''' API handler for conversations - handles GET and POST operations '''

    def get_conversation(self, cid):
        conversation = models.Conversation.get_by_id(int(cid))
        if conversation:
            self.response.set_status(200, 'OK')
            self.response.out.write(json.dumps(conversation.to_json()))
        else:
            self.error(404)
        return

    def get_message(self, cid, mid):
        message = models.Message.get_by_id(int(mid))
        if message:
            self.response.set_status(200, 'OK')
            self.response.out.write(json.dumps(message.to_json()))
        else:
            self.error(404)
        return

    def post_conversation(self):
        ''' Saves the conversation and returns the id '''

        conversation, message = self._parse_request_body(self.request.body)
        conversation.put()
        message.conversation = conversation
        message.put()
        message.send_notifications()

        self.response.set_status(201, 'Created')
        self.response.headers.add_header("Location", '{0}/{1}'.format(API_PREFIX, conversation.key().id()))
        self.response.out.write(json.dumps(conversation.to_json()))
        return

    def post_message(self, cid):
        ''' Posts a message to an existing conversation.

        param: cid: Numeric Id for the conversation to which to add the message
        '''

        logging.debug('Posting new message to conversation {0}'.format(cid))
        conversation = models.Conversation.get_by_id(int(cid))
        if not conversation:
            self.error(404)

        data = json.loads(self.request.body)
        message = models.Message(sender=data['sender'],
                                 text=data['text'],
                                 conversation=conversation)
        message.put()
        message.send_notifications()

        self.response.set_status(201, 'Created')
        self.response.headers.add_header("Location", '{0}/{1}/{2}'.format(API_PREFIX,
                                         conversation.key().id(),
                                         message.key().id()))
        self.response.out.write(json.dumps(conversation.to_json()))
        return


    def _parse_request_body(self, text):
        ''' Parses the contents of a POST body as JSON.
        Returns :class: `Conversation <Conversastion>` object 

        :param text: the contents of the request, as a string.
        '''

        data = json.loads(text)
        participants = data['to']
        participants.append(str(data['sender']))
        conversation = models.Conversation(subject = data['subject'],
                                           participants = participants)
        message = models.Message(sender=data['sender'],
                                 text=data['text'])
        return conversation, message


app = WSGIApplication([Route('/api/v1/conversations', methods=['POST'], handler='handlers.api.ApiConversationHandler:post_conversation'),
                      Route('/api/v1/conversations/', methods=['POST'], handler='handlers.api.ApiConversationHandler:post_conversation'),
                      Route('/api/v1/conversations/<cid:\d{1,6}>', methods=['POST'], handler='handlers.api.ApiConversationHandler:post_message'),
                      Route('/api/v1/conversations/<cid:\d{1,6}>/<mid:\d{1,6}>', methods=['GET'], handler='handlers.api.ApiConversationHandler:get_message'),
                      Route('/api/v1/conversations/<cid:\d{1,6}>', methods=['GET'], handler='handlers.api.ApiConversationHandler:get_conversation')],
                      debug=True)
