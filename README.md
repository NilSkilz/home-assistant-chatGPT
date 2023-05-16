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


From ChatGPT, make sure GPT-4 is selected, and in the plugin store click "Develop your own plugin"
Enter the url of your home assistant instance (i.e.  home-assistant.myhouse.com)
When prompted, enter your LLAT.
Ask it some questions!


## Current Limitations / TODO
The current Home Assistant REST API can not return a subset of entities. When returning all of them, this would overload ChatGPT. I therefore created an API endpoint to return just specific domains (lights, switches, sensors etc).
This endpoint is located at /api/chatgpt/states/{domain}

### Domains
The currently exposed domains are:
- Lights
- Switches
- Sensors
- Climate

### Capacity
The plugin can communicate with the /history API endpoint to get access to an entities history. However, it's limited in the amount of information it can digest. If there are lots of changes (like electricity monitoring) it cannot process all of the information. 

### Controling devices
They are currently read-only.
Using ChatGPT to control devices is possible, and POST requests will be implemented in future, but it is very slow at the moment, and so would not be used for real-time control.
