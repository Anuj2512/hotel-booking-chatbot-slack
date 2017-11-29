# -*- coding: utf-8 -*-
"""
In this file, we'll create a python Bot Class.
"""
import os
import json
from slackclient import SlackClient

import os.path
import sys

try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai

CLIENT_ACCESS_TOKEN = 'f98dc606670d4d4f868d0424f62e03e6'


# Messages

WELCOME_MESSAGE = " Welcome to Hotel California! How can I help you ?"

# 


class Bot(object):
    """ Instanciates a Bot object to handle Slack interactions."""
    def __init__(self):
        super(Bot, self).__init__()
        self.oauth = {"client_id": os.environ.get("CLIENT_ID"),
                      "client_secret": os.environ.get("CLIENT_SECRET"),
                      "scope": "bot"}
        self.verification = os.environ.get("VERIFICATION_TOKEN")
        self.client = SlackClient("xoxb-275349460131-zeL0WUalzSkyXwMgvuBpJy5I")
        #self.client = SlackClient("")

    def auth(self, code):
        """
        A method to exchange the temporary auth code for an OAuth token
        which is then saved it in memory on our Bot object for easier access.
        """
        auth_response = self.client.api_call("oauth.access",
                                             client_id=self.oauth['client_id'],
                                             client_secret=self.oauth[
                                                            'client_secret'],
                                             code=code)
        self.user_id = auth_response["bot"]["bot_user_id"]
        print("AUTH RESPONSE")
        print(auth_response["bot"]["bot_access_token"])
        self.client = SlackClient(auth_response["bot"]["bot_access_token"])

    def getAPIAIResponseObject(self, message_text, userid):

        print(message_text)

        ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)

        request = ai.text_request()
        request.lang = 'en'
        request.session_id = userid
        request.query = message_text
        response = request.getresponse()

        response_json = response.read()
        #print (response_text)

        responseObj = json.loads(response_json)
        return responseObj


    def handleMessage(self, message):
        
        print(message)
        text = message.get('text')
        channel = message["channel"]
        responseObj = self.getAPIAIResponseObject(text, message["user"])

        print(responseObj)
        self.interprete_response(responseObj, channel)


    def interprete_response(self, responseObj, channel):
        response_message = responseObj["result"]["fulfillment"]["messages"][0]["speech"]
        action = responseObj["result"]["action"]
        message_attachments = None

        if action == "smalltalk.greetings.hello":
            response_message += WELCOME_MESSAGE
            self.send_response(response_message, message_attachments, channel)

        elif action.startswith('smalltalk.'):
            self.send_response(response_message, message_attachments, channel)

        else:
            intent = responseObj["result"]["metadata"]["intentName"]
            room_type = responseObj["result"]["parameters"]["RoomType"]
            date_period = responseObj["result"]["parameters"]["date-period"]
            bActionComplete = responseObj["result"]["actionIncomplete"] == False

            if bActionComplete:
                response_message = "Sure. we have some " + room_type + " rooms available for " + date_period
                message_attachments = [
                        {
                            "text": "Are you sure you want to book this room ?",
                            "callback_id": "booking",
                            "color": "good",
                            "attachment_type": "default",
                            "actions": [
                                {
                                    "name": "confirm_booking",
                                    "text": ":hotel: Confirm Booking",
                                    "type": "button",
                                    "value": "confirm_booking"
                                }
                            ]
                        }
                    ]

            self.send_response(response_message, message_attachments, channel)

    def send_response(self, response_message, message_attachments, channel):
        
        print("message_attachments")
        print(message_attachments)

        if message_attachments == None:
            print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            self.client.api_call("chat.postMessage",
                            channel=channel,
                            text=response_message)
        
        else:
            print("###########################################")
            self.client.api_call("chat.postMessage",
                            channel=channel,
                            text=response_message,
                            attachments=json.dumps(message_attachments))
            

    def say_hello(self, message):
        """
        A method to ask workshop attendees to build this bot. When a user
        clicks the button for their operating system, the bot should display
        the set-up instructions for that operating system.
        """
        print("say hello")
        print(message)
        channel = message["channel"]
        hello_message = "I want to live! Please build me."
        # Add message attachments here!
        message_attachments = [
            {
                "pretext": "I'll tell you how to set up your system. :robot_face:",
                "text": "What operating system are you using?",
                "callback_id": "os",
                "color": "#3AA3E3",
                "attachment_type": "default",
                "actions": [
                    {
                        "name": "mac",
                        "text": ":apple: Mac",
                        "type": "button",
                        "value": "mac"
                    },
                    {
                        "name": "windows",
                        "text": ":fax: Windows",
                        "type": "button",
                        "value": "win"
                    }
                ]
            }
        ]
        self.client.api_call("chat.postMessage",
                             channel=channel,
                             text=hello_message,
                             attachments=json.dumps(message_attachments))

    def show_win(self):
        """
        Here we'll build a method to respond to a user's action taken from a
        message button. It should return a message with system setup
        instructions for building this bot on a Windows operating system.
        """
        message = {
            "as_user": False,
            "replace_original": False,
            "response_type": "ephemeral",
            "text": ":fax: *Windows OS*:\n Here's some helpful tips for "
            "setting up the requirements you'll need for this workshop:",
            "attachments": [{
                "mrkdwn_in": ["text", "pretext"],
                "text": "*Python 2.7 and Pip*:\n_Check to see if you have "
                "Python on your system:_\n```python --version```\n_Download "
                "link:_\nhttps://www.python.org/ftp/python/2.7.12/python-2.7.1"
                "2.msi\n_Make sure to tick  `Add Python.exe to PATH` when "
                "installing Python for Windows._\n_If that doesn't add it to "
                "the path after installation, run this command:_\n```c:\pyth"
                "on27\\tools\scripts\win_add2path.py```\n_After downloading "
                "Python, you must upgrade your version of Pip:_\n```python "
                "-m pip install -U pip```\n*Virtualenv*:\n_Check to see if "
                "you have virtualenv on your system and install it if you "
                "don't have it:_\n```virtualenv --version\npip install "
                "virtualenv```\n*Ngrok:*\n_Check to see if you have ngrok on "
                "your system:_\n```ngrok --version```\n_Download "
                "Link:_\nhttps://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable"
                "-darwin-amd64.zip\nTo unzip on Windows, just double click "
                "ngrok.zip",
                "footer": "Slack API: Build this Bot Workshop",
                "footer_icon": "https://platform.slack-edge.com/img/default"
                "_application_icon.png"
            }]}
        return json.dumps(message)
        pass

    def show_mac(self):
        """
        A method to respond to a user's action taken from a message button.
        Returns a message with system setup instructions for building this bot
        on a Mac operating system.
        """
        message = {
            "as_user": False,
            "replace_original": False,
            "response_type": "ephemeral",
            "text": ":apple: *Mac OS*:\n Here's some helpful tips for "
            "setting up the requirements you'll need for this workshop:",
            "attachments": [{
                "mrkdwn_in": ["text", "pretext"],
                "text": "*Python 2.7 and Pip*:\n_Check to see if you have "
                "Python on your system:_\n```which python && python "
                "--version```\n_If you have homebrew, you can use it to "
                "install python and pip:_\n```brew install python && pip```"
                "\n_If not, you can download python here:_Download link:_\n"
                "https://www.python.org/ftp/python/2.7.12/python-2.7.12-"
                "macosx10.6.pkg\n_After downloading Python, you must upgrade "
                "your version of Pip:_\n```pip install -U pip```\n"
                "*Virtualenv*:\n_Check to see if you have virtualenv on your "
                "system and install it if you don't have it:_\n```which "
                "virtualenv\npip install virtualenv```\n*Ngrok:*\n_Check "
                "to see if you have ngrok on your system:_\n```which ngrok"
                "```\n_Download Link:_\nhttps://bin.equinox.io/c/4VmDzA7iaHb"
                "/ngrok-stable-darwin-amd64.zip\n```unzip /path/to/ngrok.zip"
                "\ncd /usr/local/bin\nln -s /path/to/ngrok ngrok```",
                "footer": "Slack API: Build this Bot Workshop",
                "footer_icon": "https://platform.slack-edge.com/img/default"
                "_application_icon.png"
                }]
            }

        return json.dumps(message)

    def show_booking_confirmation(self, room_type, date_period):
        message = {
            "as_user": False,
            "replace_original": False,
            "response_type": "ephemeral",
            "text": "*Booking Confirmation:*:\n Here's details about your booking at Hotel California.",
            "attachments": [{
                "mrkdwn_in": ["text", "pretext"],
                "text": "Room Type: " + room_type + "\n"
                "Date: " + date_period + "\n",
                "actions": [
                    {
                        "name": "email_confirmation",
                        "text": ":ticket: Send Email Confirmation",
                        "type": "button",
                        "value": "email_confirmation"
                    }
                ]
                
            }]}
        return json.dumps(message)