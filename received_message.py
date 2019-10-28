import os
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/receive_message", methods=['GET', 'POST'])
def sms_reply():
    resp = MessagingResponse()

    resp.message("the robots are coming! head for the  hills!")

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
