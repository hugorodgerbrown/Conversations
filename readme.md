# Conversations

## Overview

Conversations is a hosted application that provides an API for threaded email conversations that support "reply-to" functionality. A good example of this is the Basecamp messaging feature. If  you receive an email notification of a new message, you can simply reply to the message, and your reply will be inserted into the conversation, whereupon all of the participants in the conversation will themselves be notified of your update.

The core use case for this service is to act as a messaging proxy for web applications. In this scenario, two or more people can communicate via email, with the entire conversation being proxied through, and recorded by, the application itself. This is very useful when you want to allow people to communicate without giving out their personal email addresses - so for something like eBay, where buyer and seller can communicate over email, but through the eBay messaging system.

The conversations application also contains a very simple implementation of a web UI to allow users to view conversations and post messages. This should be considered a sample application, and not used in production.

## Core concepts

### Conversation

A single threaded communication consisting of a chronological sequence of **messages**. A conversation may have one or more participants. Conversations have a subject / title field.

### Message

Each message consists of text that is posted to the common thread. Messages are posted by a **participant**, and notification of a new message is sent to each participant in the conversation, with the exception of the sender.

### Participant

A participant is someone who is party to the conversation. Participants can post messages to the conversation, and will receive a **notification** whenever anyone other than themselves posts a new message. They are identified by a unique email address.

### Notification

Notifications are sent via email. Each participant in a conversation is notified whenever a new message is added to the conversation.

## API 

### Create new conversation 

    POST /api/v1/conversations HTTP/1.1

A conversation itself consists of just an empty shell for the subsequent messages that it contains. The first message that is appended to the conversation sets the "subject"; the sender and recipient of any message in the conversation are appended to the list of participants.

*Sample Request* 

    POST /api/v1/conversations HTTP/1.1
    Content-type: application/json;
    Accept: application/json;

*Sample Response*

    HTTP/1.1 201 Created
    Location: http://example.com/api/v1/conversations/123456

    {
        'conversation': 
        {
            'id': "123456",
            'created': "2012-06-22T12:43:37+0100",
            'reply-to:': "123456@conversations.com"
        }
    }

The API supports the concept of initialising a conversation with the first message. This will create both the conversation shell, and the first message, which will be appended to the conversation, setting the subject and initial participants. This is the most common use case.

*Sample Request* 

    POST /api/v1/conversations HTTP/1.1
    Content-type: application/json;
    Accept: application/json;

    {
        "sender": "hugo@example.com",
        "to": ["fred@example.com"],
        "subject": "Example message",
        "text": "this is a message"
    }

*Sample Response*

    HTTP/1.1 201 Created
    Location: http://example.com/api/v1/conversations/123456

    {
        'conversation': 
        {
            'id': "123456",
            'created': "2012-06-22T12:43:37+0100",
            'reply-to:': "123456@conversations.com",
            'subject': "Example message"
            'participants': 
            [
                "fred@example.com",
                "hugo@example.com"
            ],
            'messages':[
            {
                'id': "123456.1",
                'created':"2012-06-22T12:43:37+0100",
                'sender': "hugo@example.com",
                'text': "this is a message",
                'notifications':["fred@example.com"]
            }]
        },
    }

*Actions*

When a new conversation is created, the recipient will receive a notification via email.

### View conversation

    GET /api/v1/conversations/{{conversation_id}} HTTP 1.1

Returns the entire conversation, including all messages, and a list of participants.

*Sample Request*

    GET /api/v1/conversations/123456 HTTP/1.1
    Accept: application/json;

*Sample Response*

    HTTP/1.1 200 OK

    {
        'conversation': 
        {
            'id':"123456",
            'created':"2012-06-22T12:43:37+0100",
            'reply-to:': "123456@conversations.com",
            'subject': "Example message"
            'participants': 
            [
                "fred@example.com",
                "hugo@example.com"
            ],
            'messages':[
                {
                    'id': "123456.1",
                    'created':"2012-06-22T12:43:37+0100",
                    'sender': "hugo@example.com",
                    'text': "this is a message"
                    'notifications':["fred@example.com"]
                },
                {
                    'id': "123456.2",
                    'created':"2012-06-22T12:43:37+0100",
                    'sender': "fred@example.com",
                    'text': "this is a reply"
                    'notifications':["hugo@example.com"]
                }
            ]
        },
    }

### Recipient replies to message (via web)

    POST /api/v1/conversations/{{conversation_id}} HTTP/1.1

If the recipient is viewing the conversational thread on the web (e.g. looking at a message in Basecamp and posting a reply), then the application developer will need to submit the reply via HTTP. This is just a POST to the conversation endpoint.

*Sample Request*

    POST /api/v1/conversations/123456 HTTP/1.1
    Content-type: application/json;
    Accept: application/json;


    {
        'sender': "fred@example.com",
        'text': "this is a reply"
    }

*Sample Response*

    HTTP/1.1 201 Created
    Location: http://example.com/api/v1/conversations/123456/2

    {
        'id': "123456.2",
        'created': "2012-06-22T12:43:37+0100",
        'participants': ["fred@example.com","hugo@example.com"],
        'notifications':["hugo@example.com"]
    }

*Actions*

When a message is posted to an existing conversation, a notification is sent via email to all participants, other than the sender.

### Recipient replies to message (via email)

On receipt of the message notification, one or more recipients may decide to reply to the email itself (rather than going to the website to view the conversation). They hit reply, and send their message back to the reply-to address (e.g. 123456@conversations.com). The service will then parse out the ID (123456), add the message (stripping out the original) to the conversation, and notify all other recipients of the update (everyone except the sender). The email handler should call the web handler internally - it is the same functionality, delivered over a different protocol.

*Actions*

The inbound email handler will be responsible for parsing and storing the message, and sending outbound notification emails to participants. The outbound email notifications should contain the message body, and a link back to the entire conversation.

### View message

    GET /api/v1/conversations/{{conversation_id}}/{{message_id}} HTTP 1.1

This returns an individual message, out of context of the parent conversation.

*Sample Request*

    GET /api/v1/conversations/123456/2 HTTP 1.1
    Accept: application/json;

*Sample Response*

    HTTP/1.1 200 OK

    {
        'id': "123456.2",
        'created': "2012-06-22T12:43:37+0100",
        'sender': "fred@example.com",
        'text': "this is a reply"
        'participants': ["fred@example.com","hugo@example.com"],
        'notifications':["hugo@example.com"]
    }

## Additional features

* Add participant
* Authentication