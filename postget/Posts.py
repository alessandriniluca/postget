from bs4 import BeautifulSoup
from selenium import webdriver
import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import re
import os
import shutil
import random
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from .exceptions.exceptions import WrongDateString, NoTweetsReturned, ElementNotLoaded

# Regex to match the image link
ACTUAL_IMAGE_PATTERN = '^https:\/\/pbs\.twimg\.com\/media.*'

# Regex to match date in 'until' and 'since' parameters. Notice that it does NOT check the validity of the date according to the month (e.g., one could declare) 2023-02-31.
DATE_SINCE_UNTIL = r'^(?!0000)[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$'

# Vertical size of the scroll. This is used to scroll down the page
Y = 500

# Regex to match the video preview link
ACTUAL_VIDEO_PREVIEW_PATTERN = '^https:\/\/pbs\.twimg\.com\/ext_tw_video_thumb.*'

# Target url to be scraped
TARGET_URL = 'https://www.twitter.com/login'

class Posts:
    def __init__(self, username: str, password: str, query: str, email_address: str, wait_scroll_base: int = 15, wait_scroll_epsilon :float = 5, num_scrolls: int = 10, mode: int = 0, since_id: int = -1, max_id: int = -1, since: str = 'none', until: str = 'none', since_time: str = 'none', until_time: str = 'none', headless: bool = False, chromedriver: str = 'none', root: bool=False):
        """Class initializator

        Args:
            username (str): Username that will be used to access the Twitter account
            password (str): Password of the Username that will be used access the Twitter account
            query (str): Query to be searched on Twitter
            email_address (str): Email address of the account. Will be used in case twitter asks to enter the mail for confirmation purposes.
            wait_scroll_base (int): base time to wait between one scroll and the subsequent (expressed in number of seconds, default 15)
            wait_scroll_epsilon (float): random time to be added to the base time to wait between one scroll and the subsequent, in order to avoid being detected as a bot (expressed in number of seconds, default 5)
            num_scrolls (int): number of scrolls to be performed, default 10
            mode (int): Mode of operation: 0 (default) to retrieve just images and video preview, 1 to retrieve also information about tweets
            since_id (int): id of the tweet to start the search from (default = -1 means not set. Notice that need to be defined also max_id). If one between since or until is set, since_id and max_id will not be considered
            max_id (int): id of the tweet to end the search to (default = -1 means not set. Notice that need to be defined also since_id). If one between since or until is set, since_id and max_id will not be considered
            since (str): String of the date (excluded) from which the tweets will be returned. Format: YYYY-MM-DD, UTC time. Temporarily supported only for mode 1. If you set also since_time, or until_time, this will be ignored
            until (str): String of the date (included) until which the tweets will be returned. Format: YYYY-MM-DD, UTC time. Temporarily supported only for mode 1. If you set also since_time, or until_time, this will be ignored
            since_time (str): String of the time from which the tweets will be returned. Format: timestamp in SECONDS, UTC time. Temporarily supported only for mode 1
            until_time (str): String of the time until which the tweets will be returned. Format: timestamp in SECONDS, UTC time. Temporarily supported only for mode 1
        """
        print("[postget]: You or your program started Postget, powered by")
        print("██╗░░░░░░█████╗░███╗░░██╗██████╗░░█████╗░███╗░░░███╗██╗██╗░░██╗")
        print("██║░░░░░██╔══██╗████╗░██║██╔══██╗██╔══██╗████╗░████║██║╚██╗██╔╝")
        print("██║░░░░░███████║██╔██╗██║██║░░██║██║░░██║██╔████╔██║██║░╚███╔╝░")
        print("██║░░░░░██╔══██║██║╚████║██║░░██║██║░░██║██║╚██╔╝██║██║░██╔██╗░")
        print("███████╗██║░░██║██║░╚███║██████╔╝╚█████╔╝██║░╚═╝░██║██║██╔╝╚██╗")
        print("╚══════╝╚═╝░░╚═╝╚═╝░░╚══╝╚═════╝░░╚════╝░╚═╝░░░░░╚═╝╚═╝╚═╝░░╚═╝")
        
        # Parameters initialization
        self.username = username
        self.password = password
        self.wait_scroll_base = wait_scroll_base
        self.wait_scroll_epsilon = wait_scroll_epsilon
        self.num_scrolls = num_scrolls
        self.query = query
        self.mode = mode
        self.since_id = since_id
        self.max_id = max_id
        self.until = until
        self.since = since
        self.since_time = since_time
        self.until_time = until_time
        self.email_address = email_address

        try:
            self.check_date()
        except WrongDateString as e:
            print(f'[postget]: {e}')
            print('           Ignoring since and until parameters since one among them was set wrong')
            self.since = 'none'
            self.until = 'none'
            print(f'           Setting them back to default values to ignore them: since = {self.since}, until = {self.until}')

        # Initialization of the lists of links and of tweets
        self.actual_images = []
        self.video_preview = []
        self.tweets = {}

        # Initialization of the chromedriver
        self.chrome_options = Options()
        self.chrome_options.add_experimental_option("detach", True)
        if headless:
            self.chrome_options.headless = True
            self.chrome_options.add_argument("--window-size=1920,1080")
            self.chrome_options.add_argument("--enable-javascript")
        if root:
            # If you try to run chromium as root, an error is shown displayng that reuquires --no-sandbox option to be set
            self.chrome_options.add_argument("--no-sandbox")
            print('[postget]: Running in root mode. This is not recommended for security reasons, disabling sandbox to allow run chromium.')
        if chromedriver != 'none':
            self.driver=webdriver.Chrome(chromedriver, chrome_options=self.chrome_options)
        else:
            self.driver=webdriver.Chrome(shutil.which('chromedriver'), chrome_options=self.chrome_options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 30)
        self.driver.get(TARGET_URL)

    ###### Utility methods ######
    def go_home(self):
        """Method used to go back to the homepage.
        """

        print('[postget]: Going to the homepage.')
        self.driver.get('https://twitter.com/home')
        print('[postget]: Returned to the homepage.')

    def login(self):
        """Method used to perform the login in the twitter account

        Raises:
            ElementNotLoaded: When the username input is not loaded within timeout
            ElementNotLoaded: When the button to click to go to the password input is not loaded within timeout
            ElementNotLoaded: When the password input is not loaded within timeout
            ElementNotLoaded: When the button to click to go to the home page is not loaded within timeout
        """

        print('[postget]: Logging in')
        # Input username
        try:
            username_input = self.wait.until(EC.visibility_of_element_located((By.NAME, "text")))
        except TimeoutException:
            raise ElementNotLoaded('Username input not loaded')
        
        time.sleep(0.7)
        for character in self.username:
            username_input.send_keys(character)
            time.sleep(0.3) # pause for 0.3 seconds
        # username_input.send_keys('send username here') -> can also be used, but hey ... my robot is a human
        try:
            button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[6]/div")))
        except TimeoutException:
            raise ElementNotLoaded('Button to be pressed after the username input not loaded')
        
        time.sleep(1)
        button.click()

        # Input password
        try:
            password_input = self.wait.until(EC.visibility_of_element_located((By.NAME, "password")))
        except TimeoutException:
            raise ElementNotLoaded('Password input not loaded')
        
        time.sleep(0.7)
        for character in self.password:
            password_input.send_keys(character)
            time.sleep(0.3) # pause for 0.3 seconds

        try:
            button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/div/div")))
        except TimeoutException:
            raise ElementNotLoaded('Button to be pressed after the password input not loaded')
        time.sleep(1)

        button.click()

        print('[postget]: Logged in successfully')

    def search(self):
        """Method used to search. It will take care of performing the search according to the mode and the parameters set

        Raises:
            ElementNotLoaded: when the searchbox is not loaded in time, probably the page could be stuck in rendering and exceeded the timeout
            NoTweetsReturned: when the simplified search returns no tweets
            NoTweetsReturned: when the complete search returns no tweets
        """

        # Query input
        print('[postget]: From now on, it may take a while, according to parameters.')
        try:
            searchbox = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@aria-label='Search query']")))
        except TimeoutException:

            # Could be that twitter is asking to enter the mail address:
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            if 'Verify your identity by entering the email address' in soup.get_text():

                print('[postget]: twitter is asking to verify the identity by entering the email address')
                try:
                    email_confirmation_input = self.wait.until(EC.visibility_of_element_located((By.NAME, "text")))
                except TimeoutException:
                    raise ElementNotLoaded('Email Confirmation input not loaded')
                print('[postget]: Email Confirmation input loaded, starting input email.')
                for character in self.email_address:
                    email_confirmation_input.send_keys(character)
                    time.sleep(0.3)
                try:
                    button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div/div/div/div")))
                except TimeoutException:
                    raise ElementNotLoaded('Trying to bypass email confirmation, but button \'next\' did not load')
                button.click()

                searchbox = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@aria-label='Search query']")))
            else:
                page_source = self.driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                filename = 'postget_error_soupfile.txt'
                cwd = os.getcwd()
                file_path = os.path.join(cwd, filename)

                with open(file_path, 'w') as f:
                    f.write(soup.prettify())
                raise ElementNotLoaded(f'Searchbox not loaded in time. Check {file_path} for more details.')
        # //TODO: clear query, the second query changes location to be opened

        time.sleep(0.7)
        searchbox.clear()

        self.input_query = self.query

        # Higher precedence: if one between since_time and until_time is set, since and until will be ignored. N.B.: it is correct to use always "since:" and "until:" in both cases!
        if self.since_time != 'none' or self.until_time != 'none':
            if self.since_time != 'none':
                self.input_query += f' since:{self.since_time}'
            if self.until_time != 'none':
                self.input_query += f' until:{self.until_time}'
        else:
            if self.since != 'none':
                self.input_query += f' since:{self.since}'
            if self.until != 'none':
                self.input_query += f' until:{self.until}'
        
        print(f'[postget]: Starting to input \'{self.input_query}\' in the searchbox')

        for character in self.input_query:
            searchbox.send_keys(character)
            time.sleep(0.3)
        
        searchbox.send_keys(Keys.ENTER)
        
        pause_time = self.compute_scroll_pause_time()
        print(f'[postget]: Search performed successfully, waiting first content to load. Waiting {pause_time} seconds')
        time.sleep(pause_time)
        
        if self.mode == 0:
            try:
                self.simplified_search()
            except NoTweetsReturned as e:
                raise e
        else:
            try:
                self.complete_search()
            except NoTweetsReturned as e:
                raise e

    def complete_search(self):
        """Method that performs the complete search

        Raises:
            NoTweetsReturned: raised when no tweets are returned by the search
        """

        print('[postget]: Starting complete search')
        count = 0
        destination = 0

        if self.since_id != -1 and self.max_id != -1:
            print(f'[postget]: since_id and max_id are set. since_id = {self.since_id}, max_id = {self.max_id}.')
        else:
            print(f'[postget]: since_id and max_id are not set. since_id = {self.since_id}, max_id = {self.max_id}.')
        
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        if len(soup.find_all('div', {'data-testid':'cellInnerDiv'})) == 0:
                raise NoTweetsReturned(self.input_query)

        while True:
            count += 1
            print(f'[postget]: Performing scroll {count} of {self.num_scrolls}')

            # Scroll down
            destination = destination + Y
            self.driver.execute_script(f"window.scrollTo(0, {destination})")

            # Wait for page to load
            pause_time = self.compute_scroll_pause_time()
            print(f'[postget]: Hey wait ... This content seams interesting, I\'ll wait {pause_time} seconds')
            time.sleep(pause_time)
            
            # Update page source
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            # find all tweets (div with data-testid="tweet")
            self.raw_tweets = soup.find_all('div', {'data-testid':'cellInnerDiv'})

            for raw_tweet in self.raw_tweets:
                # get the <a>...</a> tag containing the string about the id of the discussion (composed of: <username>/status/<id>)
                username_tweet_id = raw_tweet.find('a', {'class':"css-4rbku5 css-18t94o4 css-901oao r-1bwzh9t r-1loqt21 r-xoduu5 r-1q142lx r-1w6e6rj r-37j5jr r-a023e6 r-16dba41 r-9aw3ui r-rjixqe r-bcqeeo r-3s2u2q r-qvutc0"})
                
                # checking if it is an actual tweet, or an empty div at the end of the tweets

                if type(username_tweet_id) != type(None):
                    # checking if case since_id and max_id are set, it if not in the range [since_id, max_id]), and if advanced queries for times are not set, then we will search by ids.
                    if self.since_id != -1 and self.max_id != -1 and (self.since == 'none' and self.until == 'none') and (self.since_time == 'none' and self.until_time == 'none'):
                        
                        # If the tweet is in the range [since_id, max_id]
                        if int(username_tweet_id['href'].split('/')[3]) >= self.since_id and int(username_tweet_id['href'].split('/')[3]) <= self.max_id:
                            # using the discussion id as key of the dictionary, and checking if not already analyzed
                            if username_tweet_id['href'] not in self.tweets.keys():

                                # Retrieving username, tweet id, discussion link, and timestamp
                                iso_timestamp = username_tweet_id.find('time')['datetime']
                                dt = datetime.strptime(iso_timestamp,'%Y-%m-%dT%H:%M:%S.%fZ')
                                timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
                                discussion_link = f'https://twitter.com{username_tweet_id["href"]}'

                                # Retrieving tweet text
                                tweet_text = raw_tweet.find('div', {'data-testid': 'tweetText'})
                                # if tweet_text is not None. If tweet_text is None, output None
                                if tweet_text:
                                    tweet_text = tweet_text.get_text()

                                # append username, tweet id, tweet text, to the dictionary, and initializing the list of links to images and video preview
                                self.tweets[username_tweet_id['href']] = {"username": username_tweet_id['href'].split('/')[1], 
                                                                          "tweet_id": username_tweet_id['href'].split('/')[3], 
                                                                          "tweet_text": tweet_text, 
                                                                          "discussion_link": discussion_link, 
                                                                          "iso_8601_timestamp": iso_timestamp, 
                                                                          "datetime_timestamp": timestamp, 
                                                                          "images": [], 
                                                                          "video_preview": []}

                                # Retrieving images and video preview links
                                images = raw_tweet.find_all('img')
                                video_tags = raw_tweet.find_all('video')
                                for image in images:
                                    if re.match(ACTUAL_IMAGE_PATTERN, image['src']):
                                        self.tweets[username_tweet_id['href']]['images'].append(image['src'])
                                for video_tag in video_tags:
                                    if re.match(ACTUAL_VIDEO_PREVIEW_PATTERN, video_tag['poster']):
                                        self.tweets[username_tweet_id['href']]['video_preview'].append(video_tag['poster'])
                        else:
                            print(f'[postget]: Tweet {username_tweet_id["href"].split("/")[3]} not in the range [{self.since_id}, {self.max_id}]. Skipping it')
                    else:
                        # In this case, since_id and max_id are not set, so we can analyze all the tweets
                        # using the discussion id as key of the dictionary, and checking if not already analyzed
                        if username_tweet_id['href'] not in self.tweets.keys():
                            
                            # Retrieving username, tweet id, discussion link, and timestamp
                            iso_timestamp = username_tweet_id.find('time')['datetime']
                            dt = datetime.strptime(iso_timestamp,'%Y-%m-%dT%H:%M:%S.%fZ')
                            timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
                            discussion_link = f'https://twitter.com{username_tweet_id["href"]}'

                            # Retrieving tweet text
                            tweet_text = raw_tweet.find('div', {'data-testid': 'tweetText'})
                            # if tweet_text is not None. If tweet_text is None, output None
                            if tweet_text:
                                tweet_text = tweet_text.get_text()

                            # append username, tweet id, tweet text, to the dictionary, and initializing the list of links to images and video preview
                            self.tweets[username_tweet_id['href']] = {"username": username_tweet_id['href'].split('/')[1], 
                                                                      "tweet_id": username_tweet_id['href'].split('/')[3], 
                                                                      "tweet_text": tweet_text, 
                                                                      "discussion_link": discussion_link, 
                                                                      "iso_8601_timestamp": iso_timestamp, 
                                                                      "datetime_timestamp": timestamp, 
                                                                      "images": [], 
                                                                      "video_preview": []}

                            # Retrieving images and video preview links
                            images = raw_tweet.find_all('img')
                            video_tags = raw_tweet.find_all('video')
                            for image in images:
                                if re.match(ACTUAL_IMAGE_PATTERN, image['src']):
                                    self.tweets[username_tweet_id['href']]['images'].append(image['src'])
                            for video_tag in video_tags:
                                if re.match(ACTUAL_VIDEO_PREVIEW_PATTERN, video_tag['poster']):
                                    self.tweets[username_tweet_id['href']]['video_preview'].append(video_tag['poster'])
            if count == self.num_scrolls:
                break
           
            
    def simplified_search(self):
        """Method that performs the simplified search

        Raises:
            NoTweetsReturned: raised when no tweets are returned by the search
        """

        print('[postget]: Starting simplified search')

        if self.since_id != -1 or self.max_id != -1:
            print('[postget]: Simplified search does not support since_id and max_id parameters, since while browsing doesen\'t retrieve those information. Ignoring them.')

        count = 0
        destination = 0

        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        if len(soup.find_all('div', {'data-testid':'cellInnerDiv'})) == 0:
                raise NoTweetsReturned(self.input_query)

        while True:
            count += 1
            print(f'[postget]: Performing scroll {count} of {self.num_scrolls}')

            # Scroll down
            destination = destination + Y
            self.driver.execute_script(f"window.scrollTo(0, {destination})")

            # Wait to load page
            pause_time = self.compute_scroll_pause_time()
            print(f'[postget]: Hey wait ... This content seams interesting, I\'ll wait {pause_time} seconds')
            time.sleep(pause_time)
        
            # Update vectors
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            images = soup.find_all("img")
            video_tags = soup.findAll('video')

            for image in images:
                if re.match(ACTUAL_IMAGE_PATTERN, image['src']) and image['src'] not in self.actual_images:
                    self.actual_images.append(image['src'])

            for video_tag in video_tags:
                if re.match(ACTUAL_VIDEO_PREVIEW_PATTERN, video_tag['poster']) and video_tag['poster'] not in self.video_preview:
                    self.video_preview.append(video_tag['poster'])
            if count == self.num_scrolls:
                break

    def compute_scroll_pause_time(self):
        """Method used to compute the time to wait between one scroll and the subsequent

        Returns:
            int: time to wait between one scroll and the subsequent (expressed in number of seconds)
        """
        lower_bound = round(self.wait_scroll_base - self.wait_scroll_epsilon, 2)  # round to 2 decimal places
        upper_bound = round(self.wait_scroll_base + self.wait_scroll_epsilon, 2)  # round to 2 decimal places

        return round(random.uniform(lower_bound, upper_bound), 2)  # round to 2 decimal places
    
    def clear_images(self):
        """Method used to clear the images vector
        """
        self.actual_images = []

    def clear_video_previews(self):
        """Method used to clear the video preview vector
        """
        self.video_preview = []

    def clear_tweets(self):
        """Method used to clear the tweets dictionary
        """
        self.tweets = {}

    def quit_browser(self):
        """Method used to quit the browser
        """
        self.driver.quit()
    
    def print_results(self):
        """Prints the search according to the mode specified.
        """
        if self.mode == 0:
            print('[postget]: Hey hey ... here are the images:')
            for image in self.get_actual_images():
                print(f'           {image}')
            print('           and here the videos:')
            for video in self.get_video_preview():
                print(f'           {video}')
        else:
            print('[postget]: Hey hey ... here are the tweets:')
            for tweet in self.tweets:
                print(f'           {self.tweets[tweet]}')
    
    ###### Checks ######
    def check_date(self):
        """Checks if the date of advanced search parameters (since, until) is in the correct format

        Raises:
            WrongDateString: If the dates are in wrong format
        """
        if(self.since != 'none'):
            if not re.match(DATE_SINCE_UNTIL, self.since):
                raise WrongDateString(self.since, 'YYYY-MM-DD')
        if(self.until != 'none'):
            if not re.match(DATE_SINCE_UNTIL, self.until):
                raise WrongDateString(self.until, 'YYYY-MM-DD')
    
    ###### Formatters ######

    def get_discussions_links(self):
        """returns the links of the discussions returned

        Returns:
            list: strings of the discussion links
        """
        
        discussions_links = []

        for key in self.tweets.keys():
            discussions_links.append(f'https://twitter.com{key}')

        return discussions_links

    ###### Getter and setter methods ######

    def get_username(self):
        """Returns the username

        Returns:
            str: username
        """
        return self.username
    
    def set_username(self, username :str):
        """Sets the username

        Args:
            username (str): Username that will be used to access the Twitter account
        """
        self.username = username

    def get_password(self):
        """Returns the password

        Returns:
            str: password
        """
        return self.password
    
    def set_password(self, password :str):
        """Sets the password

        Args:
            password (str): Password of the Username that will be used access the Twitter account
        """
        self.password = password

    def get_wait_scroll_base(self):
        """Returns the base time to wait between one scroll and the subsequent (expressed in number of seconds)

        Returns:
            int: base time to wait between one scroll and the subsequent (expressed in number of seconds)
        """
        return self.wait_scroll_base
    
    def set_wait_scroll_base(self, wait_scroll_base :int):
        """Sets the base time to wait between one scroll and the subsequent (expressed in number of seconds)

        Args:
            wait_scroll_base (int): base time to wait between one scroll and the subsequent (expressed in number of seconds)
        """
        self.wait_scroll_base = wait_scroll_base

    def get_wait_scroll_epsilon(self):
        """Returns the random time to be added to the base time to wait between one scroll and the subsequent, in order to avoid being detected as a bot (expressed in number of seconds)

        Returns:
            float: random time to be added to the base time to wait between one scroll and the subsequent, in order to avoid being detected as a bot (expressed in number of seconds)
        """
        return self.wait_scroll_epsilon
    
    def set_wait_scroll_epsilon(self, wait_scroll_epsilon :float):
        """Sets the random time to be added to the base time to wait between one scroll and the subsequent, in order to avoid being detected as a bot (expressed in number of seconds)

        Args:
            wait_scroll_epsilon (float): random time to be added to the base time to wait between one scroll and the subsequent, in order to avoid being detected as a bot (expressed in number of seconds)
        """
        self.wait_scroll_epsilon = wait_scroll_epsilon

    def get_num_scrolls(self):
        """Returns the number of scrolls to be performed

        Returns:
            int: number of scrolls to be performed
        """
        return self.num_scrolls
    
    def set_num_scrolls(self, num_scrolls :int):
        """Sets the number of scrolls to be performed

        Args:
            num_scrolls (int): number of scrolls to be performed
        """
        self.num_scrolls = num_scrolls
    
    def get_actual_images(self):
        """get the actual images returned by the query

        Returns:
            list: list of actual images returned by the query
        """
        return self.actual_images
    
    def get_video_preview(self):
        """get the video preview returned by the query

        Returns:
            list: list of video preview returned by the query
        """
        return self.video_preview
    
    def get_query(self):
        """get the query being performed

        Returns:
            str: query
        """
        return self.query
    
    def set_query(self, query :str):
        """set the query to be performed
        """
        self.query = query
    
    def get_tweets_data(self):
        """get the tweets data returned by the complete search

        Returns:
            dict: dictionary of tweets returned by the query
        """
        return self.tweets
    
    def get_mode(self):
        """get the mode of the search

        Returns:
            int: mode of the search
        """
        return self.mode
    
    def set_mode(self, mode :int):
        """set the mode of the search

        Args:
            mode (int): mode of the search, can be either 0 (simple search with just images or video previews' links) or 1 (with complete information about tweets)
        """
        self.mode = mode
    
    def get_since_id(self):
        """get the since_id of the search

        Returns:
            int: since_id of the search
        """
        return self.since_id
    
    def set_since_id(self, since_id :int):
        """set the since_id of the search

        Args:
            since_id (int): since_id of the search
        """
        self.since_id = since_id
    
    def get_max_id(self):
        """get the max_id of the search

        Returns:
            int: max_id of the search
        """
        return self.max_id
    
    def set_max_id(self, max_id :int):
        """set the max_id of the search

        Args:
            max_id (int): max_id of the search
        """
        self.max_id = max_id
    
    def get_since(self):
        """get the since date of the search

        Returns:
            str: since date of the search
        """
        return self.since
    
    def set_since(self, since :str):
        """set the since date of the search

        Args:
            since (str): since date of the search
        """
        self.since = since
        try:
            self.check_date()
        except WrongDateString as e:
            print(f'[postget]: {e}')
            print('           Ignoring since and until parameters since one among them was set wrong')
            self.since = 'none'
            self.until = 'none'
            print(f'           Setting them back to default values to ignore them: since = {self.since}, until = {self.until}')
    
    def get_until(self):
        """get the until date of the search

        Returns:
            str: until date of the search
        """
        return self.until
    
    def set_until(self, until :str):
        """set the until date of the search

        Args:
            until (str): until date of the search
        """
        self.until = until
        try:
            self.check_date()
        except WrongDateString as e:
            print(f'[postget]: {e}')
            print('           Ignoring since and until parameters since one among them was set wrong')
            self.since = 'none'
            self.until = 'none'
            print(f'           Setting them back to default values to ignore them: since = {self.since}, until = {self.until}')
    
    def get_since_time(self):
        """get the since time of the search

        Returns:
            str: since time of the search
        """
        return self.since_time
    
    def set_since_time(self, since_time :str):
        """set the since time of the search

        Args:
            since_time (str): since time of the search
        """
        self.since_time = since_time
    
    def get_until_time(self):
        """get the until time of the search

        Returns:
            str: until time of the search
        """
        return self.until_time
    
    def set_until_time(self, until_time :str):
        """set the until time of the search

        Args:
            until_time (str): until time of the search
        """
        self.until_time = until_time

    ###### End of getter and setter methods ######
