from flask import Flask
from slackify import Slackify, request, async_task, OK
import slack
import json
import time
import requests
import os
import watson_api
import get_exercise
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()

app = Flask(__name__)
slackify = Slackify(app=app)
client = slack.WebClient(os.environ['bot-oauth-token'])


@async_task
def close_db(initial_message_ts):
    # Close database connection after 1 hour starting from initial message
    close_db_time = float(initial_message_ts) + (60 * 60)
    while True:
        if close_db_time == time.time():
            conn.close()


def get_exercise_info(found_body_part, search_type):
    # global exercise_list
    exercise_list = []
    exercise_titles = []

    with open('exercise_data.json', 'r') as f:
        exercise_dict = json.load(f)
    
    for exercise_url in exercise_dict[found_body_part]:
        if "jefit.com" in exercise_url:
            exercise_info = get_exercise.get_exercise_jefit(exercise_url)
            exercise_list.append(exercise_info)
        elif "healthline.com" in exercise_url:
            exercise_info = get_exercise.get_exercise_healthline(exercise_url)
            exercise_list.append(exercise_info)
        elif "ansellchiropractic.com.au" in exercise_url:
            exercise_info = get_exercise.get_exercise_ansell(exercise_url)
            exercise_list.append(exercise_info)

    for exercise_num in range(len(exercise_list)):
        exercise_titles.append(exercise_list[exercise_num]["title"])

    if search_type == "titles":
        return exercise_titles
    elif search_type == "info":
        return exercise_list


@slackify.event("message")
def handle_message(payload):
    # global first_name
    # global found_body_part
    # global exercise_inquiry
    # global exercise_titles
    
    body_parts = ["back", "wrist", "neck", "shoulder", "ankle", "thigh", "calves", "bicep", "tricep", "forearm", "chest", "abs", "glutes"]
    action_items = ["typ", "computer", "ran", "run", "sit", "sat", "lift", "screen", "leg day", "walk"]
    search_criteria = ["back", "wrist", "neck", "shoulder", "ankle", "thigh", "calves", "bicep", "tricep", "forearm", "chest", "abs", "glutes", "typ", "computer", "ran", "run", "sit", "sat", "lift", "screen", "leg day", "walk"]
    event = payload['event']

    with open('actions.json', 'r') as a:
        actions_dict = json.load(a)
    
    if event.get("subtype") is None and event.get("bot_id") is None: 
        original_user_message = event["text"]
        user_id = event["user"]
        user_info = client.users_info(user=user_id)
        username = user_info["user"]["profile"]["real_name_normalized"]
        name_list = username.split(" ")
        first_name = name_list[0]
        
        for search_item in search_criteria:
            if search_item in original_user_message.lower():
                if search_item in action_items:
                    user_message = "{} pain".format(actions_dict[search_item])
                    found_body_part = actions_dict[search_item]

                if search_item in body_parts:
                    found_body_part = search_item
                    user_message = original_user_message

                print(user_message)
                
                exercise_inquiry = watson_api.msg2watson(user_message)
                exercise_titles = get_exercise_info(found_body_part, "titles")
                block = [{
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Hey {}! :grin:\n\n>I read your mind and felt your {} pain from over here!\n>\n>{}".format(first_name, found_body_part, exercise_inquiry)
                    },
                    "accessory": {
                    "type": "image",
                    "image_url": "https://i.imgur.com/rNXe81s.png",
                    "alt_text": "happy paca"
                    }
                    },
                    {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "emoji": True,
                                "text": exercise_titles[0]
                            },
                            "value": "exercise0", 
                            "action_id": "exercise0"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "emoji": True,
                                "text": exercise_titles[1]
                            },
                            "value": "exercise1", 
                            "action_id": "exercise1"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "emoji": True,
                                "text": exercise_titles[2]
                            },
                            "value": "exercise2", 
                            "action_id": "exercise2"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "emoji": True,
                                "text": "Nah, I'm good"
                            },
                            "style": "danger",
                            "value": "no", 
                            "action_id": "no"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "emoji": True,
                                "text": "Remind Me Later!"
                            },
                            "value": "no", 
                            "action_id": "remind_me"
                        }
                    ]
                }
                
            ]

                if exercise_inquiry == "needs more info":
                    client.chat_postMessage(channel=user_id, text="You typed: {}".format(user_message))
                    client.chat_postMessage(channel=user_id, text="Would you like stretches/exercises for your affected body part(s)? Please provide more insight.:grin:")
                else:
                    # Send initial message as a Direct Message to the user
                    initial_message = client.chat_postMessage(channel=user_id, blocks=block)
                    initial_message_ts = initial_message["ts"]
                    close_db(initial_message_ts)

                    # Adjust any exercise titles that contain an apostrophe
                    for title in exercise_titles:
                        new_title_list = []
                        if "'" in title:
                            title_index = exercise_titles.index(title)
                            for letter in title:
                                new_title_list.append(letter)
                            apostrophe_index = new_title_list.index("'")
                            new_title_list.insert(apostrophe_index, "'")
                            new_title = "".join(new_title_list)
                            exercise_titles[title_index] = new_title

                    print(exercise_titles)

                    # Add/Update user's ID & exercise info
                    cur.execute("SELECT exists(SELECT 1 FROM users WHERE (user_id) = '{}')".format(user_id))
                    user_exists = cur.fetchall()[0][0]
                    print(user_exists)
                    if user_exists:
                        update_found_body_part = "UPDATE users SET found_body_part = '{}' WHERE user_id = '{}'".format(found_body_part, user_id)
                        update_exercise_inquiry = "UPDATE users SET exercise_inquiry = '{}' WHERE user_id = '{}'".format(exercise_inquiry, user_id)
                        update_exercises = "UPDATE users SET exercise0 = '{}', exercise1 = '{}', exercise2 = '{}' WHERE user_id = '{}'".format(exercise_titles[0], exercise_titles[1], exercise_titles[2], user_id)
                        
                        cur.execute(update_found_body_part)
                        cur.execute(update_exercise_inquiry)
                        cur.execute(update_exercises)
                        conn.commit()
                    elif not user_exists:
                        add_new_user = "INSERT INTO users (user_id) VALUES('{}')".format(user_id)
                        update_found_body_part = "UPDATE users SET found_body_part = '{}' WHERE user_id = '{}'".format(found_body_part, user_id)
                        update_exercise_inquiry = "UPDATE users SET exercise_inquiry = '{}' WHERE user_id = '{}'".format(exercise_inquiry, user_id)
                        update_exercises = "UPDATE users SET exercise0 = '{}', exercise1 = '{}', exercise2 = '{}' WHERE user_id = '{}'".format(exercise_titles[0], exercise_titles[1], exercise_titles[2], user_id)
                        
                        cur.execute(add_new_user)
                        cur.execute(update_found_body_part)
                        cur.execute(update_exercise_inquiry)
                        cur.execute(update_exercises)
                        conn.commit()
                                 

@slackify.action("remind_me")
def remind_me():
    action = json.loads(request.form["payload"])
    user_id = action["user"]["id"]

    block = [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "When would you like to be reminded?"
        },
        "accessory": {
            "action_id": "remind_me_selection",
            "type": "static_select",
            "placeholder": {
                "type": "plain_text",
                "text": "Select an option"
            },
        "options": [
            {
            "text": {
                "type": "plain_text",
                "text": "10 minutes"
            },
            "value": "10minutes"
            },
            {
            "text": {
                "type": "plain_text",
                "text": "30 minutes"
            },
            "value": "30minutes"
            },
            {
            "text": {
                "type": "plain_text",
                "text": "1 hour"
            },
            "value": "1hour"
            },
            {
            "text": {
                "type": "plain_text",
                "text": "4 hours"
            },
            "value": "4hours"
            },
            {
            "text": {
                "type": "plain_text",
                "text": "Tomorrow"
            },
            "value": "tomorrow"
            }
        ]
        }
    }]

    client.chat_postMessage(channel=user_id, blocks=block)
   

@slackify.action("remind_me_selection")
def remind_me_selection():
    action = json.loads(request.form["payload"])
    user_id = action["user"]["id"]
    remind_me_msg = action["actions"][0]["selected_option"]["text"]["text"]
    remind_me_value = action["actions"][0]["selected_option"]["value"]
    remind_me_ts = action["actions"][0]["action_ts"]

    client.chat_postMessage(channel=user_id, text="*Awesome! Your reminder has been set for {}. :alarm_clock:*".format(remind_me_msg))

    if remind_me_value == "10minutes":
        scheduled_time = float(remind_me_ts) + (10 * 60)
    elif remind_me_value == "30minutes":
        scheduled_time = float(remind_me_ts) + (30 * 60)
    elif remind_me_value == "1hour":
        scheduled_time = float(remind_me_ts) + (60 * 60)
    elif remind_me_value == "4hours":
        scheduled_time = float(remind_me_ts) + (240 * 60)
    elif remind_me_value == "tomorrow":
        scheduled_time = float(remind_me_ts) + (1440 * 60)

    remind_me_message(user_id, scheduled_time)


def remind_me_message(user_id, scheduled_time):
    # Get exercise_inquiry and found_body_part from db
    get_exercise_inquiry = cur.execute("SELECT exercise_inquiry FROM users WHERE user_id = '{}'".format(user_id))
    exercise_inquiry = cur.fetchall()[0][0]
    get_found_body_part = cur.execute("SELECT found_body_part FROM users WHERE user_id = '{}'".format(user_id))
    found_body_part = cur.fetchall()[0][0]

    exercise_titles = get_exercise_info(found_body_part, "titles")

    block = [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": 'Hey again! :grin:\n\n>I read your mind and felt your {} pain from over here!\n>\n>{}\n>\n>If you have another pained body part, *please type* "My [insert pained body part] hurts" (_e.g.: My neck hurts_).'.format(found_body_part, exercise_inquiry)
        },
        "accessory": {
        "type": "image",
        "image_url": "https://i.imgur.com/rNXe81s.png",
        "alt_text": "happy paca"
        }
        },
        {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": exercise_titles[0]
                },
                "value": "exercise0", 
                "action_id": "exercise0"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": exercise_titles[1]
                },
                "value": "exercise1", 
                "action_id": "exercise1"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": exercise_titles[2]
                },
                "value": "exercise2", 
                "action_id": "exercise2"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "Nah, I'm good"
                },
                "style": "danger",
                "value": "no", 
                "action_id": "no"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "Remind Me Later!"
                },
                "value": "no", 
                "action_id": "remind_me"
            }
        ]
    }]

    client.chat_scheduleMessage(channel=user_id, post_at=scheduled_time, blocks=block, text="Time to exercise! :tada:")


@slackify.action("exercise0")
def exercise0():
    action = json.loads(request.form["payload"])
    user_id = action["user"]["id"]
    exercise_num = 0

    # Get exercise title from db and update exercise_num
    select_exercise_title = cur.execute("SELECT exercise{} FROM users WHERE user_id = '{}'".format(exercise_num, user_id))
    exercise_title = cur.fetchall()[0][0]
    cur.execute("UPDATE users SET exercise_num = '{}' WHERE user_id = '{}'".format(exercise_num, user_id))
    conn.commit()

    block = [{
        "type": "divider"
        },
        {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "Would you like to see images, instructions, or both for the *{}* exercise?".format(exercise_title)
        }
        },
        {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "See Images"
                },
                "value": "see_images", 
                "action_id": "see_images"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "See Instructions"
                },
                "value": "see_instructions", 
                "action_id": "see_instructions"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "See Both"
                },
                "value": "see_both", 
                "action_id": "see_both"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "Nah, I'm good"
                },
                "style": "danger",
                "value": "no", 
                "action_id": "no"
            }
        ]
    }]

    client.chat_postMessage(channel=user_id, blocks=block)


@slackify.action("exercise1")
def exercise1():
    action = json.loads(request.form["payload"])
    user_id = action["user"]["id"]
    exercise_num = 1

    # Get exercise title from db and update exercise_num
    select_exercise_title = cur.execute("SELECT exercise{} FROM users WHERE user_id = '{}'".format(exercise_num, user_id))
    exercise_title = cur.fetchall()[0][0]
    cur.execute("UPDATE users SET exercise_num = '{}' WHERE user_id = '{}'".format(exercise_num, user_id))
    conn.commit()

    block = [{
        "type": "divider"
        },
        {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "Would you like to see images, instructions, or both for the *{}* exercise?".format(exercise_title)
        }
        },
        {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "See Images"
                },
                "value": "see_images", 
                "action_id": "see_images"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "See Instructions"
                },
                "value": "see_instructions", 
                "action_id": "see_instructions"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "See Both"
                },
                "value": "see_both", 
                "action_id": "see_both"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "Nah, I'm good"
                },
                "style": "danger",
                "value": "no", 
                "action_id": "no"
            }
        ]
    }]

    client.chat_postMessage(channel=user_id, blocks=block)


@slackify.action("exercise2")
def exercise2():
    action = json.loads(request.form["payload"])
    user_id = action["user"]["id"]
    exercise_num = 2

    # Get exercise title from db and update exercise_num
    select_exercise_title = cur.execute("SELECT exercise{} FROM users WHERE user_id = '{}'".format(exercise_num, user_id))
    exercise_title = cur.fetchall()[0][0]
    cur.execute("UPDATE users SET exercise_num = '{}' WHERE user_id = '{}'".format(exercise_num, user_id))
    conn.commit()

    block = [{
        "type": "divider"
        },
        {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "Would you like to see images, instructions, or both for the *{}* exercise?".format(exercise_title)
        }
        },
        {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "See Images"
                },
                "value": "see_images", 
                "action_id": "see_images"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "See Instructions"
                },
                "value": "see_instructions", 
                "action_id": "see_instructions"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "See Both"
                },
                "value": "see_both", 
                "action_id": "see_both"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "Nah, I'm good"
                },
                "style": "danger",
                "value": "no", 
                "action_id": "no"
            }
        ]
    }]

    client.chat_postMessage(channel=user_id, blocks=block)


@slackify.action("see_images")
def see_images():
    action = json.loads(request.form["payload"])
    user_id = action["user"]["id"] 
    num_of_images = 0 

    headers = {"Content-Type": "application/json"}
    replacement_message = {"text": "Okay! Please wait while I gather the images..."}
    requests.post(url=action["response_url"], headers=headers, json=replacement_message)

    # Get exercise_num, exercise title, and found_body_part from db
    get_exercise_num = cur.execute("SELECT exercise_num FROM users WHERE user_id = '{}'".format(user_id))
    exercise_num = cur.fetchall()[0][0]
    select_exercise_title = cur.execute("SELECT exercise{} FROM users WHERE user_id = '{}'".format(exercise_num, user_id))
    exercise_title = cur.fetchall()[0][0]
    get_found_body_part = cur.execute("SELECT found_body_part FROM users WHERE user_id = '{}'".format(user_id))
    found_body_part = cur.fetchall()[0][0]

    intro_block = [{
        "type": "divider"
        },
        {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*Here are the images for the {}:*".format(exercise_title)
        }
    }]

    client.chat_postMessage(channel=user_id, blocks=intro_block)

    exercise_list = get_exercise_info(found_body_part, "info")

    if exercise_list[exercise_num]["domain"] == "jefit":
        for exercise_key in exercise_list[exercise_num].keys():
            if "image" in exercise_key:
                num_of_images += 1

        for img_num in range(1, num_of_images + 1):
            exercise_title = exercise_list[exercise_num]["title"] + " - Position {}".format(img_num)
            image_url = exercise_list[exercise_num]["image{}".format(img_num)]
            attachments = [{"title": exercise_title, "image_url": image_url}]
            client.chat_postMessage(channel=user_id, attachments=attachments)

    elif exercise_list[exercise_num]["domain"] == "healthline":
        image_url = exercise_list[exercise_num]["image1"]
        attachments = [{"title": exercise_list[exercise_num]["title"], "image_url": image_url}]
        client.chat_postMessage(channel=user_id, attachments=attachments)

    elif exercise_list[exercise_num]["domain"] == "ansell":
        image_url = exercise_list[exercise_num]["image1"]
        video_url = exercise_list[exercise_num]["video1"]
        attachments = [{"title": exercise_list[exercise_num]["title"], "image_url": image_url}]
        client.chat_postMessage(channel=user_id, attachments=attachments) 
        client.chat_postMessage(channel=user_id, text=video_url)

    block = [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "Would you like to *start the stretch or exercise* now or see *step-by-step instructions*?"
        }
        },
        {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "Yeah, let's do it"
                },
                "style": "primary",
                "value": "load_timer", 
                "action_id": "load_timer"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "See Instructions"
                },
                "value": "see_instructions_sub", 
                "action_id": "see_instructions_sub"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "Nah, I'm good"
                },
                "style": "danger",
                "value": "no", 
                "action_id": "no"
            }
        ]
    }]

    client.chat_postMessage(channel=user_id, blocks=block)


@slackify.action("see_instructions")
def see_instructions():
    action = json.loads(request.form["payload"])
    user_id = action["user"]["id"]

    headers = {"Content-Type": "application/json"}
    replacement_message = {"text": "Okay! Please wait while I gather the instructions..."}
    requests.post(url=action["response_url"], headers=headers, json=replacement_message)

    # Get exercise_num, exercise title, and found_body_part from db
    get_exercise_num = cur.execute("SELECT exercise_num FROM users WHERE user_id = '{}'".format(user_id))
    exercise_num = cur.fetchall()[0][0]
    select_exercise_title = cur.execute("SELECT exercise{} FROM users WHERE user_id = '{}'".format(exercise_num, user_id))
    exercise_title = cur.fetchall()[0][0]
    get_found_body_part = cur.execute("SELECT found_body_part FROM users WHERE user_id = '{}'".format(user_id))
    found_body_part = cur.fetchall()[0][0]

    exercise_list = get_exercise_info(found_body_part, "info")
    exercise_steps = exercise_list[exercise_num]["steps"]
    exercise_steps_split = exercise_steps.split("\n\r\n")
    exercise_steps_list = []

    # if exercise_list[exercise_num]["domain"] == "jefit":
    for exercise_step in exercise_steps_split:
        if "Steps" not in exercise_step:
            indented_exercise = ">{}".format(exercise_step)
            exercise_steps_list.append(indented_exercise)
            exercise_steps_list.append("\n>\r\n")
    indented_exercise_steps = "".join(exercise_steps_list)

    steps_block = [{
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Here are the step-by-step instructions for the {}:*".format(exercise_title)
            }
        },        
        {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": indented_exercise_steps
        }
        }]

    client.chat_postMessage(channel=user_id, blocks=steps_block)

    block = [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "Would you like to *start the stretch or exercise* now or *see step-by-step images*?"
        }
        },
        {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "Yeah, let's do it"
                },
                "style": "primary",
                "value": "load_timer", 
                "action_id": "load_timer"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "See Images"
                },
                "value": "see_images_sub", 
                "action_id": "see_images_sub"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "Nah, I'm good"
                },
                "style": "danger",
                "value": "no", 
                "action_id": "no"
            }
        ]
    }]

    client.chat_postMessage(channel=user_id, blocks=block)


@slackify.action("see_both")
def see_both():
    action = json.loads(request.form["payload"])
    user_id = action["user"]["id"]
    num_of_images = 0

    headers = {"Content-Type": "application/json"}
    replacement_message = {"text": "Okay! Please wait while I gather the images and instructions..."}
    requests.post(url=action["response_url"], headers=headers, json=replacement_message) 

    # Get exercise_num, exercise title, and found_body_part from db
    get_exercise_num = cur.execute("SELECT exercise_num FROM users WHERE user_id = '{}'".format(user_id))
    exercise_num = cur.fetchall()[0][0]
    select_exercise_title = cur.execute("SELECT exercise{} FROM users WHERE user_id = '{}'".format(exercise_num, user_id))
    exercise_title = cur.fetchall()[0][0]
    get_found_body_part = cur.execute("SELECT found_body_part FROM users WHERE user_id = '{}'".format(user_id))
    found_body_part = cur.fetchall()[0][0]

    exercise_list = get_exercise_info(found_body_part, "info")

    intro_block = [{
        "type": "divider"
        },
        {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*Here are both the images and step-by-step instructions for the {}:*".format(exercise_title)
        }
    }]

    client.chat_postMessage(channel=user_id, blocks=intro_block)

    if exercise_list[exercise_num]["domain"] == "jefit":
        for exercise_key in exercise_list[exercise_num].keys():
            if "image" in exercise_key:
                num_of_images += 1

        for img_num in range(1, num_of_images + 1):
            exercise_title = exercise_list[exercise_num]["title"] + " - Position {}".format(img_num)
            image_url = exercise_list[exercise_num]["image{}".format(img_num)]
            attachments = [{"title": exercise_title, "image_url": image_url}]
            client.chat_postMessage(channel=user_id, attachments=attachments)

    elif exercise_list[exercise_num]["domain"] == "healthline":
        image_url = exercise_list[exercise_num]["image1"]
        attachments = [{"title": exercise_list[exercise_num]["title"], "image_url": image_url}]
        client.chat_postMessage(channel=user_id, attachments=attachments)

    elif exercise_list[exercise_num]["domain"] == "ansell":
        image_url = exercise_list[exercise_num]["image1"]
        video_url = exercise_list[exercise_num]["video1"]
        attachments = [{"title": exercise_list[exercise_num]["title"], "image_url": image_url}]
        client.chat_postMessage(channel=user_id, attachments=attachments)
        client.chat_postMessage(channel=user_id, text=video_url)

    # Send exercise steps
    exercise_steps = exercise_list[exercise_num]["steps"]
    exercise_steps_split = exercise_steps.split("\n\r\n")
    exercise_steps_list = []

    for exercise_step in exercise_steps_split:
        if "Steps" not in exercise_step:
            indented_exercise = ">{}".format(exercise_step)
            exercise_steps_list.append(indented_exercise)
            exercise_steps_list.append("\n>\r\n")

    indented_exercise_steps = "".join(exercise_steps_list)

    steps_block = [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": indented_exercise_steps
        }
        }]

    client.chat_postMessage(channel=user_id, blocks=steps_block)

    block = [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "Would you like to *start the stretch or exercise* now?"
        }
        },
        {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "Yeah, let's do it"
                },
                "style": "primary",
                "value": "load_timer", 
                "action_id": "load_timer"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "Nah, I'm good"
                },
                "style": "danger",
                "value": "no", 
                "action_id": "no"
            }
        ]
    }]

    client.chat_postMessage(channel=user_id, blocks=block)


@slackify.action("see_images_sub")
def see_images_sub():
    action = json.loads(request.form["payload"])
    user_id = action["user"]["id"]
    num_of_images = 0 

    headers = {"Content-Type": "application/json"}
    replacement_message = {"text": "Okay! Please wait while I gather the images..."}
    requests.post(url=action["response_url"], headers=headers, json=replacement_message)

    # Get exercise_num, exercise title, and found_body_part from db
    get_exercise_num = cur.execute("SELECT exercise_num FROM users WHERE user_id = '{}'".format(user_id))
    exercise_num = cur.fetchall()[0][0]
    select_exercise_title = cur.execute("SELECT exercise{} FROM users WHERE user_id = '{}'".format(exercise_num, user_id))
    exercise_title = cur.fetchall()[0][0]
    get_found_body_part = cur.execute("SELECT found_body_part FROM users WHERE user_id = '{}'".format(user_id))
    found_body_part = cur.fetchall()[0][0]

    exercise_list = get_exercise_info(found_body_part, "info")

    intro_block = [{
        "type": "divider"
        },
        {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*Here are the images for the {}:*".format(exercise_title)
        }
    }]

    client.chat_postMessage(channel=user_id, blocks=intro_block)

    if exercise_list[exercise_num]["domain"] == "jefit":
        for exercise_key in exercise_list[exercise_num].keys():
            if "image" in exercise_key:
                num_of_images += 1

        for img_num in range(1, num_of_images + 1):
            exercise_title = exercise_list[exercise_num]["title"] + " - Position {}".format(img_num)
            image_url = exercise_list[exercise_num]["image{}".format(img_num)]
            attachments = [{"title": exercise_title, "image_url": image_url}]
            client.chat_postMessage(channel=user_id, attachments=attachments)

    elif exercise_list[exercise_num]["domain"] == "healthline":
        image_url = exercise_list[exercise_num]["image1"]
        attachments = [{"title": exercise_list[exercise_num]["title"], "image_url": image_url}]
        client.chat_postMessage(channel=user_id, attachments=attachments)

    elif exercise_list[exercise_num]["domain"] == "ansell":
        image_url = exercise_list[exercise_num]["image1"]
        video_url = exercise_list[exercise_num]["video1"]
        attachments = [{"title": exercise_list[exercise_num]["title"], "image_url": image_url}]
        client.chat_postMessage(channel=user_id, attachments=attachments)
        client.chat_postMessage(channel=user_id, text=video_url)

    block = [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "Would you like to *start the stretch or exercise* now?"
        }
        },
        {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "Yeah, let's do it"
                },
                "style": "primary",
                "value": "load_timer", 
                "action_id": "load_timer"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "Nah, I'm good"
                },
                "style": "danger",
                "value": "no", 
                "action_id": "no"
            }
        ]
    }]

    client.chat_postMessage(channel=user_id, blocks=block)


@slackify.action("see_instructions_sub")
def see_instructions_sub():
    action = json.loads(request.form["payload"])
    user_id = action["user"]["id"]

    headers = {"Content-Type": "application/json"}
    replacement_message = {"text": "Okay! Please wait while I gather the instructions..."}
    requests.post(url=action["response_url"], headers=headers, json=replacement_message)

    # Get exercise_num, exercise title, and found_body_part from db
    get_exercise_num = cur.execute("SELECT exercise_num FROM users WHERE user_id = '{}'".format(user_id))
    exercise_num = cur.fetchall()[0][0]
    select_exercise_title = cur.execute("SELECT exercise{} FROM users WHERE user_id = '{}'".format(exercise_num, user_id))
    exercise_title = cur.fetchall()[0][0]
    get_found_body_part = cur.execute("SELECT found_body_part FROM users WHERE user_id = '{}'".format(user_id))
    found_body_part = cur.fetchall()[0][0]

    exercise_list = get_exercise_info(found_body_part, "info")

    exercise_steps = exercise_list[exercise_num]["steps"]
    exercise_steps_split = exercise_steps.split("\n\r\n")
    exercise_steps_list = []

    for exercise_step in exercise_steps_split:
        if "Steps" not in exercise_step:
            indented_exercise = ">{}".format(exercise_step)
            exercise_steps_list.append(indented_exercise)
            exercise_steps_list.append("\n>\r\n")

    indented_exercise_steps = "".join(exercise_steps_list)

    steps_block = [{
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Here are the step-by-step instructions for the {}:*".format(exercise_list[exercise_num]["title"])
            }
        },        
        {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": indented_exercise_steps
        }
        }]

    client.chat_postMessage(channel=user_id, blocks=steps_block)

    block = [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "Would you like to *start the stretch or exercise* now?"
        }
        },
        {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "Yeah, let's do it"
                },
                "style": "primary",
                "value": "load_timer", 
                "action_id": "load_timer"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "Nah, I'm good"
                },
                "style": "danger",
                "value": "no", 
                "action_id": "no"
            }
        ]
    }]

    client.chat_postMessage(channel=user_id, blocks=block)


@slackify.action("load_timer")
def load_timer():
    # global amount_of_seconds
    # global initial_timer_ts
    # global initial_timer_channel
    action = json.loads(request.form["payload"])
    user_id = action["user"]["id"]

    headers = {"Content-Type": "application/json"}
    replacement_message = {"text": "Okay! Please wait while I load the timer..."}
    requests.post(url=action["response_url"], headers=headers, json=replacement_message)

    # Get exercise_num and found_body_part from db
    get_exercise_num = cur.execute("SELECT exercise_num FROM users WHERE user_id = '{}'".format(user_id))
    exercise_num = cur.fetchall()[0][0]
    get_found_body_part = cur.execute("SELECT found_body_part FROM users WHERE user_id = '{}'".format(user_id))
    found_body_part = cur.fetchall()[0][0]

    exercise_list = get_exercise_info(found_body_part, "info")

    exercise_steps = exercise_list[exercise_num]["steps"]
    exercise_steps_into_list = exercise_list[exercise_num]["steps"].split(" ")

    if "seconds" in exercise_steps_into_list:
        seconds_index = exercise_steps_into_list.index("seconds")
        amount_of_seconds = exercise_steps_into_list[seconds_index - 1]

    if "seconds," in exercise_steps_into_list:
        seconds_index = exercise_steps_into_list.index("seconds,")
        amount_of_seconds = exercise_steps_into_list[seconds_index - 1]

    if "amount_of_seconds" in locals():
        # Add amount_of_seconds to db
        update_amount_of_seconds = "UPDATE users SET amount_of_seconds = '{}' WHERE user_id = '{}'".format(amount_of_seconds, user_id)
        cur.execute(update_amount_of_seconds)
        get_found_body_part = cur.execute("SELECT found_body_part FROM users WHERE user_id = '{}'".format(user_id))
        found_body_part = cur.fetchall()[0][0]

        # Send Initial Timer with seconds
        block = [{
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Timer: {} seconds".format(amount_of_seconds)
            }
            },
            {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "Start Timer"
                    },
                    "style": "primary",
                    "value": "start_timer", 
                    "action_id": "start_timer"
                }
            ]
        }]

        initial_timer = client.chat_postMessage(channel=user_id, blocks=block)
        initial_timer_ts = initial_timer["ts"]
        initial_timer_channel = initial_timer["channel"]

        # Update initial_timer_ts and initial_timer_channel in db and commit everything
        update_initial_timer_ts = "UPDATE users SET initial_timer_ts = '{}' WHERE user_id = '{}'".format(initial_timer_ts, user_id)
        cur.execute(update_initial_timer_ts)
        update_initial_timer_channel = "UPDATE users SET initial_timer_channel = '{}' WHERE user_id = '{}'".format(initial_timer_channel, user_id)
        cur.execute(update_initial_timer_channel)
        conn.commit()
        
    
    else:
        # No seconds in steps -> do not send timer
        block_another = [{
            "type": "divider"
            },
            {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "You're doing great! Would you like to see another stretch or exercise?"
            }
            },
            {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "Yes"
                    },
                    "style": "primary",
                    "value": "another_exercise",
                    "action_id": "another_exercise"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "No thanks"
                    },
                    "style": "danger",
                    "value": "no", 
                    "action_id": "no"
                }
            ]
        }]

        client.chat_postMessage(channel=user_id, text="This workout has no instructed time limit. Feel free to follow the steps at your own pace. :smile:")
        time.sleep(10)
        client.chat_postMessage(channel=user_id, blocks=block_another)
        

@slackify.action("start_timer")
def start_timer():
    action = json.loads(request.form["payload"])
    user_id = action["user"]["id"]

    # Get amount_of_seconds, initial_timer_ts, and initial_timer_channel from db
    get_amount_of_seconds = cur.execute("SELECT amount_of_seconds FROM users WHERE user_id = '{}'".format(user_id))
    amount_of_seconds = cur.fetchall()[0][0]
    get_initial_timer_ts = cur.execute("SELECT initial_timer_ts FROM users WHERE user_id = '{}'".format(user_id))
    initial_timer_ts = cur.fetchall()[0][0]
    get_initial_timer_channel = cur.execute("SELECT initial_timer_channel FROM users WHERE user_id = '{}'".format(user_id))
    initial_timer_channel = cur.fetchall()[0][0]

    for second in reversed(range(int(amount_of_seconds) + 1)):
        if int(amount_of_seconds) <= 15:
            block = [{
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Timer: {} seconds".format(second)
                }
                },
                {
					"type": "image",
                    "image_url": "https://i.imgur.com/dCldD2f.gif",
                    "alt_text": "paca with sparkles"
				},
                {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "emoji": True,
                            "text": ":hourglass_flowing_sand:Timer Started:hourglass_flowing_sand:"
                        },
                        "value": "do_nothing", 
                        "action_id": "do_nothing"
                    }
                ]
            }]

        elif int(amount_of_seconds) in range(15, 31):
            block = [{
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Timer:* {} *seconds*".format(second)
                }
                },
                {
					"type": "image",
                    "image_url": "https://i.imgur.com/NxTxMuW.gif",
                    "alt_text": "paca good"
				},
                {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "emoji": True,
                            "text": ":hourglass_flowing_sand:Timer Started:hourglass_flowing_sand:"
                        },
                        "value": "do_nothing", 
                        "action_id": "do_nothing"
                    }
                ]
            }]

        elif int(amount_of_seconds) > 30:
            block = [{
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Timer: {} seconds".format(second)
                }
                },
                {
					"type": "image",
                    "image_url": "https://i.imgur.com/7WdEmoN.gif",
                    "alt_text": "vaporwave paca"
				},
                {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "emoji": True,
                            "text": ":hourglass_flowing_sand:Timer Started:hourglass_flowing_sand:"
                        },
                        "value": "do_nothing", 
                        "action_id": "do_nothing"
                    }
                ]
            }]

        # Finished block
        block_done = [{
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": ":tada: *Timer Done* :tada:"
            }
            }]

        # Another exercise block
        block_another = [{
            "type": "divider"
            },
            {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "You're doing great! Would you like to see another stretch or exercise?"
            }
            },
            {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "Yes"
                    },
                    "style": "primary",
                    "value": "another_exercise",
                    "action_id": "another_exercise"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "No thanks"
                    },
                    "style": "danger",
                    "value": "no", 
                    "action_id": "no"
                }
            ]
        }]
        
        if second == 0:
            client.chat_update(channel=initial_timer_channel, blocks=block_done, ts=initial_timer_ts)
            client.chat_postMessage(channel=user_id, blocks=block_another)
        else:
            client.chat_update(channel=initial_timer_channel, blocks=block, ts=initial_timer_ts)
            time.sleep(1)


@slackify.action("another_exercise")
def another_exercise():
    action = json.loads(request.form["payload"])
    user_id = action["user"]["id"]

    # Get exercise_inquiry and found_body_part from db
    get_exercise_inquiry = cur.execute("SELECT exercise_inquiry FROM users WHERE user_id = '{}'".format(user_id))
    exercise_inquiry = cur.fetchall()[0][0]
    get_found_body_part = cur.execute("SELECT found_body_part FROM users WHERE user_id = '{}'".format(user_id))
    found_body_part = cur.fetchall()[0][0]

    exercise_titles = get_exercise_info(found_body_part, "titles")

    block = [{
        "type": "divider"
        },
        {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": 'You mentioned that you would like to see another stretch!\n\n>{}\n>\n>If you have another pained body part, *please type* "My [insert pained body part] hurts" (_e.g.: My neck hurts_).'.format(exercise_inquiry)
        }
        },
        {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": exercise_titles[0]
                },
                "style": "primary",
                "value": "exercise0", 
                "action_id": "exercise0"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": exercise_titles[1]
                },
                "style": "primary",
                "value": "exercise1", 
                "action_id": "exercise1"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": exercise_titles[2]
                },
                "style": "primary",
                "value": "exercise2", 
                "action_id": "exercise2"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "Nah, I'm good"
                },
                "style": "danger",
                "value": "no", 
                "action_id": "no"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "Remind Me Later!"
                },
                "value": "no", 
                "action_id": "remind_me"
            }
        ]
    }]

    client.chat_postMessage(channel=user_id, blocks=block)


@slackify.action("no")
def no_selected():
    action = json.loads(request.form["payload"])
    user_id = action["user"]["id"]

    block = [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": '*Okay! Make sure to take breaks, hydrate, and stretch periodically!* :smile:'
        }
        },
        {
            "type": "divider"    
        },
        {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "When would you like to be reminded?"
        },
        "accessory": {
            "action_id": "remind_me_selection",
            "type": "static_select",
            "placeholder": {
                "type": "plain_text",
                "text": "Select an option"
            },
        "options": [
            {
            "text": {
                "type": "plain_text",
                "text": "10 minutes"
            },
            "value": "10minutes"
            },
            {
            "text": {
                "type": "plain_text",
                "text": "30 minutes"
            },
            "value": "30minutes"
            },
            {
            "text": {
                "type": "plain_text",
                "text": "1 hour"
            },
            "value": "1hour"
            },
            {
            "text": {
                "type": "plain_text",
                "text": "4 hours"
            },
            "value": "4hours"
            },
            {
            "text": {
                "type": "plain_text",
                "text": "Tomorrow"
            },
            "value": "tomorrow"
            }
        ]
        }
        },
        {
            "type": "divider"    
        }]

    client.chat_postMessage(channel=user_id, blocks=block)
    
    
# ./ngrok http 5000
if __name__ == "__main__":
    app.run(port=5000)
