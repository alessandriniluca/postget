# postget
## Intent
<u>**This package is intended EXCLUSIVELY for demonstrative purposes. The author has no responsibility about the use you will do and the consequences of it. Keep in mind that running this code is forbidden, is just a demonstration about how scraping works.**</u>

This package wants to retrieve images and video preview from tweets, without using APIs.

## Setup

### Chrome driver
Notice that this is **required** for this package to work. To install it, it is enough to install chromium.

In Arch Linux, to install it, it is enough to type in terminal:
```
sudo pacman -S chromium
```
Then, you need to put the path of the chromedriver as value `PATH` inside the file `./postget/Posts.py`. You can find its path in linux by typing in terminal:
```
which chromedriver
```

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
If the response is correct, then it is working.

## Usage

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

A couple of words on `since_id` and `max_id`: if one of them is not set, or set to the default value, also the other correctly set will be ignored. If correctly set, tweets with the id within `[since_id, max_id]` will be saved (extremes included).

**Utility methods**:
- Getters and setters, among which four important methods are:
    - `get_actual_images()` to return the list of the images' urls (operating mode 0)
    - `get_video_preview()` to return the list of the videos' previews (operating mode 0)
    - `get_tweets_data()` to return the dictionary of tweets (operating mode 1)
    - `get_discussions_links()` to return the discussion links returned
- `login()` to perform the login according to the values of `username` and `password`
- `search()` according to the value of `query` (it takes care of handling the operating mode)
- `clear_images()` to clear the list of the images' urls (operating mode 0)
- `clear_video_previews()` to clear the list of the video previews' urls (operating mode 0)
- `clear_tweets()` to clear the tweet dictionary (operating mode 1)
- `quit_browser()` to close the instance of the driver
- `print_results()` to print the results (it takes care of verifying the operating mode)

Please, change and access the parameters with getters and setters.

## Roadmap

- [ ] Support for custom time digitation (standard time plus or minus epsilon)
- [ ] Avoiding the search to crash when one div fails, just raise an exception
- [ ] Adding support for advanced search in the search bar
- [ ] Adding complete support for multiple searches without closing the browser