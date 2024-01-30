"""
A python library for interacting with Google Voice
"""

import os
import re
import urllib.parse
import requests
import time
import traceback
import threading
from requests import get
from selenium import webdriver
from undetected_chromedriver.options import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import NoSuchElementException

def element_exists(driver, by, value):
    try:
        driver.find_element(by, value)
        return True
    except NoSuchElementException:
        return False

class browsers:
    googleChrome = 0x0
    chromium = 0x1

class _message:
    """
    Helper class used internally by pygooglevoice
    """
    def __init__(self, messageText: str, messageSender: str, messageConversation: str, messageAttachments: list = []):
        self.text=messageText
        self.sender=messageSender
        self.conversation=messageConversation
        self.attachments=messageAttachments
        return

class GoogleVoice:

    lastMessageTime=time.time()

    usageLock = threading.Lock()

    def load_google_voice(self):
        self.chrome.get('https://voice.google.com/u/0/messages')
        while True:
            if not (self.chrome.execute_script("var items = document.querySelectorAll(`div.gvConversationList-item`); for (let i=0; i<items.length; i++) {if(items[i].querySelector('gv-text-thread-item') == null){return true;}}; return false;")):
                break

    def internet_check_thread(self):
        while True:
            try:
                get('https://8.8.8.8',timeout=.75)     
                time.sleep(0.5)  
            except:
                print('Internet is offline, pausing most actions!')
                self.usageLock.acquire()
                while True:
                    try:
                        if get('https://8.8.8.8').status_code == 200:
                            break
                    except:
                        time.sleep(1)
                self.load_google_voice()
                print('Internet is back online, re-enabling actions!')
                self.usageLock.release()

    def inactivity_reload_thread(self):
        while True:
            if time.time() > self.lastMessageTime + 1800:
                print('Google Voice has been inactive for 30 minutes, reloading.')
                self.usageLock.acquire()
                self.lastMessageTime=time.time()
                self.load_google_voice()
                self.usageLock.release()

    def __init__(self, email: str, password: str, saveChromeData: bool = True, chromeDataPath: str = 'google-chrome', headless: bool = True, browser = 0x0):
        """
        Logs into google voice using google email and password.

        Required Parameters:
        - `email`: Your Google Voice email address
        - `password`: Your Google Voice email address

        Optional Parameters:
        - `headless`: Set `headless=True` to run the browser in headless mode, making it invisible during operation.
        - `saveChromeData`: Set `saveChromeData=False` if you don't want to save the Chrome profile data.
        - `chromeDataPath`: Use `chromeDataPath` to specify a custom path for the Chrome profile.
        - `browser`: Use `browser=browsers.chromium` to use Chromium instead of Google Chrome.

        Returns a Google Voice session
        """

        self.lastMessageTime=time.time()

        threading.Thread(target=self.internet_check_thread).start()
        threading.Thread(target=self.inactivity_reload_thread).start()

        # Setting up Chrome options
        chrome_options = ChromeOptions()

        # Check if headless mode is enabled
        if headless:
            chrome_options.add_argument("--headless")

        # Check if saving data is enabled
        if saveChromeData:
            chrome_options.add_argument('--user-data-dir=' + chromeDataPath)

        # Additional Chrome options
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument('user-agent="Mozilla/5.0 (Windows NT 10.4;) AppleWebKit/535.17 (KHTML, like Gecko) Chrome/49.0.3318.292 Safari/600"')

        # Initializing Chrome WebDriver with options

        if(browser == 0x0):
            service=ChromeService(ChromeDriverManager().install(), desired_capabilities={'unexpectedAlertBehaviour': 'ignore'})
        elif(browser == 0x1):
            service=ChromeService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install(), desired_capabilities={'unexpectedAlertBehaviour': 'ignore'})

        self.chrome = webdriver.Chrome(service=service, options=chrome_options)

        # Execute JavaScript to hide WebDriver properties
        self.chrome.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
                });
            """
        })

        self.chrome.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": '''
                var zoomer = setInterval(() => {
                    console.log("page is fully loaded");
                    if(document.querySelector('div.gvMessagingView-loading') != null) {
                        document.querySelector('gv-conversation-list').style.zoom="0.00000001%";
                        clearInterval(zoomer);
                    };
               });
            '''
        })

        # Open Google login page
        self.chrome.get('https://accounts.google.com/')

        # Check if already logged in
        if 'https://myaccount.google.com' in self.chrome.current_url:
            self.load_google_voice()
            self.chrome.execute_script('let elem = document.createElement("div"); elem.id="phone-number"; elem.setAttribute("num", window._gv.soyProto["VoiceClientAccount"][0]); document.body.appendChild(elem)')
            self.GVNumber = self.chrome.find_element(By.ID, 'phone-number').get_attribute('num')
            return

        # Wait for email input field to be present
        emailBox = WebDriverWait(self.chrome, 120).until(EC.presence_of_element_located((By.ID, 'identifierId')))

        # Enter email character by character
        for i in range(len(email)):
            char = email[i]
            emailBox.send_keys(char)
        emailBox.send_keys(Keys.ENTER)
        
        # Wait for password input field to be present
        passwordBox = WebDriverWait(self.chrome, 120).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="Passwd"]')))

        # Enter password character by character
        for i in range(len(password)):
            char = password[i]
            passwordBox.send_keys(char)
        passwordBox.send_keys(Keys.ENTER)

        verificationNeeded = True
        while verificationNeeded:
            try:
                # Wait for 2-Step Verification page to appear
                WebDriverWait(self.chrome, 1).until(EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), '2-Step Verification'))
                verificationTextBox = self.chrome.find_element(By.CLASS_NAME, 'PrDSKc')
                verificationText = verificationTextBox.text.strip().replace('"', '').replace('<strong>', '').replace('</strong>', '')
                print(f'2-Step Verification Required. {verificationText}')

                verified = False
                while not verified:
                    try:
                        # Wait for 2-Step Verification to complete
                        WebDriverWait(self.chrome, 1).until(EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), '2-Step Verification'))
                    except TimeoutException:
                        print('Verified!')
                        verified = True
            except TimeoutException:
                # Check if redirected to account page after verification
                if self.chrome.current_url.startswith('https://myaccount.google.com/'):
                    verificationNeeded = False
        self.load_google_voice()
        self.chrome.execute_script('let elem = document.createElement("div"); elem.id="phone-number"; elem.setAttribute("num", window._gv.soyProto["VoiceClientAccount"][0]); document.body.appendChild(elem)')
        self.GVNumber = self.chrome.find_element(By.ID, 'phone-number').get_attribute('num')
        
                    
    def check_for_unread_conversations(self):
        """
        Will check Google Voice for all conversations that have unread messages.

        Returns a list with all the conversation IDs of conversations that contain unread messages

        Known Issue: If the client running pygooglevoice get's disconnected from the internet, it will no longer be able to check for unread conversations, even if the client reconnects.
        """
        with self.usageLock:
            retryCounter=0
            while retryCounter < 5:
                try:
                    GVSession = self.chrome
                    if (not GVSession.current_url.startswith('https://voice.google.com/u/0/messages')):
                        self.load_google_voice()
                    conversationsBox = self.chrome.find_element(By.CSS_SELECTOR, 'md-virtual-repeat-container[gv-id="thread-list-container"] div[class="md-virtual-repeat-offsetter"]')
                    conversationList = conversationsBox.find_elements(By.CSS_SELECTOR, 'gv-text-thread-item[conversation="conversation"] > gv-thread-item > div[aria-label^="Unread. "]')
                    unreadConversations = []
                    for conversation in conversationList:
                        unreadConversations = [conversation.get_attribute('gv-thread-id')] + unreadConversations
                    return unreadConversations
                except Exception as e:
                    retryCounter+=1
            raise Exception('Retry counter exceeded')

    def read_latest_message(self, conversationID: str):
        """
        Will grab the latest message in a conversation.

        Returns a message object
        """
        with self.usageLock:
            self.lastMessageTime=time.time()
            retryCounter=0
            while retryCounter < 5:
                try:
                    GVSession=self.chrome
                    if (not GVSession.current_url.startswith('https://voice.google.com/u/0/messages')):
                        self.load_google_voice()
                    #if(conversationID.startswith('g.Group')):
                    WebDriverWait(GVSession, 120).until(EC.presence_of_element_located((By.CSS_SELECTOR,'div[class="md-virtual-repeat-scroller"]')))
                    while True:
                        if not (GVSession.execute_script("var items = document.querySelectorAll(`div.gvConversationList-item`); for (let i=0; i<items.length; i++) {if(items[i].querySelector('gv-text-thread-item') == null){return true;}}; return false;")):
                            if (GVSession.execute_script('if(document.querySelector(`div[gv-thread-id="'+conversationID+'"]`) != null) {return true;} else {return false;}')):
                                GVSession.execute_script('document.querySelector(`div[gv-thread-id="'+conversationID+'"]`).click()')
                                break
                            else:
                                raise Exception('notfound')
                        else:
                            raise Exception('notfound')              
                    messageContainer = WebDriverWait(GVSession, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,'gv-text-message-item div.incoming')))[-1].find_element(By.XPATH,'..')
                    status = ('gv-text-message-item' not in messageContainer.get_attribute('outerHTML'))
                    while status:
                        messageContainer = messageContainer.find_element(By.XPATH,'..')
                        status = ('gv-text-message-item' not in messageContainer.get_attribute('outerHTML'))
                    try:
                        messageText = WebDriverWait(messageContainer, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'gv-annotation'))).get_attribute('innerHTML')
                    except:
                        messageText = ''
                    if ('t.' in conversationID):
                        sender=conversationID.replace('t.','')
                    else:
                        senderString=messageContainer.find_element(By.CLASS_NAME, 'sender').text.strip()
                        if(re.match(r'\(\d{3}\) \d{3}-\d{4}', senderString)):
                            sender='+1'+senderString.replace('(', '').replace(') ', '').replace('-', '')
                        else:
                            WebDriverWait(GVSession,120).until(EC.presence_of_element_located((By.CSS_SELECTOR,'md-menu-item[gv-test-id="pao"] button')))
                            GVSession.execute_script('document.querySelector(\'md-menu-item[gv-test-id="pao"] button\').click()')
                            WebDriverWait(GVSession,120).until(EC.presence_of_element_located((By.CSS_SELECTOR,'md-sidenav.md-sidenav-right.gvMessagingView-sidenav')))
                            chatParticipantsElement = GVSession.find_element(By.CSS_SELECTOR, 'md-sidenav.md-sidenav-right.gvMessagingView-sidenav')
                            for elem in chatParticipantsElement.find_elements(By.CSS_SELECTOR,'div[gv-test-id="people-item"]'):
                                name = elem.find_element(By.CSS_SELECTOR,'div[gv-test-id="people-phone-or-name"]').text.strip()
                                if name == senderString:
                                    sender = '+1'+elem.find_element(By.CSS_SELECTOR,'div[gv-test-id="people-phone-number"]').text.replace('(', '').replace(') ', '').replace('-', '').replace(' • mobile','').replace('‪','').strip()
                                    break
                    pattern = r'<img[^>]*alt="([^"]*)"[^>]*>'
                    messageText = re.sub(pattern, r'\1',messageText.strip())
                    pattern = r'''<a\s+(?:[^>]*?\s+)?href=["'](.*?)["'][^>]*>(.*?)<\/a>'''
                    messageText = re.sub(pattern, r'\1',messageText.strip())
                    messageAttachments = []
                    for item in messageContainer.find_elements(By.CSS_SELECTOR,'gv-image-attachment'):
                        attachmentUrl = item.find_element(By.CSS_SELECTOR,'img.image').get_attribute('src')
                        selenium_cookies = GVSession.get_cookies()
                        session = requests.Session()
                        for cookie in selenium_cookies:
                            session.cookies.set(cookie['name'], cookie['value'])
                        response = session.get(attachmentUrl)
                        messageAttachments.append(response.content)

                    return _message(messageText, sender, conversationID, messageAttachments=messageAttachments)
                except Exception as e:
                    if e == 'notfound':
                        raise Exception(f'Conversation with ID "{conversationID}" not found.')
                    retryCounter+=1
            raise Exception('Retry counter exceeded')

    def send_message(self, conversationID: str, message: str, photos: list = []):
        """
        Sends a message in a conversation.

        Required Parameters:
        - `conversationID`: The conversation to send the message in.
        - `message`: The content of the message you want to send.

        Optional Parameters:
        - `photos`: A list of the file paths of images to send along with the message.
        """
        with self.usageLock:
            self.lastMessageTime=time.time()
            retryCounter=0
            while retryCounter < 5:
                try:
                    GVSession = self.chrome
                    if (not GVSession.current_url.startswith('https://voice.google.com/u/0/messages')):
                        self.load_google_voice()
                    WebDriverWait(GVSession, 120).until(EC.presence_of_element_located((By.CSS_SELECTOR,'div[class="md-virtual-repeat-scroller"]')))
                    while True:
                        if not (GVSession.execute_script("var items = document.querySelectorAll(`div.gvConversationList-item`); for (let i=0; i<items.length; i++) {if(items[i].querySelector('gv-text-thread-item') == null){return true;}}; return false;")):
                            if (GVSession.execute_script('if(document.querySelector(`div[gv-thread-id="'+conversationID+'"]`) != null) {return true;} else {return false;}')):
                                GVSession.execute_script('document.querySelector(`div[gv-thread-id="'+conversationID+'"]`).click()')
                                break
                            else:
                                raise Exception('notfound')
                        else:
                            raise Exception('notfound')  
                    if(len(photos) > 0):
                        WebDriverWait(GVSession, 20).until(EC.presence_of_element_located((By.ID, 'ib1')))
                        GVSession.execute_script('document.getElementById("ib1").dispatchEvent(new MouseEvent("click", {view: window, bubbles: true, cancelable: true}));')
                        WebDriverWait(GVSession, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR,"iframe[allow=\"camera 'src' https://docs.google.com\"]")))
                        GVSession.switch_to.frame(GVSession.find_element(By.CSS_SELECTOR,"iframe[allow=\"camera 'src' https://docs.google.com\"]"))
                        WebDriverWait(GVSession, 20).until(EC.presence_of_element_located((By.ID, ':7')))
                        GVSession.find_element(By.ID, ':7').click()
                        WebDriverWait(GVSession, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR,"input[accept='image/bmp,image/gif,image/jpeg,image/png,image/tiff']")))
                        for file in photos:
                            GVSession.find_element(By.CSS_SELECTOR,"input[accept='image/bmp,image/gif,image/jpeg,image/png,image/tiff']").send_keys(os.path.abspath(file))
                        class aria_disabled_not_true(object):
                            def __init__(self, locator):
                                self.locator = locator

                            def __call__(self, GVSession):
                                element = GVSession.find_element(*self.locator)
                                if element.get_attribute("aria-disabled") != "true":
                                    return element
                                else:
                                    return False
                        WebDriverWait(GVSession, 300).until(aria_disabled_not_true((By.ID, "picker:ap:2")))
                        GVSession.find_element(By.ID,'picker:ap:2').click()
                        GVSession.switch_to.default_content()
                    WebDriverWait(GVSession, 20).until(EC.presence_of_element_located((By.ID, 'input_0')))
                    GVSession.execute_script(f'document.getElementById("input_0").value=`{message}`;')
                    GVSession.find_element(By.ID, 'input_0').send_keys('a'+Keys.BACK_SPACE+Keys.ENTER)
                    return
                except:
                    retryCounter+=1
            raise Exception('Retry counter exceeded')
