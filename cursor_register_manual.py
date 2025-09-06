import os
from colorama import Fore, Style, init
import time
import random
import re
import datetime
from faker import Faker
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from cursor_auth import CursorAuth
from reset_machine_manual import MachineIDResetter
from get_user_token import get_token_from_cookie
from config import get_config
from account_manager import AccountManager

os.environ["PYTHONVERBOSE"] = "0"
os.environ["PYINSTALLER_VERBOSE"] = "0"

# Initialize colorama
init()

# Define emoji constants
EMOJI = {
    'START': '🚀',
    'FORM': '📝',
    'VERIFY': '🔄',
    'PASSWORD': '🔑',
    'CODE': '📱',
    'DONE': '✨',
    'ERROR': '❌',
    'WAIT': '⏳',
    'SUCCESS': '✅',
    'MAIL': '📧',
    'KEY': '🔐',
    'UPDATE': '🔄',
    'INFO': 'ℹ️'
}

class CursorRegistration:
    def __init__(self, translator=None):
        self.translator = translator
        # Set to display mode
        os.environ['BROWSER_HEADLESS'] = 'False'
        self.browser = None
        self.controller = None
        self.sign_up_url = "https://authenticator.cursor.sh/sign-up"
        self.settings_url = "https://www.cursor.com/settings"
        self.email_address = None
        self.signup_tab = None
        self.email_tab = None
        self.temp_email_driver = None
        
        # initialize Faker instance
        self.faker = Faker()
        
        # generate account information
        self.password = self._generate_password()
        self.first_name = self.faker.first_name()
        self.last_name = self.faker.last_name()
        
        # modify the first letter of the first name(keep the original function)
        new_first_letter = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        self.first_name = new_first_letter + self.first_name[1:]
        
        print(f"\n{Fore.CYAN}{EMOJI['PASSWORD']} {self.translator.get('register.password')}: {self.password} {Style.RESET_ALL}")
        print(f"{Fore.CYAN}{EMOJI['FORM']} {self.translator.get('register.first_name')}: {self.first_name} {Style.RESET_ALL}")
        print(f"{Fore.CYAN}{EMOJI['FORM']} {self.translator.get('register.last_name')}: {self.last_name} {Style.RESET_ALL}")

    def _generate_password(self, length=12):
        """Generate password"""
        return self.faker.password(length=length, special_chars=True, digits=True, upper_case=True, lower_case=True)

    def setup_email(self):
        """Setup Email"""
        try:
            # Try to get a suggested email
            account_manager = AccountManager(self.translator)
            suggested_email = account_manager.suggest_email(self.first_name, self.last_name)
            
            if suggested_email:
                print(f"{Fore.CYAN}{EMOJI['START']} {self.translator.get('register.suggest_email', suggested_email=suggested_email) if self.translator else f'Suggested email: {suggested_email}'}")
                print(f"{Fore.CYAN}{EMOJI['START']} {self.translator.get('register.use_suggested_email_or_enter') if self.translator else 'Type "yes" to use this email or enter your own email:'}")
                user_input = input().strip()
                
                if user_input.lower() == 'yes' or user_input.lower() == 'y':
                    self.email_address = suggested_email
                else:
                    # User input is their own email address
                    email_address, temp_driver = self.create_temp_email()
                    if email_address:
                        self.email_address = email_address
                        # Store the temp email driver so we can keep it open
                        self.temp_email_driver = temp_driver
                    else:
                        print(f"{Fore.RED}{EMOJI['ERROR']} Failed to create temporary email{Style.RESET_ALL}")
                        return False
            else:
                # If there's no suggested email, create temporary email
                print(f"{Fore.CYAN}{EMOJI['START']} {self.translator.get('register.manual_email_input') if self.translator else 'Please enter your email address:'}")
                email_address, temp_driver = self.create_temp_email()
                if email_address:
                    self.email_address = email_address
                    # Store the temp email driver so we can keep it open
                    self.temp_email_driver = temp_driver
                else:
                    print(f"{Fore.RED}{EMOJI['ERROR']} Failed to create temporary email{Style.RESET_ALL}")
                    return False
            
            # Validate if the email is valid
            if '@' not in self.email_address:
                print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('register.invalid_email') if self.translator else 'Invalid email address'}{Style.RESET_ALL}")
                return False
                
            print(f"{Fore.CYAN}{EMOJI['MAIL']} {self.translator.get('register.email_address')}: {self.email_address}" + "\n" + f"{Style.RESET_ALL}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('register.email_setup_failed', error=str(e))}{Style.RESET_ALL}")
            return False

    
    def create_temp_email(self):
        """Create temporary email using imail.edu.vn service"""
        driver = None
        
        try:
            print(f"{Fore.CYAN}{EMOJI['START']} Creating temporary email...{Style.RESET_ALL}")
            
            # Configure Chrome for optimal performance
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-logging")
            chrome_options.add_argument("--disable-default-apps")
            chrome_options.add_argument("--disable-sync")
            chrome_options.add_argument("--disable-translate")
            chrome_options.add_argument("--hide-scrollbars")
            chrome_options.add_argument("--mute-audio")
            chrome_options.add_argument("--no-first-run")
            chrome_options.add_argument("--disable-infobars")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-popup-blocking")
            chrome_options.add_argument("--disable-prompt-on-repost")
            chrome_options.add_argument("--disable-hang-monitor")
            chrome_options.add_argument("--disable-client-side-phishing-detection")
            chrome_options.add_argument("--disable-component-update")
            chrome_options.add_argument("--disable-domain-reliability")
            chrome_options.add_argument("--disable-features=TranslateUI")
            chrome_options.add_argument("--disable-ipc-flooding-protection")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_experimental_option("prefs", {
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0,
                "profile.managed_default_content_settings.images": 2
            })
            
            print(f"{Fore.CYAN}{EMOJI['START']} Opening Chrome browser...{Style.RESET_ALL}")
            driver = webdriver.Chrome(options=chrome_options)
            # Hide webdriver detection
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Step 1: Navigate to imail.edu.vn
            print(f"{Fore.CYAN}{EMOJI['MAIL']} Navigating to imail.edu.vn...{Style.RESET_ALL}")
            driver.get("https://imail.edu.vn/")
            
            # Wait for page to load
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "input")))
            
            # Step 2: Create unique username with timestamp and random number (max 15 chars)
            base_username = f"{self.first_name}.{self.last_name}".lower()
            timestamp = datetime.datetime.now().strftime("%m%d%H%M")
            random_num = random.randint(10, 99)  # Reduced to 2 digits
            
            # Ensure total length doesn't exceed 15 characters
            full_username = f"{base_username}.{timestamp}{random_num}"
            if len(full_username) > 15:
                # Truncate base username if too long
                max_base_len = 15 - len(f".{timestamp}{random_num}")
                base_username = base_username[:max_base_len]
                username = f"{base_username}.{timestamp}{random_num}"
            else:
                username = full_username
                
            print(f"{Fore.CYAN}{EMOJI['FORM']} Filling username: {username} (length: {len(username)}){Style.RESET_ALL}")
            
            try:
                # Find visible username input (there are multiple inputs with same name)
                username_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[name="user"]')
                username_input = None
                
                # Find the visible one
                for input_elem in username_inputs:
                    if input_elem.is_displayed() and input_elem.is_enabled():
                        username_input = input_elem
                        break
                
                if not username_input:
                    print(f"{Fore.RED}{EMOJI['ERROR']} No visible username input found{Style.RESET_ALL}")
                    return None, None
                
                username_input.clear()
                username_input.send_keys(username)
                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Username filled successfully{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}{EMOJI['ERROR']} Error filling username: {e}{Style.RESET_ALL}")
                return None, None
            
            # Step 3: Select domain
            print(f"{Fore.CYAN}{EMOJI['FORM']} Selecting domain...{Style.RESET_ALL}")
            
            try:
                # Find visible domain dropdown (there are multiple inputs with same name)
                domain_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[name="domain"]')
                domain_dropdown = None
                
                # Find the visible one
                for input_elem in domain_inputs:
                    if input_elem.is_displayed() and input_elem.is_enabled():
                        domain_dropdown = input_elem
                        break
                
                if not domain_dropdown:
                    print(f"{Fore.RED}{EMOJI['ERROR']} No visible domain input found{Style.RESET_ALL}")
                    return None, None
                
                # Set domain using JavaScript (fastest method)
                driver.execute_script("arguments[0].value = 'apple.edu.pl';", domain_dropdown)
                driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", domain_dropdown)
                driver.execute_script("arguments[0].dispatchEvent(new Event('input'));", domain_dropdown)
                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Domain set to: apple.edu.pl{Style.RESET_ALL}")
                
            except Exception as e:
                print(f"{Fore.RED}{EMOJI['ERROR']} Error setting domain: {e}{Style.RESET_ALL}")
                return None, None
            
            # Wait for domain to be selected
            time.sleep(0.5)
            
            # Step 4: Click Create button
            print(f"{Fore.CYAN}{EMOJI['FORM']} Clicking Create button...{Style.RESET_ALL}")
            
            try:
                # Find visible Create button (there are multiple buttons)
                create_buttons = driver.find_elements(By.CSS_SELECTOR, 'input[value="Create"]')
                create_button = None
                
                # Find the visible one (usually the teal/green colored one)
                for button in create_buttons:
                    if button.is_displayed() and button.is_enabled():
                        # Check if it's the Create button by looking at the class or text
                        button_class = button.get_attribute("class")
                        if "teal" in button_class or "bg-teal" in button_class:
                            create_button = button
                            break
                
                if not create_button and create_buttons:
                    # Fallback: use the first visible submit button
                    for button in create_buttons:
                        if button.is_displayed() and button.is_enabled():
                            create_button = button
                            break
                
                if not create_button:
                    print(f"{Fore.RED}{EMOJI['ERROR']} No visible Create button found{Style.RESET_ALL}")
                    return None, None
                
                create_button.click()
                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Create button clicked{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}{EMOJI['ERROR']} Error clicking Create button: {e}{Style.RESET_ALL}")
                return None, None
            
            # Create email address with the unique username
            email_address = f"{username}@apple.edu.pl"
            
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Temporary email created: {email_address}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{EMOJI['INFO']} Browser will remain open for you to check emails{Style.RESET_ALL}")
            
            # Return both email address and driver to keep browser open
            return email_address, driver

        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} Error creating temporary email: {e}{Style.RESET_ALL}")
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            return None, None
        
        finally:
            # Note: We don't close the driver here as we want to keep the browser open
            # The caller should handle closing the browser when done
            pass

    def get_verification_code(self):
        """Get Verification Code from temporary email"""
        try:
            # If we have a temp email driver, try to get code automatically
            if hasattr(self, 'temp_email_driver') and self.temp_email_driver:
                print(f"{Fore.CYAN}{EMOJI['CODE']} {self.translator.get('register.auto_getting_code') if self.translator else 'Automatically getting verification code from email...'}{Style.RESET_ALL}")
                
                code = self._get_code_from_email()
                if code:
                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('register.code_found', code=code) if self.translator else f'Found verification code: {code}'}{Style.RESET_ALL}")
                    return code
                else:
                    print(f"{Fore.YELLOW}{EMOJI['WAIT']} {self.translator.get('register.code_not_found_manual') if self.translator else 'Could not find code automatically. Please enter manually:'}{Style.RESET_ALL}")
            
            # Fallback to manual input
            print(f"{Fore.CYAN}{EMOJI['CODE']} {self.translator.get('register.manual_code_input') if self.translator else 'Please enter the verification code:'}")
            code = input().strip()
            
            if not code.isdigit() or len(code) != 6:
                print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('register.invalid_code') if self.translator else 'Invalid verification code'}{Style.RESET_ALL}")
                return None
                
            return code
            
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('register.code_input_failed', error=str(e))}{Style.RESET_ALL}")
            return None

    def _get_code_from_email(self):
        """Get verification code from temporary email mailbox"""
        try:
            driver = self.temp_email_driver
            
            # Navigate to mailbox if not already there
            current_url = driver.current_url
            if "mailbox" not in current_url:
                print(f"{Fore.CYAN}{EMOJI['MAIL']} Navigating to mailbox...{Style.RESET_ALL}")
                driver.get("https://imail.edu.vn/mailbox")
                time.sleep(2)
            
            # Refresh mailbox to get latest emails
            print(f"{Fore.CYAN}{EMOJI['MAIL']} Refreshing mailbox...{Style.RESET_ALL}")
            try:
                # Try to find and click refresh button
                refresh_button = None
                try:
                    all_divs = driver.find_elements(By.XPATH, "//div[contains(@class, 'cursor-pointer')]")
                    for div in all_divs:
                        if "Refresh" in div.text:
                            refresh_button = div
                            break
                except:
                    pass
                
                if refresh_button:
                    refresh_button.click()
                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Refreshed mailbox{Style.RESET_ALL}")
                else:
                    driver.refresh()
                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Refreshed mailbox (F5){Style.RESET_ALL}")
                
                time.sleep(2)
            except Exception as e:
                print(f"{Fore.YELLOW}{EMOJI['WAIT']} Refresh failed, continuing...{Style.RESET_ALL}")
            
            # Look for Cursor verification email
            print(f"{Fore.CYAN}{EMOJI['MAIL']} Looking for Cursor verification email...{Style.RESET_ALL}")
            
            cursor_emails = []
            max_attempts = 10
            for attempt in range(max_attempts):
                print(f"{Fore.CYAN}{EMOJI['WAIT']} Attempt {attempt + 1}/{max_attempts}...{Style.RESET_ALL}")
                
                # Try different selectors to find Cursor email
                try:
                    # Look for email containing Cursor and verification
                    cursor_emails = driver.find_elements(By.XPATH, "//div[contains(@class, 'cursor-pointer') and contains(., 'Cursor') and contains(., 'Verify your email address')]")
                    
                    if not cursor_emails:
                        cursor_emails = driver.find_elements(By.XPATH, "//div[contains(@class, 'cursor-pointer') and contains(., 'Cursor') and contains(., 'cursor.sh')]")
                    
                    if not cursor_emails:
                        cursor_emails = driver.find_elements(By.XPATH, "//div[contains(@class, 'cursor-pointer') and contains(., 'Verify your email address')]")
                    
                    if not cursor_emails:
                        cursor_emails = driver.find_elements(By.XPATH, "//div[contains(@class, 'cursor-pointer') and contains(., 'no-reply@cursor.sh')]")
                    
                    if cursor_emails:
                        print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Found {len(cursor_emails)} Cursor email(s){Style.RESET_ALL}")
                        break
                    else:
                        print(f"{Fore.YELLOW}{EMOJI['WAIT']} No Cursor email found, waiting 3 seconds...{Style.RESET_ALL}")
                        time.sleep(3)
                        
                        # Refresh mailbox again
                        try:
                            driver.refresh()
                            time.sleep(2)
                        except:
                            pass
                            
                except Exception as e:
                    print(f"{Fore.YELLOW}{EMOJI['WAIT']} Error searching for emails: {e}{Style.RESET_ALL}")
                    time.sleep(3)
            
            if not cursor_emails:
                print(f"{Fore.RED}{EMOJI['ERROR']} No Cursor verification email found after {max_attempts} attempts{Style.RESET_ALL}")
                return None
            
            # Click on the first Cursor email
            print(f"{Fore.CYAN}{EMOJI['MAIL']} Opening Cursor email...{Style.RESET_ALL}")
            try:
                # Hide ads before clicking
                try:
                    driver.execute_script("document.querySelectorAll('iframe[id*=\"aswift\"]').forEach(iframe => iframe.style.display = 'none');")
                    driver.execute_script("document.querySelectorAll('ins.adsbygoogle').forEach(ad => ad.style.display = 'none');")
                except:
                    pass
                
                # Click on the email
                try:
                    driver.execute_script("arguments[0].click();", cursor_emails[0])
                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Clicked on Cursor email (JavaScript){Style.RESET_ALL}")
                except:
                    cursor_emails[0].click()
                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Clicked on Cursor email (Selenium){Style.RESET_ALL}")
                
                time.sleep(2)
            except Exception as e:
                print(f"{Fore.RED}{EMOJI['ERROR']} Error clicking on email: {e}{Style.RESET_ALL}")
                return None
            
            # Extract verification code from email content
            print(f"{Fore.CYAN}{EMOJI['CODE']} Extracting verification code...{Style.RESET_ALL}")
            
            try:
                # Get page text
                page_text = driver.find_element(By.TAG_NAME, "body").text
                
                # Look for verification code pattern
                code_match = re.search(r'Your verification code is (\d{6})', page_text, re.IGNORECASE)
                
                if code_match:
                    code = code_match.group(1)
                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Found verification code: {code}{Style.RESET_ALL}")
                    return code
                
                # Fallback: find all 6-digit numbers
                numbers = re.findall(r'\b\d{6}\b', page_text)
                if numbers:
                    # Usually the verification code is the second 6-digit number
                    code = numbers[1] if len(numbers) >= 2 else numbers[0]
                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Found verification code (fallback): {code}{Style.RESET_ALL}")
                    return code
                
                # Try to find in iframe
                try:
                    iframe = driver.find_element(By.CSS_SELECTOR, "iframe[srcdoc]")
                    if iframe:
                        srcdoc = iframe.get_attribute('srcdoc')
                        
                        code_match = re.search(r'Your verification code is (\d{6})', srcdoc, re.IGNORECASE)
                        if code_match:
                            code = code_match.group(1)
                            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Found verification code in iframe: {code}{Style.RESET_ALL}")
                            return code
                        
                        numbers = re.findall(r'\b\d{6}\b', srcdoc)
                        if numbers:
                            code = numbers[1] if len(numbers) >= 2 else numbers[0]
                            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Found verification code in iframe (fallback): {code}{Style.RESET_ALL}")
                            return code
                except Exception as e:
                    print(f"{Fore.YELLOW}{EMOJI['WAIT']} Could not check iframe: {e}{Style.RESET_ALL}")
                
                print(f"{Fore.RED}{EMOJI['ERROR']} Could not find verification code in email content{Style.RESET_ALL}")
                return None
                
            except Exception as e:
                print(f"{Fore.RED}{EMOJI['ERROR']} Error extracting code: {e}{Style.RESET_ALL}")
                return None
                
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} Error getting code from email: {e}{Style.RESET_ALL}")
            return None

    def register_cursor(self):
        """Register Cursor"""
        browser_tab = None
        try:
            print(f"{Fore.CYAN}{EMOJI['START']} {self.translator.get('register.register_start')}...{Style.RESET_ALL}")
            
            # Check if tempmail_plus is enabled
            config = get_config(self.translator)
            email_tab = None
            if config and config.has_section('TempMailPlus'):
                if config.getboolean('TempMailPlus', 'enabled'):
                    email = config.get('TempMailPlus', 'email')
                    epin = config.get('TempMailPlus', 'epin')
                    if email and epin:
                        from email_tabs.tempmail_plus_tab import TempMailPlusTab
                        email_tab = TempMailPlusTab(email, epin, self.translator)
                        print(f"{Fore.CYAN}{EMOJI['MAIL']} {self.translator.get('register.using_tempmail_plus')}{Style.RESET_ALL}")
            
            # Use new_signup.py directly for registration
            from new_signup import main as new_signup_main
            
            # Execute new registration process, passing translator
            result, browser_tab = new_signup_main(
                email=self.email_address,
                password=self.password,
                first_name=self.first_name,
                last_name=self.last_name,
                email_tab=email_tab,  # Pass email_tab if tempmail_plus is enabled
                controller=self,  # Pass self instead of self.controller
                translator=self.translator
            )
            
            if result:
                # Use the returned browser instance to get account information
                self.signup_tab = browser_tab  # Save browser instance
                success = self._get_account_info()
                
                # Close browser after getting information (but not temp email browser)
                if browser_tab and browser_tab != self.temp_email_driver:
                    try:
                        browser_tab.quit()
                        self.temp_email_driver.quit()
                    except:
                        pass
                
                return success
            
            return False
            
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('register.register_process_error', error=str(e))}{Style.RESET_ALL}")
            return False
        finally:
            # Ensure browser is closed in any case (but not temp email browser)
            if browser_tab and browser_tab != self.temp_email_driver:
                try:
                    browser_tab.quit()
                    self.temp_email_driver.quit()
                except:
                    pass
                
    def _get_account_info(self):
        """Get Account Information and Token"""
        try:
            self.signup_tab.get(self.settings_url)
            time.sleep(2)
            
            usage_selector = (
                "css:div.col-span-2 > div > div > div > div > "
                "div:nth-child(1) > div.flex.items-center.justify-between.gap-2 > "
                "span.font-mono.text-sm\\/\\[0\\.875rem\\]"
            )
            usage_ele = self.signup_tab.ele(usage_selector)
            total_usage = "未知"
            if usage_ele:
                total_usage = usage_ele.text.split("/")[-1].strip()

            print(f"Total Usage: {total_usage}\n")
            print(f"{Fore.CYAN}{EMOJI['WAIT']} {self.translator.get('register.get_token')}...{Style.RESET_ALL}")
            max_attempts = 30
            retry_interval = 2
            attempts = 0

            while attempts < max_attempts:
                try:
                    cookies = self.signup_tab.cookies()
                    for cookie in cookies:
                        if cookie.get("name") == "WorkosCursorSessionToken":
                            token = get_token_from_cookie(cookie["value"], self.translator)
                            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('register.token_success')}{Style.RESET_ALL}")
                            self._save_account_info(token, total_usage)
                            return True

                    attempts += 1
                    if attempts < max_attempts:
                        print(f"{Fore.YELLOW}{EMOJI['WAIT']} {self.translator.get('register.token_attempt', attempt=attempts, time=retry_interval)}{Style.RESET_ALL}")
                        time.sleep(retry_interval)
                    else:
                        print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('register.token_max_attempts', max=max_attempts)}{Style.RESET_ALL}")

                except Exception as e:
                    print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('register.token_failed', error=str(e))}{Style.RESET_ALL}")
                    attempts += 1
                    if attempts < max_attempts:
                        print(f"{Fore.YELLOW}{EMOJI['WAIT']} {self.translator.get('register.token_attempt', attempt=attempts, time=retry_interval)}{Style.RESET_ALL}")
                        time.sleep(retry_interval)

            return False

        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('register.account_error', error=str(e))}{Style.RESET_ALL}")
            return False

    def _save_account_info(self, token, total_usage):
        """Save Account Information to File"""
        try:
            # Update authentication information first
            print(f"{Fore.CYAN}{EMOJI['KEY']} {self.translator.get('register.update_cursor_auth_info')}...{Style.RESET_ALL}")
            if self.update_cursor_auth(email=self.email_address, access_token=token, refresh_token=token, auth_type="Auth_0"):
                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('register.cursor_auth_info_updated')}...{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('register.cursor_auth_info_update_failed')}...{Style.RESET_ALL}")

            # Reset machine ID
            print(f"{Fore.CYAN}{EMOJI['UPDATE']} {self.translator.get('register.reset_machine_id')}...{Style.RESET_ALL}")
            resetter = MachineIDResetter(self.translator)  # Create instance with translator
            if not resetter.reset_machine_ids():  # Call reset_machine_ids method directly
                raise Exception("Failed to reset machine ID")
            
            # Save account information to file using AccountManager
            account_manager = AccountManager(self.translator)
            if account_manager.save_account_info(self.email_address, self.password, token, total_usage):
                return True
            else:
                return False
            
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('register.save_account_info_failed', error=str(e))}{Style.RESET_ALL}")
            return False

    def start(self):
        """Start Registration Process"""
        try:
            if self.setup_email():
                if self.register_cursor():
                    print(f"\n{Fore.GREEN}{EMOJI['DONE']} {self.translator.get('register.cursor_registration_completed')}...{Style.RESET_ALL}")
                    return True
            return False
        finally:
            # Close email tab (but keep temp email browser open)
            if hasattr(self, 'temp_email') and not hasattr(self, 'temp_email_driver'):
                try:
                    self.temp_email.close()
                except:
                    pass

    def update_cursor_auth(self, email=None, access_token=None, refresh_token=None, auth_type="Auth_0"):
        """Convenient function to update Cursor authentication information"""
        auth_manager = CursorAuth(translator=self.translator)
        return auth_manager.update_auth(email, access_token, refresh_token, auth_type)

def main(translator=None):
    """Main function to be called from main.py"""
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{EMOJI['START']} {translator.get('register.title')}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

    registration = CursorRegistration(translator)
    registration.start()

    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    input(f"{EMOJI['INFO']} {translator.get('register.press_enter')}...")

if __name__ == "__main__":
    from main import translator as main_translator
    main(main_translator) 