# PACA
## Short Description

PACA is a Slack application that uses IBM Watson Assistant to detect messages about body pain and then send a direct message to the pained user to provide them with recommended stretches and exercises. If a user is not available at the time to do the stretch or exercise, they can use PACA’s reminder feature to be reminded at a later time. The goal of this application is to ease remote workers’ body pain as they work from undisciplined work environments and encourage them to stretch or exercise more throughout the day. 
 
[![License](https://img.shields.io/badge/License-Apache2-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0) [![Slack](https://img.shields.io/badge/Join-Slack-blue)][Slack in the #paca channel](https://join.slack.com/share/zt-g6v7kt4z-dMfVFDuP4En80VHH5UrTXQ).


## Contents
1. [Short description](#short-description)
1. [PACA Story](#paca-story)
1. [The architecture](#the-architecture)
1. [Long description](#long-description)
1. [Project roadmap](#project-roadmap)
1. [Getting started](#getting-started)
1. [Built with](#built-with)
1. [Contributing](#contributing)
1. [Versioning](#versioning)
1. [Authors](#authors)
1. [License](#license)
1. [Acknowledgments](#acknowledgments)


## PACA Story

Watch the video below to understand PACA’s solution and how it can help remote workers like Marcus: 

[![](http://img.youtube.com/vi/vOgCOoy_Bx0/0.jpg)](http://www.youtube.com/watch?v=vOgCOoy_Bx0)


Architecture
## The architecture



## Long description 
Real-world problem we identified
Due to the spread of COVID-19, many workers are practicing social distancing through working from home. As more workers are now on the computer for longer hours, they tend to neglect their physical well-being. Oftentimes while working on the computer, body pain is noticed but quickly ignored and dismissed. However, ignoring the pain and not addressing it will only make it worse. Those working from home need to be reminded and shown quick exercises and stretches for specific aching body parts throughout the workday!

The technology project we created
Companies and organizations have moved most of their work communications onto Slack. PACA is a Slack application using Python programming language and IBM Watson Assistant to detect keywords in a conversation that relates to pain of a specific body part. During a conversation in a Slack channel, if a message contains words involving body part pain, PACA will directly message the user and show recommended stretches and exercises.

Explain why it is better than any existing solution
PACA monitor and detect real-time Slack channel messages related to aching of a body part. There are other health and wellness Slack applications that remind you to take breaks, but they do not provide the user actual actionable tasks that specifically target body pain. PACA will show exercises and stretches that can be accomplished quickly during the workday.

[More detail is available here] [DESCRIPTION.md]


## Project roadmap

![Roadmap] [insert image here]


## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. Please see [SETUP.md]

SETUP.MD
#Getting the Solution Started

## Prerequisites

Before you begin, you’ll need the following: 

A [Slack] (https://slack.com/get-started#/) account. 
An [IBM Cloud] (https://cloud.ibm.com/registration) account. 
Heroku 
Flask


### Slack
1. Slack Event Adapter


## Built With

* [Python]
* [IBM Watson Assistant] 
* [Slack Events API]
* [Heroku] 
* [Heroku Postgres] 
* [Flask] 
* [Ngrok]


## Contributing

Please read CONTRIBUTING.md for details on our code of conduct, and the process for submitting pull requests to us.

CONTRIBUTING.md

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags).


##Authors

* **Geordan Banks**
* **Marcus Chan**
* **Camille Kae Valerio**


## License 
This project is licensed under the Apache 2 License - see the LICENSE file for details.


## Acknowledgements

* [Ryan Engaling] (insert website here) for his video production 
* Yu Chen & San Jose State University 

