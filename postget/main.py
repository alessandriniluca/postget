import argparse
from .Posts import Posts
from .exceptions.exceptions import *

def parse_args():
    parser = argparse.ArgumentParser(description='My Python Package')
    parser.add_argument('--username', type=str, metavar='', help='Username that will be used to access the Twitter account')
    parser.add_argument('--password', type=str, metavar='', help='Password of the Username that will be used access the Twitter account')
    parser.add_argument('--wait_scroll_base', type=int, metavar='', default=15, help='Base time to wait between one scroll and the subsequent (expressed in number of seconds, default: 15)')
    parser.add_argument('--wait_scroll_epsilon', type=float, metavar='', default=5, help='Random time to wait between one scroll and the subsequent (expressed in number of seconds, default: 5)')
    parser.add_argument('--num_scrolls', type=int, metavar='', default=10, help='Number of scrolls to be performed, default: 10')
    parser.add_argument('--query', type=str, metavar='', help='Query to be searched on Twitter')
    parser.add_argument('--email_address', type=str, metavar='', help='Email address of the account. Will be used in case twitter asks to enter the mail for confirmation purposes.')
    parser.add_argument('--mode',type=int, metavar='', default=0, help='Mode of operation: 0 (default) to retrieve just images and video preview, 1 to retrieve also information about tweets')
    parser.add_argument('--since_id', type=int, metavar='', default = -1, help='id of the tweet to start the search from (default = -1 means not set. Notice that need to be defined also max_id). If one between since or until is set, since_id and max_id will not be considered')
    parser.add_argument('--max_id', type=int, metavar='', default = -1, help='id of the tweet to end the search to (default = -1 means not set. Notice that need to be defined also since_id). If one between since or until is set, since_id and max_id will not be considered')
    parser.add_argument('--until', type=str, metavar='YYYY-MM-DD', default='none', help='String of the date (excluded) until which the tweets will be returned. Format: YYYY-MM-DD, UTC time. Temporarily supported only for mode 1. If you set also since_time, or until_time, this will be ignored')
    parser.add_argument('--since', type=str, metavar='YYYY-MM-DD', default='none', help='String of the date (included) from which the tweets will be returned. Format: YYYY-MM-DD, UTC time. Temporarily supported only for mode 1. If you set also since_time, or until_time, this will be ignored')
    parser.add_argument('--since_time', type=str, metavar='<timestamp>', default='none', help='String of the time from which the tweets will be returned. Format: timestamp in SECONDS, UTC time. Temporarily supported only for mode 1')
    parser.add_argument('--until_time', type=str, metavar='<timestamp>', default='none', help='String of the time until which the tweets will be returned. Format: timestamp in SECONDS, UTC time. Temporarily supported only for mode 1')
    parser.add_argument('--headless', action='store_true', help='Call with this to run the browser in headless mode')
    parser.add_argument('--chromedriver', type=str, metavar='/path/to/chromedriver', default='none', help='Path of the chromedriver. If not set, the package will try to automatically retrieve it.')
    parser.add_argument('--root', action='store_true', help='Call with this if you are running in root mode')
    try:
        args = parser.parse_args()
        return args
    except argparse.ArgumentError:
        parser.print_help()
    exit()

def main():
    args = parse_args()

    # Initialization
    if args.headless:
        if args.root:
            my_object = Posts(args.username, args.password, args.query, args.email_address, args.wait_scroll_base, args.wait_scroll_epsilon, args.num_scrolls, args.mode, args.since_id, args.max_id, args.since, args.until, args.since_time, args.until_time, headless=True, root = True)
        else:
            my_object = Posts(args.username, args.password, args.query, args.email_address, args.wait_scroll_base, args.wait_scroll_epsilon, args.num_scrolls, args.mode, args.since_id, args.max_id, args.since, args.until, args.since_time, args.until_time, headless=True)
    else:
        if args.root:
            my_object = Posts(args.username, args.password, args.query, args.email_address, args.wait_scroll_base, args.wait_scroll_epsilon, args.num_scrolls, args.mode, args.since_id, args.max_id, args.since, args.until, args.since_time, args.until_time, root=True)
        else:
            my_object = Posts(args.username, args.password, args.query, args.email_address, args.wait_scroll_base, args.wait_scroll_epsilon, args.num_scrolls, args.mode, args.since_id, args.max_id, args.since, args.until, args.since_time, args.until_time)
    # Run
    try:
        my_object.login()
    except ElementNotLoaded as e:
        print(e)
    try:
        my_object.search()
        my_object.print_results()
    except ElementNotLoaded as e:
        print(e)
    except NoTweetsReturned as e:
        print(e)
    my_object.quit_browser()

if __name__ == '__main__':
    main()