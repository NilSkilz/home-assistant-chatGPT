# home-assistant-chatGPT


## What it is
This integration works by exposing a new REST API on top of your Home Assistant instance.

ChatGPT plugins work by fetching a manifest file, which describes the details of the API that it can connect to, to get back certain information. This integration allows ChatGPT to get those files from your instance and communicate securely with Home Assistant.

## What's required
You will need: 
- Access to ChatGPT plugins (as of May 2023 this is only for "Plus" users who have joined the waiting list).
- Your Home Assistant instance accessable from the internet.
- A HA Long Lived Access token


## Installation

Copy folder into /config/custom_components

add 

```chat_gpt:``` 

to configuration.yml
