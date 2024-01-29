# PyGoogleVoice: A Python Library for Interacting with Google Voice

PyGoogleVoice is a Python library that offers a Pythonic way to interact with Google Voice. It enables tasks such as logging into a Google Voice account, checking for unread messages, reading and sending messages, and handling attachments in conversations.

## Dependencies

To use PyGoogleVoice, the following dependencies must be installed:

- [Selenium](https://www.selenium.dev/)
- [Undetected-chromedriver](https://pypi.org/project/undetected-chromedriver/)
- [Webdriver-manager](https://pypi.org/project/webdriver-manager/)
- [Google Chrome](https://www.google.com/chrome/) or Chromium

Install the Python dependencies using pip:

```bash
pip install selenium undetected-chromedriver webdriver-manager
```

Ensure that Google Chrome or Chromium is installed. Download Chrome from the [Google website](https://chrome.google.com/).

## How to Use

Create a Google Voice session with your email and password:

```python
from pygooglevoice import GoogleVoice

emailAddress = "your_email@example.com"
password = "your_password"

GVSession = GoogleVoice(emailAddress, password)
```

Replace `"your_email@example.com"` and `"your_password"` with your Google Voice credentials.

Note: For 2-Factor Authentication, you will receive a prompt on your device. You need to authorize the login attempt.

### Optional Parameters

Customize your session with optional parameters:

- `headless`: Run browser in headless mode (`headless=True`).
- `saveChromeData`: Choose whether to save Chrome profile data (`saveChromeData=False` to not save).
- `chromeDataPath`: Specify custom path for Chrome profile data.
- `browser`: Choose between Google Chrome (`browser=browsers.googleChrome`) and Chromium (`browser=browsers.chromium`).

### Retrieving the Connected Phone Number

After initializing the GoogleVoice session, you can retrieve the phone number associated with your Google Voice account:

```python
phoneNumber = GVSession.GVNumber
print("Connected Phone Number:", phoneNumber)
```

This will display the phone number connected to your Google Voice account.

### Checking for Unread Conversations

Check for unread messages:

```python
unreadConversations = GVSession.check_for_unread_conversations()
```

This returns a list of conversation IDs with unread messages.

### Reading the Latest Message

The `read_latest_message` function returns a message object with the following attributes:

- `text`: The text content of the message.
- `sender`: The sender of the message. This could be a phone number or a contact name, depending on the information available.
- `conversation`: The ID of the conversation the message belongs to.
- `attachments`: A list of attachments in the message. Each attachment is represented as binary data.

Use the function like this:

```python
message = GVSession.read_latest_message(conversationID)
print("Message Text:", message.text)
print("Sender:", message.sender)
print("Attachments:", len(message.attachments))
```

### Sending a Message

Send a text or media message:

```python
# Text message
GVSession.send_message(conversationID, 'Your Message')

# Message with photo
GVSession.send_message(conversationID, 'Your Message', photos=['path/to/photo.jpg'])
```

### Internet Connectivity and Inactivity Management

The library includes features to handle internet connectivity issues and reload Google Voice after periods of inactivity. These features help maintain the session's stability and responsiveness.

## To-Do

Future improvements for PyGoogleVoice include:

- Reading all unread messages.
- Conversation management (create, delete, check existence).
- Message deletion.
- Support for calls.
