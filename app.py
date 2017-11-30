# -*- coding: utf-8 -*-
"""
In this file, we'll create a routing layer to handle incoming and outgoing
requests between our bot and Slack.
"""
import json
import jinja2
from flask import render_template, request, make_response
from slackeventsapi import SlackEventAdapter
from bot import Bot
from python_mysql_connect import iter_row, getRoomType, getRoomInfo, getAvailableRoomInfo, getRoomAvailabilityByType, getRoomAvailabilityByDate, bookRoom
from mail_sender import send_mail


mybot = Bot()
events_adapter = SlackEventAdapter(mybot.verification, "/slack")

template_loader = jinja2.ChoiceLoader([
                    events_adapter.server.jinja_loader,
                    jinja2.FileSystemLoader(['templates']),
                  ])
events_adapter.server.jinja_loader = template_loader


@events_adapter.server.route("/install", methods=["GET"])
def before_install():
    """
    This route renders an installation page for our app!
    """
    client_id = mybot.oauth["client_id"]
    return render_template("install.html", client_id=client_id)


@events_adapter.server.route("/thanks", methods=["GET"])
def thanks():
    """
    This route renders a page to thank users for installing our app!
    """
    auth_code = request.args.get('code')
    mybot.auth(auth_code)
    return render_template("thanks.html")


# Here we'll add a route to listen for incoming message button actions
@events_adapter.server.route("/after_button", methods=["GET", "POST"])
def respond():
    """
    This route listens for incoming message button actions from Slack.
    """
    slack_payload = json.loads(request.form.get("payload"))
    print("############################################")
    print(request)

    # get the value of the button press
    action_value = slack_payload["actions"][0].get("value")
    print(action_value)
    print(slack_payload)

    original_msg_obj = slack_payload["original_message"]
    print(original_msg_obj)

    # handle the action
    return action_handler(action_value, original_msg_obj)


# Let's add an event handler for actions taken from message buttons
@events_adapter.on("action")
def action_handler(action_value, original_msg_obj):
    
    original_msg = original_msg_obj["text"]
    print("########### Action Handler ###########", action_value)

    if action_value == "mac":
        return make_response(mybot.show_mac(), 200, {'Content-Type':
                                                     'application/json'})
    if action_value == "win":
        return make_response(mybot.show_win(), 200, {'Content-Type':
                                                     'application/json'})

    if action_value == "confirm_booking":
        
        responseObj = mybot.getAPIAIResponseObject(original_msg, "bot_user")

        intent = responseObj["result"]["metadata"]["intentName"]
        room_type = responseObj["result"]["parameters"]["RoomType"]
        date_period = responseObj["result"]["parameters"]["date-period"]
        email = getEmailId(original_msg)

        bActionComplete = responseObj["result"]["actionIncomplete"] == False
        
        print(intent, room_type, date_period, bActionComplete)
        
        arr_available_rooms = getRoomAvailabilityByType(room_type)

        if len(arr_available_rooms) == 0:
            return make_response(mybot.show_room_not_available(room_type, date_period), 200, {'Content-Type':
                                                        'application/json'})
        else:
            dates = date_period.split("/")   
            bookRoom(0, dates[0], dates[1], "", "", "", "", "", "", email, "", "", 0,0,"","", arr_available_rooms[0])
            
            return make_response(mybot.show_booking_confirmation(room_type, date_period, email), 200, {'Content-Type':
                                                        'application/json'})

    
    if action_value == "email_confirmation":
        print("$$$$$$$$$$$$$$$$$$$ original_msg $$$$$$$$$$$$$$$$$$$$$$")
        attachment_msg = original_msg_obj["attachments"][0]["text"]
        responseObj = mybot.getAPIAIResponseObject(attachment_msg, "bot_user")
        
        intent = responseObj["result"]["metadata"]["intentName"]
        room_type = responseObj["result"]["parameters"]["RoomType"]
        date_period = responseObj["result"]["parameters"]["date-period"]
        email = getEmailId(attachment_msg)
        dates = date_period.split("/") 

        print(intent, room_type, date_period, email)
        
        email_subject = "Booking Confirmation"
        email_body = "Dear " + email + ", \n\nHere is your booking details at Hotel California. \n\n"  \
                     "Room Type: " + room_type + "\n"  \
                     "CheckIn Date: " + dates[0] + "\n"  \
                     "CheckOut Date: " + dates[1] + "\n\n" \
                     "Thank you for choosing Hotel California."

        send_mail(email, email_subject, email_body)

        return make_response(mybot.show_email_sent(room_type, date_period, email), 200, {'Content-Type':
                                                        'application/json'})


    return "No action handler found for %s type actions" % action_value
    pass


@events_adapter.on("message")
def handle_message(event_data):
    message = event_data["event"]

    subtype = message.get('subtype')
    if subtype == None:
        mybot.handleMessage(message)

# Here's some helpful debugging hints for checking that env vars are set
@events_adapter.server.before_first_request
def before_first_request():
    client_id = mybot.oauth.get("client_id")
    client_secret = mybot.oauth.get("client_secret")
    verification = mybot.verification
    if not client_id:
        print("Can't find Client ID, did you set this env variable?")
    if not client_secret:
        print("Can't find Client Secret, did you set this env variable?")
    if not verification:
        print("Can't find Verification Token, did you set this env variable?")

def getEmailId(s):
    _,_,rest = s.partition("<mailto:")
    result,_,_ = rest.partition("|")
    return result

if __name__ == '__main__':
    events_adapter.start(debug=True)
