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

Google Chrome can be downloaded from the [Google website](https://chrome.google.com/).

## How to use

Creating the Google Voice session is done like this:

```python
from pygooglevoice import GoogleVoice

emailAddress = "example@example.com"
password = "password"

GVSession = GoogleVoice(emailAddress, password)
```

Please note that you would need to replace `"example@example.com"` and `"password"` with your actual Google Voice email and password in order for this script to work.

2-Factor Authentication is a required step during login, Google will send a notification to your authentication device, you will need to allow the login attempt in order to use this script.

If you want to run the browser in headless mode you can set `headless=True`.


If you don't want to save the Chrome Profile you can set `saveChromeData=False`.

If you want to change the Chrome Profile path you can set `chromeDataPath="path/to/profile"`.

If you want to use Chromium instead of Google Chrome you can do:

```python
from pygooglevoice import GoogleVoice, browsers

emailAddress = "example@example.com"
password = "password"

GVSession = GoogleVoice(emailAddress, password, browser=browsers.chromium)
```

Checking for conversations with unread messages is done like this:

```python
unreadConversations = GVSession.check_for_unread_conversations()
```

This will return a list with the conversationIDs of every conversation with unread messages.

To send a message do:

```python
GVSession.send_message(conversationID, 'Message')
```

Sending with a photo is done like this:

```python
GVSession.send_message(conversationID, 'Message', photos=['path/to/photo.jpg'])
```

Reading the latest message in a conversation can be done like this:

```python
message = GVSession.read_latest_message(conversationID)
```

The Selenium webdriver can be accesed directly with `GVSession.chrome`.

## To do

* Allow for reading all unread messages instead of the latest message.
* Add to PyPi so it can be installed via pip.

