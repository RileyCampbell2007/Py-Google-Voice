import os
import urllib.parse
from selenium import webdriver
from undetected_chromedriver.options import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.chrome.service import Service as ChromeService

class browsers:
    googleChrome = 'googleChrome'
    chromium = 'chromium'

class GoogleVoice:
    def __init__(self, email: str, password: str, saveChromeData: bool = True, chromeDataPath: str = 'google-chrome', headless: bool = True, browser = 'googleChrome'):
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

        if(browser == 'googleChrome'):
            service=ChromeService(ChromeDriverManager().install(), desired_capabilities={'unexpectedAlertBehaviour': 'ignore'})
        elif(browser == 'chromium'):
            service=ChromeService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install(), desired_capabilities={'unexpectedAlertBehaviour': 'ignore'})

        self.chrome = webdriver.Chrome(service=service, options=chrome_options)

        # Execute JavaScript to hide WebDriver properties
        self.chrome.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
                })
            """
        })

        # Open Google login page
        self.chrome.get('https://accounts.google.com/')

        # Check if already logged in
        if 'https://myaccount.google.com' in self.chrome.current_url:
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
                    
    def check_for_unread_conversations(self):
        GVSession = self.chrome
        if (not GVSession.current_url.startswith('https://voice.google.com/u/0/messages')):
            GVSession.get('https://voice.google.com/u/0/messages')
        conversationsBox = WebDriverWait(WebDriverWait(GVSession,120).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'md-virtual-repeat-container[gv-id="thread-list-container"]'))),120).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class="md-virtual-repeat-offsetter"]')))
        conversationList = conversationsBox.find_elements(By.CSS_SELECTOR, 'gv-text-thread-item[conversation="conversation"]')
        unreadConversations = []
        for conversation in conversationList:
            try:
                conversationElement = conversation.find_element(By.CSS_SELECTOR, 'gv-thread-item').find_element(By.CSS_SELECTOR, 'div')
            except:
                continue
            conversationText = conversationElement.get_attribute('aria-label')
            if (conversationText.startswith('Unread. ')):
                unreadConversations = [conversationElement.get_attribute('gv-thread-id')] + unreadConversations
        return unreadConversations

    def read_latest_message(self, conversationID):
        GVSession=self.chrome
        if (not GVSession.current_url.startswith('https://voice.google.com/u/0/messages')):
            GVSession.get(f'https://voice.google.com/u/0/messages?itemId={urllib.parse.quote(conversationID)}')
        else:
            try:
                GVSession.find_element(By.CSS_SELECTOR, f'div[gv-thread-id="{conversationID}"]').click()
            except:
                GVSession.get(f'https://voice.google.com/u/0/messages?itemId={urllib.parse.quote(conversationID)}')
        messageContainer = WebDriverWait(GVSession, 120).until(EC.presence_of_all_elements_located((By.CLASS_NAME,'incoming')))[-1]
        message = WebDriverWait(messageContainer, 120).until(EC.presence_of_element_located((By.TAG_NAME, 'gv-annotation'))).text
        return message

    def send_message(self, conversationID: str, message: str, photos: list = []):
        GVSession = self.chrome
        if (not GVSession.current_url.startswith('https://voice.google.com/u/0/messages')):
            GVSession.get(f'https://voice.google.com/u/0/messages?itemId={urllib.parse.quote(conversationID)}')
        else:
            try:
                GVSession.find_element(By.CSS_SELECTOR, f'div[gv-thread-id="{conversationID}"]').click()
            except:
                GVSession.get(f'https://voice.google.com/u/0/messages?itemId={urllib.parse.quote(conversationID)}')
        if(len(photos) > 0):
            WebDriverWait(GVSession, 120).until(EC.presence_of_element_located((By.ID, 'ib1')))
            GVSession.execute_script('document.getElementById("ib1").dispatchEvent(new MouseEvent("click", {view: window, bubbles: true, cancelable: true}));')
            WebDriverWait(GVSession, 120).until(EC.presence_of_element_located((By.CSS_SELECTOR,"iframe[allow=\"camera 'src' https://docs.google.com\"]")))
            GVSession.switch_to.frame(GVSession.find_element(By.CSS_SELECTOR,"iframe[allow=\"camera 'src' https://docs.google.com\"]"))
            WebDriverWait(GVSession, 120).until(EC.presence_of_element_located((By.ID, ':7')))
            GVSession.find_element(By.ID, ':7').click()
            WebDriverWait(GVSession, 120).until(EC.presence_of_element_located((By.CSS_SELECTOR,"input[accept='image/bmp,image/gif,image/jpeg,image/png,image/tiff']")))
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
        WebDriverWait(GVSession, 120).until(EC.presence_of_element_located((By.ID, 'input_0')))
        GVSession.execute_script(f'document.getElementById("input_0").value=`{message}`;')
        GVSession.find_element(By.ID, 'input_0').send_keys('a'+Keys.BACK_SPACE+Keys.ENTER)
