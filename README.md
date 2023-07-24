# PyGoogleVoice: A Python Library for Interacting with Google Voice

PyGoogleVoice is a powerful Python library that provides a Pythonic way to interact with Google Voice. It enables users to perform various tasks, including logging into a Google Voice account, checking for unread messages, reading the latest message, and sending messages.

## Dependencies

Before using PyGoogleVoice, you need to install the following dependencies:
- [Selenium](https://www.selenium.dev/): A web automation library used for browser interaction.
- [Undetected-chromedriver](https://pypi.org/project/undetected-chromedriver/): A library that provides an undetectable Chrome WebDriver for Selenium.
- [Webdriver-manager](https://pypi.org/project/webdriver-manager/): A library used to manage browser driver executables.
- [Google Chrome](https://www.google.com/chrome/): The Chrome browser is required for the library to function.

You can install the necessary Python dependencies using pip:

```bash
pip install selenium undetected-chromedriver webdriver-manager
```

Please ensure you have Google Chrome installed. If not, you can download it from the [Google website](https://chrome.google.com/).

## How to Use

Using PyGoogleVoice is straightforward. First, create a Google Voice session by providing your Google Voice email address and password:

```python
from pygooglevoice import GoogleVoice

emailAddress = "example@example.com"
password = "password"

GVSession = GoogleVoice(emailAddress, password)
```

Replace `"example@example.com"` and `"password"` with your actual Google Voice email and password.

Please note that during the login process, if you have 2-Factor Authentication enabled, you will receive a notification on your authentication device. You need to allow the login attempt for the script to work.

### Optional Parameters

PyGoogleVoice also offers some optional parameters to customize your session:
- `headless`: Set `headless=True` to run the browser in headless mode, making it invisible during operation.
- `saveChromeData`: Set `saveChromeData=False` if you don't want to save the Chrome profile data.
- `chromeDataPath`: Use `chromeDataPath` to specify a custom path for the Chrome profile.
- `browser`: Use `browser=browsers.chromium` to use Chromium instead of Google Chrome.

For example, to use Chromium instead of Google Chrome:

```python
from pygooglevoice import GoogleVoice, browsers

emailAddress = "example@example.com"
password = "password"

GVSession = GoogleVoice(emailAddress, password, browser=browsers.chromium)
```
### Checking for Unread Conversations

You can check for conversations with unread messages:

```python
unreadConversations = GVSession.check_for_unread_conversations()
```

This will return a list containing the conversationIDs of each conversation with unread messages.

### Sending a Message

To send a message, use the `send_message` method:

```python
GVSession.send_message(conversationID, 'Message')
```

You can also send a message with a photo:

```python
GVSession.send_message(conversationID, 'Message', photos=['path/to/photo.jpg'])
```

### Reading the Latest Message

To read the latest message in a conversation, use the `read_latest_message` method:

```python
message = GVSession.read_latest_message(conversationID)
```

### Accessing the WebDriver

The Selenium WebDriver used internally by PyGoogleVoice can be accessed directly using `GVSession.chrome`.

## To-Do

There are some improvements planned for PyGoogleVoice:
- Allow reading all unread messages instead of just the latest message.
- Publish PyGoogleVoice to PyPi for easier installation using pip.

With PyGoogleVoice, you can automate various tasks in Google Voice, making it a useful tool for managing your Google Voice account programmatically.
