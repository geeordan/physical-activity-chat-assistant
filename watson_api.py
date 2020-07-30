import json
import os
import requests

def msg2watson(user_message):
  '''
  Usage:
  exercise_inquiry = msg2watson(user_message)
  '''

  apikey = os.environ['watson_apikey']
  session_url = "https://api.us-south.assistant.watson.cloud.ibm.com/v2/assistants/fe893bff-b526-462f-81f3-8b78859bacd4/sessions?version=2020-04-01"
  user = "apikey"
  headers = {"Content-Type": "application/json"}

  # GET session_id
  response = requests.post(auth=(user, apikey), url=session_url)
  result = json.loads(response.content)
  session_id = result['session_id']
  
  # POST message to IBM Watson
  message = {"input": {"text": user_message}}
  message_url = "https://api.us-south.assistant.watson.cloud.ibm.com/v2/assistants/fe893bff-b526-462f-81f3-8b78859bacd4/sessions/{}/message?version=2020-04-01".format(session_id)
  response = requests.post(auth=(user, apikey) , url=message_url, json=message, headers=headers)
  result = json.loads(response.content)

  if result["output"]["generic"][0]["text"] == "I didn't understand can you try again" or result["output"]["intents"][0]["confidence"] < 0.6:
    return "needs more info"
  else:
    exercise_question = result["output"]["generic"][0]["text"]
    exercise_question_split = exercise_question.split(" ")
    please_index = exercise_question_split.index("please")
    before_please = " ".join(exercise_question_split[:please_index])
    full_exercise_inquiry = "{} *please click one of the options below.*".format(before_please)
    
    return full_exercise_inquiry
