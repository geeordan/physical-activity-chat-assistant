import requests
from bs4 import BeautifulSoup
import urllib.request
import os.path
import json


def get_exercise_jefit(jefit_url):
    '''
    Usage:
    exercise_info = get_exercise_jefit(jefit_url)
    '''

    exercise_payload = dict()
    jefit_base_url = "https://www.jefit.com/"

    exercise_response = requests.get(url=jefit_url)
    soup = BeautifulSoup(exercise_response.content, "html.parser")
    
    # Retrieve page title
    page_title = soup.find("div", attrs={"class": ""})
    for title in page_title:
        if "->" in title:
            start_index = title.index(">") + 2
            actual_title = title[start_index::].strip()
    exercise_payload["title"] = actual_title

    # Retrieve image URLs
    image_num = 1
    images = soup.find_all("img", attrs={"alt": actual_title})

    for image in images:
        image_url = image["src"]
        image_src = image_url[9::]
        full_image_url = "{}{}".format(jefit_base_url, image_src)  
        exercise_payload["image{}".format(str(image_num))] = full_image_url
        image_num += 1

    # Retrieve exercise instructions
    how_to_perform = soup.find_all("p", attrs={"class": "p-2"})
    exercise_steps = how_to_perform[1].text.strip()
    exercise_payload["steps"] = exercise_steps

    exercise_payload["domain"] = "jefit"

    return exercise_payload


def get_exercise_healthline(healthline_url):
    '''
    Usage:
    exercise_info = get_exercise_healthline(healthline_url)

    Info:
    Selected ankle exercises: Ankle Circles, Achilles Stretch, Cross Leg Ankle Stretch
    ankle circles = steps[1], achilles stretch = steps[2], Cross leg ankle stretch = steps[7]

    Selected bicep exercises: Standing Bicep Stretch, Seated Bicep Stretch
    standing bicep stretch = steps[0], seated bicep stretch = steps[1]
    '''

    exercise_payload = dict()
    image_prefix = "https:"

    exercise_response = requests.get(url=healthline_url)
    soup = BeautifulSoup(exercise_response.content, "html.parser")

    if "ankle" in healthline_url:
        # Retrieve ankle image URLs
        if "circles" in healthline_url:
            exercise_payload["title"] = "Ankle Circles"
            images = soup.find_all("img", attrs={"alt": "ankle circles"})
            full_image_url = "{}{}".format(image_prefix, images[0]["src"])
            exercise_payload["image1"] = full_image_url
            steps_index = 1
        elif "achilles" in healthline_url:
            exercise_payload["title"] = "Achilles Stretch"
            images = soup.find_all("img", attrs={"alt": "achilles stretch"})
            full_image_url = "{}{}".format(image_prefix, images[0]["src"])
            exercise_payload["image1"] = full_image_url
            steps_index = 2
        elif "cross" in healthline_url:
            exercise_payload["title"] = "Cross Leg Ankle Stretch"
            images = soup.find_all("lazy-image", attrs={"alt": "Cross leg ankle stretch"})
            full_image_url = "{}{}".format(image_prefix, images[0]["src"])
            exercise_payload["image1"] = full_image_url
            steps_index = 7

        # Retrieve ankle exercise instructions 
        p_steps = []
        li_steps = []
        step_num = 1
        exercise_steps = []
        steps = soup.find_all("div", attrs={"class": "css-0"})

        for p in steps[steps_index].find_all('p'):
            p_steps.append(p.text)
        
        for li in steps[steps_index].find_all('li'):
            li_steps.append(li)

        for exercise_step in li_steps:
            full_exercise_step = "{}.) {}".format(step_num, exercise_step.text)
            exercise_steps.append(full_exercise_step)
            exercise_steps.append("\n\r\n")
            step_num += 1
        
        exercise_steps.insert(0, "{}\n\r\n".format(p_steps[0]))
        exercise_steps.append(p_steps[1])
        exercise_payload["steps"] = "".join(exercise_steps)
        exercise_payload["domain"] = "healthline"

    elif "bicep" in healthline_url:
        # Retrieve bicep image URLs
        if "standing" in healthline_url:
            exercise_payload["title"] = "Standing Bicep Stretch"
            images = soup.find_all("img", attrs={"class": "css-1lwg88w"})
            full_image_url = "{}{}".format(image_prefix, images[1]["src"])
            exercise_payload["image1"] = full_image_url
            steps_index = 0
            identifier = "standing"
        elif "seated" in healthline_url:
            exercise_payload["title"] = "Seated Bicep Stretch"
            images = soup.find_all("lazy-image", attrs={"classname": "css-1lwg88w"})
            full_image_url = "{}{}".format(image_prefix, images[0]["src"])
            exercise_payload["image1"] = full_image_url
            steps_index = 1
            identifier = "seated"
        elif "doorway" in healthline_url:
            exercise_payload["title"] = "Doorway Bicep Stretch"
            images = soup.find_all("lazy-image", attrs={"classname": "css-1lwg88w"})
            full_image_url = "{}{}".format(image_prefix, images[1]["src"])
            exercise_payload["image1"] = full_image_url
            steps_index = 2
            identifier = "doorway"

        # Retrieve bicep exercise instructions 
        p_steps = []
        li_steps = []
        step_num = 1
        exercise_steps = []
        steps = soup.find_all("div", attrs={"class": "css-0"})

        for p in steps[steps_index].find_all('p'):
            p_steps.append(p.text)
        
        for li in steps[steps_index].find_all('li'):
            li_steps.append(li)

        for exercise_step in li_steps:
            full_exercise_step = "{}.) {}".format(step_num, exercise_step.text)
            exercise_steps.append(full_exercise_step)
            exercise_steps.append("\n\r\n")
            step_num += 1
        
        exercise_steps.insert(0, "{}\n\r\n".format(p_steps[0]))
        exercise_steps.insert(1, "{}\n\r\n".format(p_steps[1]))
        if identifier != "doorway":
            exercise_steps.append(p_steps[2])
        else:
            del exercise_steps[-1]
        exercise_payload["steps"] = "".join(exercise_steps)
        exercise_payload["domain"] = "healthline"

    return exercise_payload
    

def get_exercise_ansell(ansell_url):
    '''
    Usage:
    exercise_info = get_exercise_ansell(ansell_url)

    Info:
    Includes keys: image1 & video1
    '''

    exercise_payload = dict()

    exercise_response = requests.get(url=ansell_url)
    soup = BeautifulSoup(exercise_response.content, "html.parser")

    # Retrieve image URLs
    if "trapezius" in ansell_url:
        exercise_payload["title"] = "Trapezius Muscle Stretch"
        images = soup.find_all("img", attrs={"alt": "Trapezius muscle stretch"})
        srcset = images[1]["srcset"].split(", ")
        full_image_url = srcset[-1][:-6]
        exercise_payload["image1"] = full_image_url
        exercise_payload["video1"] = "https://youtu.be/rmk5RTu0eOg?t=91"
        steps_index = 1
    elif "levator" in ansell_url:
        exercise_payload["title"] = "Levator Scapulae Muscle Stretch"
        images = soup.find_all("img", attrs={"alt": "Levator Scapulae muscle stretch"})
        srcset = images[1]["srcset"].split(", ")
        full_image_url = srcset[-1][:-6]
        exercise_payload["image1"] = full_image_url
        exercise_payload["video1"] = "https://youtu.be/rmk5RTu0eOg?t=128"
        steps_index = 2
    elif "scm" in ansell_url:
        exercise_payload["title"] = "SCM Muscle Stretch"
        images = soup.find_all("img", attrs={"alt": "SCM muscle stretch"})
        srcset = images[1]["srcset"].split(", ")
        full_image_url = srcset[-1][:-6]
        exercise_payload["image1"] = full_image_url
        exercise_payload["video1"] = "https://youtu.be/rmk5RTu0eOg?t=158"
        steps_index = 3

    # Retrieve exercise instructions
    ul_steps = []
    li_steps = []
    step_num = 1
    exercise_steps = []
    steps = soup.find_all("div", attrs={"class": "et_pb_text_inner"})

    for ul in steps[1].find_all('ul'):
            ul_steps.append(ul)

    for li in ul_steps[steps_index].find_all('li'):
        li_steps.append(li)

    for exercise_step in li_steps:
        full_exercise_step = "{}.) {}".format(step_num, exercise_step.text)
        exercise_steps.append(full_exercise_step)
        exercise_steps.append("\n\r\n")
        step_num += 1

    exercise_steps.insert(0, "Steps: \n\r\n")
    del exercise_steps[-1]

    exercise_payload["steps"] = "".join(exercise_steps)
    exercise_payload["domain"] = "ansell"
    
    return exercise_payload
   