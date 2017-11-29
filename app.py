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
    # get the value of the button press
    action_value = slack_payload["actions"][0].get("value")
    original_msg = slack_payload["original_message"]["text"]
    print(original_msg)

    # handle the action
    return action_handler(action_value, original_msg)


# Let's add an event handler for actions taken from message buttons
@events_adapter.on("action")
def action_handler(action_value, original_msg):
    
    print("########### Action Handler ###########", action_value)

    if action_value == "mac":
        return make_response(mybot.show_mac(), 200, {'Content-Type':
                                                     'application/json'})
    if action_value == "win":
        return make_response(mybot.show_win(), 200, {'Content-Type':
                                                     'application/json'})

    if action_value == "confirm_booking":
        
        print(original_msg)
        responseObj = mybot.getAPIAIResponseObject(original_msg, "bot_user")

        intent = responseObj["result"]["metadata"]["intentName"]
        room_type = responseObj["result"]["parameters"]["RoomType"]
        date_period = responseObj["result"]["parameters"]["date-period"]
        bActionComplete = responseObj["result"]["actionIncomplete"] == False

        print(intent, room_type, date_period, bActionComplete)
        booking_response = book_room()
        #if True:
              
        return make_response(mybot.show_booking_confirmation(room_type, date_period), 200, {'Content-Type':
                                                     'application/json'})
    
    if action_value == "email_confirmation":
        print(original_msg)


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


def book_room():
    return True

if __name__ == '__main__':
    events_adapter.start(debug=True)
