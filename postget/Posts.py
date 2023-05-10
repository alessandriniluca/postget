from bs4 import BeautifulSoup
from selenium import webdriver
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import re
import random
from selenium.webdriver.chrome.options import Options

# Regex to match the image link
ACTUAL_IMAGE_PATTERN = '^https:\/\/pbs\.twimg\.com\/media.*'

# Path to the chromedriver
PATH = '/usr/bin/chromedriver'

# Vertical size of the scroll. This is used to scroll down the page
Y = 500

# Regex to match the video preview link
ACTUAL_VIDEO_PREVIEW_PATTERN = '^https:\/\/pbs\.twimg\.com\/ext_tw_video_thumb.*'

# Target url to be scraped
TARGET_URL = 'https://www.twitter.com/login'

class Posts:
    def __init__(self, username: str, password: str, query: str, wait_scroll_base: int = 15, wait_scroll_epsilon :float = 5, num_scrolls: int = 10, mode: int = 0, since_id: int = -1, max_id: int = -1):
        """Class initializator

        Args:
            username (str): Username that will be used to access the Twitter account
            password (str): Password of the Username that will be used access the Twitter account
            query (str): Query to be searched on Twitter
            wait_scroll_base (int): base time to wait between one scroll and the subsequent (expressed in number of seconds, default 15)
            wait_scroll_epsilon (float): random time to be added to the base time to wait between one scroll and the subsequent, in order to avoid being detected as a bot (expressed in number of seconds, default 5)
            num_scrolls (int): number of scrolls to be performed, default 10
            mode (int): Mode of operation: 0 (default) to retrieve just images and video preview, 1 to retrieve also information about tweets
            since_id (int): id of the tweet to start the search from (default = -1 means not set. Notice that need to be defined also max_id)
            max_id (int): id of the tweet to end the search to (default = -1 means not set. Notice that need to be defined also since_id)
        """
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

        # Initialization of the lists of links and of tweets
        self.actual_images = []
        self.video_preview = []
        self.tweets = {}

        # Initialization of the chromedriver
        self.chrome_options = Options()
        self.chrome_options.add_experimental_option("detach", True)
        self.driver=webdriver.Chrome(PATH, chrome_options=self.chrome_options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 30)
        self.driver.get(TARGET_URL)

    ###### Utility methods ######
    def login(self):
        """Method used to perform the login in the twitter account
        """

        print('[postget]: Logging in')
        # Input username
        username_input = self.wait.until(EC.visibility_of_element_located((By.NAME, "text")))
        time.sleep(0.7)
        for character in self.username:
            username_input.send_keys(character)
            time.sleep(0.3) # pause for 0.3 seconds
        # username_input.send_keys('send username here') -> can also be used, but hey ... my robot is a human

        button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[6]/div")))
        time.sleep(1)
        button.click()

        # Input password
        password_input = self.wait.until(EC.visibility_of_element_located((By.NAME, "password")))
        time.sleep(0.7)
        for character in self.password:
            password_input.send_keys(character)
            time.sleep(0.3) # pause for 0.3 seconds


        button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/div/div")))
        time.sleep(1)
        button.click()

        print('[postget]: Logged in successfully')

    def search(self):
        """Method used to search. It will take care of performing the search according to the mode
        """

        # Query input
        print('[postget]: From now on, it may take a while, according to parameters.')
        searchbox = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@aria-label='Search query']")))
        # //TODO: clear query, the second query changes location to be opened

        time.sleep(0.7)
        searchbox.clear()

        for character in self.query:
            searchbox.send_keys(character)
            time.sleep(0.3)
        
        searchbox.send_keys(Keys.ENTER)
        
        pause_time = self.compute_scroll_pause_time()
        print(f'[postget]: Search performed successfully, waiting first content to load. Waiting {pause_time} seconds')
        time.sleep(pause_time)
        
        if self.mode == 0:
            self.simplified_search()
        else:
            self.complete_search()

    def complete_search(self):
        """Method used to perform the complete search
        """

        print('[postget]: Starting complete search')
        count = 0
        destination = 0

        if self.since_id != -1 and self.max_id != -1:
            print(f'[postget]: since_id and max_id are set. since_id = {self.since_id}, max_id = {self.max_id}.')
        else:
            print(f'[postget]: since_id and max_id are not set. since_id = {self.since_id}, max_id = {self.max_id}.')

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
            time.sleep(3)

            # find all tweets (div with data-testid="tweet")
            self.raw_tweets = soup.find_all('div', {'data-testid':'cellInnerDiv'})

            for raw_tweet in self.raw_tweets:
                # get the <a>...</a> tag containing the string about the id of the discussion (composed of: <username>/status/<id>)
                username_tweet_id = raw_tweet.find('a', {'class':"css-4rbku5 css-18t94o4 css-901oao r-14j79pv r-1loqt21 r-xoduu5 r-1q142lx r-1w6e6rj r-37j5jr r-a023e6 r-16dba41 r-9aw3ui r-rjixqe r-bcqeeo r-3s2u2q r-qvutc0"})
                
                # checking if case since_id and max_id are set, it if not in the range [since_id, max_id])
                if self.since_id != -1 and self.max_id != -1:
                    
                    # If the tweet is in the range [since_id, max_id]
                    if int(username_tweet_id['href'].split('/')[3]) >= self.since_id and int(username_tweet_id['href'].split('/')[3]) <= self.max_id:
                        # using the discussion id as key of the dictionary, and checking if not already analyzed
                        if username_tweet_id['href'] not in self.tweets.keys():
                        
                            # append username, tweet id, to the dictionary, and initializing the list of links to images and video preview
                            self.tweets[username_tweet_id['href']] = {"username": username_tweet_id['href'].split('/')[1], "tweet_id": username_tweet_id['href'].split('/')[3], "images": [], "video_preview": []}

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
                        
                        # append username, tweet id, to the dictionary, and initializing the list of links to images and video preview
                        self.tweets[username_tweet_id['href']] = {"username": username_tweet_id['href'].split('/')[1], "tweet_id": username_tweet_id['href'].split('/')[3], "images": [], "video_preview": []}

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
        """Method that performs the simplified search.
        """

        print('[postget]: Starting simplified search')

        count = 0
        destination = 0

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

    ###### End of getter and setter methods ######