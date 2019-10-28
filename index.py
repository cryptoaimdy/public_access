from flask import Flask, request, jsonify, render_template
import os
import dialogflow
import requests
import json
import time
#import pusher
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# initialize Pusher

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/receive_message", methods=['GET', 'POST'])
def message_reply():
    print (request.values)
    body = request.values.get('Body', None) #https://www.twilio.com/docs/sms/tutorials/how-to-receive-and-reply-python
    project_id = os.getenv('DIALOGFLOW_PROJECT_ID')
    session_id = request.values.get('From', None)
    fulfillment_text = detect_intent_texts(project_id, session_id, body, 'en')

    resp = MessagingResponse()

    resp.message(fulfillment_text)
    time.sleep(0.5)
    return str(resp)


@app.route('/get_movie_detail', methods=['POST'])
def get_movie_detail():
    data = request.get_json(silent=True)
    
    try:
        movie = data['queryResult']['parameters']['movie']
        api_key = os.getenv('OMDB_API_KEY')
        
        movie_detail = requests.get('http://www.omdbapi.com/?t={0}&apikey={1}'.format(movie, api_key)).content
        movie_detail = json.loads(movie_detail)

        response =  """
            Title : {0}
            Released: {1}
            Actors: {2}
            Plot: {3}
        """.format(movie_detail['Title'], movie_detail['Released'], movie_detail['Actors'], movie_detail['Plot'])
    except:
        response = "Could not get movie detail at the moment, please try again"
    
    reply = { "fulfillmentText": response }
    
    return jsonify(reply)

def detect_intent_texts(project_id, session_id, text, language_code):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)
    
    if text:
        text_input = dialogflow.types.TextInput(
            text=text, language_code=language_code)
        query_input = dialogflow.types.QueryInput(text=text_input)
        response = session_client.detect_intent(
            session=session, query_input=query_input)
        
        return response.query_result.fulfillment_text

@app.route('/send_message', methods=['POST'])
def send_message():
    try:
        socketId = request.form['socketId']
    except KeyError:
        socketId = ''
        
    message = request.form['message']
    project_id = os.getenv('DIALOGFLOW_PROJECT_ID')
    fulfillment_text = detect_intent_texts(project_id, "unique", message, 'en')
    response_text = { "message":  fulfillment_text }
                        
    return jsonify(response_text)

# run Flask app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True, threaded=True)
