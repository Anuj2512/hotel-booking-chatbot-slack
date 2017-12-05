# -*- coding: utf-8 -*-
"""
In this file, we'll create a python Bot Class.
"""
import shortuuid
import os
import json
from slackclient import SlackClient
from python_mysql_connect import iter_row, getRoomType, getRoomInfo, getAvailableRoomInfo, getRoomAvailabilityByType, getRoomAvailabilityByDate, bookRoom

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
            email = responseObj["result"]["parameters"]["email"]
            dates = date_period.split("/")

            if bActionComplete:
                
                arr_available_rooms = getRoomAvailabilityByType(room_type)
                if len(arr_available_rooms) == 0:
                    response_message = "Sorry. We don't have " + room_type + " rooms available from " + dates[0] + " to " + dates[1]
                else:
                    response_message = "Thank you " + email + " . we have some " + room_type + " rooms available from " + dates[0] + " to " + dates[1]
                    message_attachments = [
                            {
                                "text": "Are you sure you want to book this room ?",
                                "callback_id": "booking",
                                "color": "warning",
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

    def show_booking_confirmation(self, room_type, date_period, email):
        dates = date_period.split("/")
        confimationId = shortuuid.ShortUUID().random(length=6).upper()
        message = {
            "as_user": False,
            "replace_original": True,
            "response_type": "ephemeral",
            "text": "*Booking Confirmation:*:\n Here's details about your booking at Hotel California.",
            "attachments": [{
                "attachment_type": "default",
                "mrkdwn_in": ["text", "pretext"],
                "color": "good",
                "text": "Booking Confirmation ID: " + confimationId + "\n"
                        "Email: " + email + "\n"
                        "Room Type: " + room_type + "\n"
                        "Date: " + dates[0] + " to " + dates[1]  + "\n",
                "callback_id": "booking",
                "actions": [
                    {
                        "name": "email_confirmation",
                        "text": ":email: Send Email Confirmation",
                        "type": "button",
                        "value": "email_confirmation"
                    },
                    {
                        "name": "sms_confirmation",
                        "text": ":phone: Send SMS Confirmation",
                        "type": "button",
                        "value": "sms_confirmation"
                    }
                ]
                
            }]}
        return json.dumps(message)

    def show_room_not_available(self, room_type, date_period):
        message = {
        "as_user": False,
        "replace_original": False,
        "response_type": "ephemeral",
        "text": "Sorry. Room you are looking is no more available."
        }
        return json.dumps(message)


    def show_email_sent(self, room_type, date_period, email):
        
        message = {
            "as_user": False,
            "replace_original": False,
            "response_type": "ephemeral",
            "text": "I have sent booking confirmation email to " + email + ". Thanks for choosing Hotel California.",
            }
        return json.dumps(message)

    def show_sms_sent(self, room_type, date_period, mobile):
        
        message = {
            "as_user": False,
            "replace_original": False,
            "response_type": "ephemeral",
            "text": "I have sent booking confirmation to " + mobile + ". Thanks for choosing Hotel California.",
            }
        return json.dumps(message)