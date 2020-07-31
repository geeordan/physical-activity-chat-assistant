# ![physical-activity-chat-assistant](/img/LogoBanner.png) 

## Short Description

PACA is a Slack application that uses IBM Watson Assistant to detect messages about body pain and then send a direct message to the pained user to provide them with recommended stretches and exercises. If a user is not available at the time to do the stretch or exercise, they can use PACA’s reminder feature to be reminded at a later time. The goal of this application is to ease remote workers’ body pain as they work from undisciplined work environments and encourage them to stretch or exercise more throughout the day. 
 
[![License](https://img.shields.io/badge/License-Apache2-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0) [![Slack](https://img.shields.io/badge/Join-Slack-blue)](https://join.slack.com/share/zt-g6v7kt4z-dMfVFDuP4En80VHH5UrTXQ)


## Contents
1. [Short Description](#short-description)
1. [PACA Story](#paca-story)
1. [The Architecture](#the-architecture)
1. [Long Description](#long-description)
1. [Project Roadmap](#project-roadmap)
1. [Getting Started](#getting-started)
1. [Live Demo](#live-demo)
1. [Built With](#built-with)
1. [Contributing](#contributing)
1. [Authors](#authors)
1. [License](#license)
1. [Acknowledgments](#acknowledgments)


## PACA Story

Watch the video below to understand PACA’s solution and how it can help remote workers like Marcus: 


[![PACA](http://img.youtube.com/vi/CHB8kZkMnWY/0.jpg)](https://www.youtube.com/watch?v=CHB8kZkMnWY "PACA")


## The Architecture
![Architecture path](img/PACA_Architecture.png)


## Long Description 
Due to the spread of COVID-19, many workers are practicing social distancing through working from home. As more workers spend longer hours on the computer, they tend to neglect their physical well-being. While working on the computer for extended periods of time, body pain and muscle aches may be noticed but are typically quickly ignored and dismissed. However, ignoring the pain and not addressing may only make it worse. Those working from home must be reminded and shown quick exercises and stretches for specific aching body parts throughout the workday to mitigate the adverse effects that could result from muscle stiffness and lack of mobility!

Companies and organizations have adopted Slack as their primary communication platform. PACA is a Slack application using Python programming language and IBM Watson Assistant to detect keywords in a conversation that relates to pain of a specific body part. During a conversation in a Slack channel, if a message contains words involving body part pain or potential sources of future muscle pain, PACA will directly message the user and provide recommended stretches and exercises.

PACA monitors and detects real-time Slack channel messages related to aching body parts. Although there are alternative health and wellness Slack applications and bots that remind you to take breaks, they lack the functionality to provide the user with actual actionable tasks that specifically target body pain. PACA will show exercises and stretches that can be accomplished quickly during the workday.

[More detail is available here](DESCRIPTION.md)


## Project Roadmap

![Roadmap](/img/PACA_Roadmap.png) 


## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

1. Create a [Slack app](https://api.slack.com/apps)
2. Add a new bot user to the Slack app
3. Replace the ```bot-oauth-token``` environmental variable in main.py with your Bot User OAuth Access Token
4. Add Bot Token Scopes to allow the app to read messages, send messages, view basic user information, etc.
5. Replace the ```DATABASE_URL``` environmental variable in main.py with your PostgreSQL database URL and credentials
6. Replace the ```watson_apikey``` environmental variable, session_url variable, and message_url variable in ```watson_api.py``` (IBM Watson assistant **must** be configured with Intents and Dialogs based on each body part specified in ```exercise_data.json```)
7. Start an Ngrok server on port 5000 (ex: ```./ngrok http 5000```) in the same directory as ```main.py``` and run ```main.py```
8. Using the public-facing URL provided by Ngrok, input the URL as a Request URL in the Interactivity & Shortcuts tab in your Slack app settings
9. In the Event Subscriptions tab, input the Ngrok URL followed by the endpoint ```/slack/events```
10. Invite your Slack bot to run in the background of your channels and to interact with users in your workspace!

Ngrok should only be used for development! When deploying the app, migrate the code base to a cloud platform (e.g. Heroku) to publicly host the API.


## Prerequisites

Before you begin, you’ll need the following: 

* A [Slack](https://slack.com/get-started#/) account. 
* An [IBM Cloud](https://cloud.ibm.com/registration) account. 
* Heroku 
* Flask


### Slack
* [Slack Event Adapter API](https://github.com/slackapi/python-slack-events-api)
* [Slackify](https://github.com/Ambro17/slackify)


## Live Demo

You can find PACA running at our live Slack server here: https://paca-bot.slack.com


## Built With

* [Python](https://www.python.org/) 
* [IBM Watson Assistant](https://www.ibm.com/cloud/watson-assistant/) 
* [Slack Events API](https://github.com/slackapi/python-slack-events-api)
* [Heroku](https://www.heroku.com) 
* [Heroku Postgres](https://www.heroku.com/postgres)
* [Flask](https://flask.palletsprojects.com/en/1.1.x/)
* [Ngrok](https://ngrok.com)


## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.


## Authors

* **Geordan Banks**
* **Marcus Chan**
* **Camille Kae Valerio**


## License 
This project is licensed under the Apache 2 License - see the [LICENSE](LICENSE) file for details.


## Acknowledgments

* [Ryan Engaling](https://www.instagram.com/love.ryanalexander) for his video production 
* Yu Chen & San Jose State University 
* Information and template from [Code and Response: Project Sample](https://github.com/Code-and-Response/Project-Sample) 

