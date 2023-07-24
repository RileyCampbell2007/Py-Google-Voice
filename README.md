# Py Google Voice

Py Google Voice is a Python library that allows users to interact with Google Voice in a Pythonic way. It provides features like logging into a Google Voice account, checking for unread messages, reading the latest message, and sending a message.

## Dependencies

* Selenium
* Undetected-chromedriver
* Webdriver-manager == 3.8.6
* Google Chrome

## Install dependencies

You can install the necessary python dependencies using pip:

```bash
pip install selenium undetected-chromedriver webdriver-manager
```

Google Chrome can be downloaded from the [Google website.](https://chrome.google.com/)

## How to use

Here is a short example script that demonstrates how to use Py Google Voice:

```python
import pygooglevoice as gv

# Replace with your Google Voice email and password
email = "youremail@gmail.com"
password = "yourpassword"

GVSession = gv.login(email, password)

# Fetch all unread conversations
unread_conversations = gv.check_for_unread_conversations(GVSession)

# Read the latest message in the first unread conversation
latest_message = gv.read_latest_message(GVSession, unread_conversations[0])

print("Latest message: ", latest_message)

# Send a new message to the same contact
gv.send_message(GVSession, unread_conversations[0], "This is a test reply from Py Google Voice.")
```

Please note that you would need to replace `"youremail@gmail.com"` and `"yourpassword"` with your actual Google Voice email and password in order for this script to work.

2-Factor Authentication is a required step during login, Google will send a notification to your authentication device, you will need to allow the login attempt in order to use this script.
