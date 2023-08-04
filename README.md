# postget
## Sections
- [Intent](#intent)
- [Setup](#setup)
    - [Chromedriver](#chromedriver)
    - [Virtual Environment](#virtual-environment)
- [Usage](#usage)
    - [Example - CLI](#example---cli)
    - [Example - Import in another project](#example---import-in-another-project)
    - [Operating Mode](#operating-mode)
    - [Command Line](#command-line)
    - [Import this in another project](#import-this-in-another-project)
- [Self management of exceptions](#self-management-of-exceptions)
- [Roadmap](#roadmap)
- [Changelog](#changelog)


## Intent
<u>**This package is intended EXCLUSIVELY for demonstrative purposes. The author has no responsibility about the use you will do and the consequences of it. Keep in mind that running this code is forbidden, is just a demonstration about how scraping works. If you decide to run it anyway, you will assume all the responsibilities about the consequence it will have.**</u>

This package wants to retrieve tweets text, images links and video preview links from tweets, without using APIs.

## Setup

### Chromedriver
Notice that this is **required** for this package to work. To install it, it is enough to install chromium and the chromedriver.

As an example, in Arch Linux, to install chromium, it is enough to type in terminal:
```
sudo pacman -S chromium
```
The path of `chromedriver` is found automatically. If your operating system for whatever reason gives it another name, pass it through the parameter `chromedriver`.

Tested on:
- [chromium](https://archlinux.org/packages/extra/x86_64/chromium/) (114.0.5735.45), **DARK THEME** (N.B.: the theme is important, since the loaded css will differ between light and dark. Future developments will add support for both)
- [chromedriver](https://aur.archlinux.org/packages/chromedriver) (same version of chromium)

### Virtual Environment
Creation of a virtual environment is **highly recommended**. In the home folder of a linux system:
```
python3 -m venv ./venv
```
Acrivate it:
```
source venv/bin/activate
```
Install the requirements of the package:
```
pip install -r requirements.txt
```
Install the package. It is **highly suggested** to install it in the editor mode, to allow changes without need of re-install it every time. Enter the path of the folder which contains this file, and type from the terminal:
```
pip install -e .
```
To test the installation, try to type (inside the virtual environment):
```
postget --help
```
If the response is correct and show the output of a help command, then it is working.

## Usage

### Example - CLI
An example of command is (in the following a detailed explanation is provided):
```
postget --username '<your_username>' --password '<your_password>' --query '<query_to_be_performed>' --email_address '<mail_of_the_account>' --num_scrolls 10  --wait_scroll_base 3 --wait_scroll_epsilon 1  --mode 1
```
### Example - Import in another project
As a reference for import (for parameters meaning see the [related section](#import-this-in-another-project)), after having installed it:
```
from postget.Posts import Posts
from postget.exceptions.exceptions import *

def main():
    twitter_getter = Posts(username='<USERNAME>', password='<PASSWORD>', email_address='<MAIL>', query='', num_scrolls=2, mode=1, wait_scroll_base = 4, wait_scroll_epsilon = 2)
    try:
        twitter_getter.login()
    except ElementNotLoaded as e:
        raise e


    print("Setting query in the object")
    twitter_getter.set_query('test')

    print("Start Search, this will input the query and perform the scroll with the selected mode")
    try:
	    twitter_getter.search()
    except ElementNotLoaded as e:
	    raise e
    except NoTweetsReturned as e:
	    print(e)
	
    print("Printing returned results and going home")
    twitter_getter.print_results()
    twitter_getter.go_home()
    print("Clearing Results")
    twitter_getter.clear_tweets()
    print("quitting browser")
    twitter_getter.quit_browser()

if __name__=='__main__':
    main()
```

### Operating mode

`postget` searches for images and tweet in two different ways:
- **Mode `0`**, or *simple search*: it just grep all links of images and videos detected when scrolling
- **Mode `1`**, or *complete search*: it greps also all information of tweet, such as id of the discussion and author. Notice that if you want to perform the search within two tweets' ids, it is necessary to operate in this mode.

Why keeping both? Because in mode `1` many things can go wrong, it is sufficient that one div search fails, that the entire search crashes. 

### Command Line
You can use this package from command line.

How it will be runned: `postget` will
- log in
- search for the query according to the operating mode
- perform scrolls
- print the images and video previews links or the tweets informations according to the operating mode
- close the driver

Notice that this means that a second call will imply a new login phase.

For information about the parameters, type in command line
```
postget --help
```

### Import this in another project
Import the class `Posts`. Main **parameters in the initialization**:
- `username` (`str`): Username that will be used to access the Twitter account
- `password` (`str`): Password of the Username that will be used access the Twitter account
- `query` (`str`): Query to be searched on Twitter
- `wait_scroll_base` (`int`): base time to wait between one scroll and the subsequent (expressed in number of seconds, default 15)
- `wait_scroll_epsilon` (`float`): random time to be added to the base time to wait between one scroll and the subsequent, in order to avoid being detected as a bot (expressed in number of seconds, default 5)
- `num_scrolls` (`int`): number of scrolls to be performed, default 10
- `since_id` (`int`): id from which tweets will be saved (tweets with an id `<` with respect than this value will be discarded). If set to `-1` (default value), this parameter will not be considered. Notice that this will be considered only if also `max_id` will be set, and will work only for search mode equal to `1`
- `max_id` (`int`): id until tweets will be saved (tweets with an id `>` with respect to this value, will be discarded). Notice that this will be considered only if also `max_id` will be set, and will work only for search mode equal to `1`
- `mode` (`int`): selects the operating mode, the default is `0`.
- `since` (`str`): String of the date (excluded) from which the tweets will be returned. Format: `YYYY-MM-DD`, UTC time. Temporarily supported only for mode `1`. If you set also since_time, or until_time, this will be ignored. Wrong formats will be ignored
- `until` (`str`): String of the date (included) until which the tweets will be returned. Format: `YYYY-MM-DD`, UTC time. Temporarily supported only for mode `1`. If you set also since_time, or until_time, this will be ignored. Wrong formats will be ignored
- `since_time` (`str`): String of the time from which the tweets will be returned. Format: timestamp in SECONDS, UTC time. Temporarily supported only for mode `1`
- `until_time` (`str`): String of the time until which the tweets will be returned. Format: timestamp in SECONDS, UTC time. Temporarily supported only for mode `1`
- `headless` **CURRENTLY NO MORE WORKING, use non headless mode** (`bool` if imported, just type `--headles` if called from command line): If specified, runs the browser in headless mode. Unfortunately something changed from the first version of postget, and this is no more working. A section in the roadmap has been added for this.
- `chromedriver` (`str`): custom path to the chromedriver. if not specified, the code will try to find automatically the path of `chromedriver`
- `email_address` (`str`): email of the account, required since sometimes could be asked to insert it to verify the account
- `root` (`bool` if imported, just type `--root` if called from command line): If specified, adds the option `--no-sandbox` to the chrome options, needed to be runned in root mode. Please notice that running in root mode is **not** safe for security reasons.

A couple of words on advenced filters:

- `since_id` and `max_id`: if one of them is not set, or set to the default value, also the other correctly set will be ignored. If correctly set, tweets with the id within `[since_id, max_id]` will be saved (extremes included).
- Precedences among `since_id`, `max_id`, `since`, `until`, `since_time`, `until_time`:
    - The definition of even just one parameter among `since`, or `until` causes the invalidation of `since_id` and `max_id` (they simply will not be considered).
    - The definition of even just one parameter among `since_time` or `until_time` causes the invalidation of `since` and `until` (they simply will not be considered). The same reasoning will be applied to `since_id` and `max_id` when one among `since_time` or `until_time` is defined.

**Utility methods**:
- Getters and setters, among which four important methods are:
    - `get_actual_images()` to return the list of the images' urls (operating mode 0)
    - `get_video_preview()` to return the list of the videos' previews (operating mode 0)
    - `get_tweets_data()` to return the dictionary of tweets (operating mode 1)
    - `get_discussions_links()` to return the discussion links returned
- `login()` to perform the login according to the values of `username` and `password`. **Raises**:
    - `ElementNotLoaded` exception when the username input is not loaded within timeout
    - `ElementNotLoaded` exception when the button to click to go to the password input is not loaded within timeout
    - `ElementNotLoeaded` exception when the password input is not loaded within timeout
    - `ElementNotLoaded` exception when the button to click to go to the home page is not loaded within timeout
- `search()` according to the value of `query` (it takes care of handling the operating mode). **Raises**:
    - `ElementNotLoaded` exception when the searchbox is not loaded in time, probably the page could be stuck in rendering and exceeded the timeout
    - `NoTweetsReturned` when the simplified search returns no tweets
    - `NoTweetsReturned` when the complete search returns no tweets.
- `go_home()` to go back to the homepage.
- `clear_images()` to clear the list of the images' urls (operating mode 0)
- `clear_video_previews()` to clear the list of the video previews' urls (operating mode 0)
- `clear_tweets()` to clear the tweet dictionary (operating mode 1)
- `quit_browser()` to close the instance of the driver
- `print_results()` to print the results (it takes care of verifying the operating mode)

Please, change and access the parameters with getters and setters.

## Self Management of Exceptions
- When the format of parameters `since` and `until` is not correct (i.e., is not `YYYY-MM-DD`), those parameters internally raises an exception, which will cause the reset to their default value (`none`) before proceding.

## Roadmap

- [ ] Support for custom digitation speed (standard time plus or minus epsilon)
- [ ] Support for both dark and light themes
- [ ] Re-implement headless feature

## Changelog
### 1.1.2
- Fixed naming inconsistency for the CLI interface. This did not cause any bug, but has been changed for code consistency
- Added support for tweet text retrieval