import time
import pandas as pd
import logging
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
import subprocess
import threading
import ip_info
class InstagramBot:
    def __init__(self, mobile_name, user_names, login_user_name, password, count, ip, proxy_enable, log_file_path=None):
        self.mobile_name = mobile_name
        self.driver = None
        self.user_names = user_names
        self.error_checker = False
        self.login_user_name = login_user_name
        self.password = password
        self.count = count
        self.ip = ip
        self.proxy_enable = proxy_enable
        self.emails=[]
        if log_file_path:
            self.logger = logging.getLogger(f'Bot{self.count}')
            self.setup_logger(log_file_path)
        else:
            self.logger = logging.getLogger(__name__)
            self.setup_logger('bot_logs.log')

    def setup_logger(self, log_file_path):
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            filename=log_file_path,
                            filemode='a')
        
    def launch_instagram(self):
        self.logger.info(f"Launching Instagram on device {self.mobile_name}")
        try:
            if self.proxy_enable==0:
                print("Without proxy running")
                capabilities = {
                'platformName': 'Android',
                'automationName': 'UiAutomator2',
                'deviceName': self.mobile_name,
                'udid': self.mobile_name,
                'appPackage': 'com.instagram.android',
                'appActivity': 'com.instagram.mainactivity.LauncherActivity',
                'noReset': True,
                'autoGrantPermissions': True
            }
             
            elif self.proxy_enable==1:
                proxy_host = self.ip
                proxy_http_port = ip_info.proxy_http_port
                proxy_socks5_port =ip_info.proxy_socks5_port
                username = ip_info.username
                password = ip_info.password

                # Define capabilities including proxy settings
                capabilities = {
                    'platformName': 'Android',
                    'automationName': 'UiAutomator2',
                    'deviceName': self.mobile_name,
                    'udid': self.mobile_name,
                    'appPackage': 'com.instagram.android',
                    'appActivity': 'com.instagram.mainactivity.LauncherActivity',
                    'noReset': True,
                    'autoGrantPermissions': True,
                    'proxy': {
                        'http': f'http://{username}:{password}@{proxy_host}:{proxy_http_port}',
                        'https': f'http://{username}:{password}@{proxy_host}:{proxy_http_port}',
                        'socks5': f'socks5://{username}:{password}@{proxy_host}:{proxy_socks5_port}',
                        'no_proxy': 'localhost,127.0.0.1',
                        'verify_ssl': False,
                    }
                }

            subprocess.Popen(f'cmd /c appium --address 127.0.0.1 --port {472+self.count} --log-level debug', shell=True)
            self.driver = webdriver.Remote(f"http://localhost:{472+self.count}/wd/hub", options=UiAutomator2Options().load_capabilities(capabilities))
            time.sleep(7)
        except Exception as e:
            self.logger.error(f"Error in launch_instagram: {str(e)}")

    def login(self):
        self.logger.info("Logging in...")
        try:
            user_name = self.driver.find_element(by=AppiumBy.XPATH, value='//android.widget.FrameLayout[@resource-id="com.instagram.android:id/layout_container_main"]/android.widget.FrameLayout/android.widget.FrameLayout[2]/android.widget.FrameLayout[1]/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[2]/android.view.ViewGroup/android.view.ViewGroup/android.widget.EditText')
            user_name.send_keys(self.login_user_name)
            time.sleep(4)

            password = self.driver.find_element(by=AppiumBy.XPATH, value='//android.widget.FrameLayout[@resource-id="com.instagram.android:id/layout_container_main"]/android.widget.FrameLayout/android.widget.FrameLayout[2]/android.widget.FrameLayout[1]/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[3]/android.view.ViewGroup/android.widget.EditText')
            password.send_keys(self.password)
            time.sleep(4)

            login_button = self.driver.find_element(by=AppiumBy.XPATH, value='//android.widget.Button[@content-desc="Log in"]/android.view.ViewGroup')
            login_button.click()
            time.sleep(5)
            self.driver.quit()
            time.sleep(5)
            self.launch_instagram()
            time.sleep(5)
        except Exception as e:
            self.logger.error("Error in login:", exc_info=True)

    def loop_user_names(self, user_name):
        self.logger.info(f"Searching for user: {user_name}")
        try:
            search = self.driver.find_element(by=AppiumBy.XPATH, value='//android.widget.EditText[@resource-id="com.instagram.android:id/action_bar_search_edit_text"]')
            search.send_keys(user_name)
            time.sleep(3)
            try:
                first_search_result = self.driver.find_element(by=AppiumBy.XPATH, value='(//android.widget.LinearLayout[@resource-id="com.instagram.android:id/row_search_user_info_container"])[1]/android.widget.LinearLayout')
                first_search_result.click()
                time.sleep(5)
                try:
                    email = self.driver.find_element(by=AppiumBy.XPATH, value='//android.widget.Button[@content-desc="Email"]')
                    email.click()
                    time.sleep(5)
                    email = self.driver.find_element(by=AppiumBy.XPATH, value='//android.widget.Button[contains(@content-desc, "@")]')
                    email_text = email.text
                    print(email_text)
                    self.emails.append(email_text)
                    time.sleep(3)
                    self.get_back()
                    time.sleep(2)
                except Exception as e:
                    self.logger.info(f"No email for this user{user_name}")
                    self.driver.back()
                    time.sleep(5)
            except Exception as e:
                self.logger.info(f"Username not found")
                self.driver.back() 
                time.sleep(5)
        except Exception as e:
            self.error_checker = True
            self.logger.error(f"Error in loop_user_names: {str(e)}")

    def search_username(self):
        self.logger.info("Searching for usernames...")
        try:
            search_button = self.driver.find_element(by=AppiumBy.XPATH, value='(//android.widget.ImageView[@resource-id="com.instagram.android:id/tab_icon"])[3]')
            search_button.click()
            time.sleep(4)

            search = self.driver.find_element(by=AppiumBy.XPATH, value='//android.widget.EditText[@resource-id="com.instagram.android:id/action_bar_search_edit_text"]')
            search.click()
            time.sleep(4)
            
            index = 0
            while index < len(self.user_names):
                if self.error_checker == True:
                    print("Error Checker is True")
                    self.loop_user_names(self.user_names[index])
                    del self.user_names[index]
                    return
                print(self.user_names[index])

                self.loop_user_names(self.user_names[index])
                del self.user_names[index]
        except Exception as e:
            self.error_checker = True
            self.logger.error(f"Error in search_username: {str(e)}")

    def get_back(self):
        try:
            self.driver.back()
            time.sleep(3)
            self.driver.back()
            time.sleep(3)
            self.driver.back()
            time.sleep(3)
        except Exception as e:
            self.logger.error(f"Error in Get_back from email: {str(e)}")

    def other_activities(self):
        self.logger.info("Starting other activities...")
        while True:
            try:
                self.launch_instagram()
                self.login()
                self.search_username()
                if self.error_checker:
                    self.error_checker = False
                    continue
                self.driver.quit()
                print(self.emails)
                return self.emails
                break
            except Exception as e:
                self.logger.error(f"Error in other_activities: {str(e)}")
                self.logger.info("Re-running bot...")
                self.driver.quit()
                time.sleep(5)
                continue




