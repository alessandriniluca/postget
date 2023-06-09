# postget
## Intent
<u>**This package is intended EXCLUSIVELY for demonstrative purposes. The author has no responsibility about the use you will do and the consequences of it. Keep in mind that running this code is forbidden, is just a demonstration about how scraping works. If you decide to run it anyway, you will assume all the responsibilities about the consequence it will have.**</u>

This package wants to retrieve images and video preview from tweets, without using APIs.

## Setup

### Chrome driver
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

### Example
An example of command is (in the following a detailed explanation is provided):
```
postget --username '<your_username>' --password '<your_password>' --query '<query_to_be_performed>' --mail '<mail_of_the_account>' --num_scrolls 10  --wait_scroll_base 3 --wait_scroll_epsilon 1  --mode 1
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
- `headless` (`bool` if imported, just type `--headles` if called from command line): If specified, runs the browser in headless mode
- `chromedriver` (`str`): custom path to the chromedriver. if not specified, the code will try to find automatically the path of `chromedriver`
- `mail` (`str`): email of the account, required since sometimes could be asked to insert it to verify the account
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