import argparse
from .Posts import Posts

def parse_args():
    parser = argparse.ArgumentParser(description='My Python Package')
    parser.add_argument('--username', type=str, metavar='', help='Username that will be used to access the Twitter account')
    parser.add_argument('--password', type=str, metavar='', help='Password of the Username that will be used access the Twitter account')
    parser.add_argument('--wait_scroll_base', type=int, metavar='', default=15, help='Base time to wait between one scroll and the subsequent (expressed in number of seconds, default: 15)')
    parser.add_argument('--wait_scroll_epsilon', type=float, metavar='', default=5, help='Random time to wait between one scroll and the subsequent (expressed in number of seconds, default: 5)')
    parser.add_argument('--num_scrolls', type=int, metavar='', default=10, help='Number of scrolls to be performed, default: 10')
    parser.add_argument('--query', type=str, metavar='', help='Query to be searched on Twitter')
    parser.add_argument('--mode',type=int, metavar='', default=0, help='Mode of operation: 0 (default) to retrieve just images and video preview, 1 to retrieve also information about tweets')
    parser.add_argument('--since_id', type=int, metavar='', default = -1, help='id of the tweet to start the search from (default = -1 means not set. Notice that need to be defined also max_id)')
    parser.add_argument('--max_id', type=int, metavar='', default = -1, help='id of the tweet to end the search to (default = -1 means not set. Notice that need to be defined also since_id)')
    try:
        args = parser.parse_args()
        return args
    except argparse.ArgumentError:
        parser.print_help()
    exit()

def main():
    args = parse_args()

    # Initialization
    my_object = Posts(args.username, args.password, args.query, args.wait_scroll_base, args.wait_scroll_epsilon, args.num_scrolls, args.mode, args.since_id, args.max_id)

    # Run
    my_object.login()
    my_object.search()
    my_object.print_results()
    my_object.quit_browser()

if __name__ == '__main__':
    main()