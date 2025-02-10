import os
from colorama import Fore

from src.api import RedAPI, OpsAPI
from src.args import parse_args
from src.config import Config
from src.scanner import scan_torrent_directory, scan_torrent_file
from src.webserver import run_webserver


class CLIConfig:
    def __init__(self, config_file):
        self.config = Config().load(config_file)
        self.red_key = self.config.get('red_key', 'default_red_key')
        self.ops_key = self.config.get('ops_key', 'default_ops_key')
        self.input_directory = self.config.get('input_directory', '.')
        self.output_directory = self.config.get('output_directory', './output')
        self.port = int(os.environ.get("PORT", 9713))


def cli_entrypoint(args):
    try:
        cli_config = CLIConfig(args.config_file)
        red_api, ops_api = __verify_api_keys(cli_config)

        if args.server:
            run_webserver(cli_config.input_directory, cli_config.output_directory, red_api, ops_api, port=cli_config.port)
        elif args.input_file:
            print(scan_torrent_file(args.input_file, cli_config.output_directory, red_api, ops_api))
        elif args.input_directory:
            print(scan_torrent_directory(args.input_directory, cli_config.output_directory, red_api, ops_api))
    except KeyError as e:
        print(f"{Fore.RED}Missing configuration key: {str(e)}{Fore.RESET}")
        exit(1)
    except Exception as e:
        print(f"{Fore.RED}{str(e)}{Fore.RESET}")
        exit(1)


def __verify_api_keys(cli_config):
    red_api = RedAPI(cli_config.red_key)
    ops_api = OpsAPI(cli_config.ops_key)

    # This will perform a lookup with the API and raise if there was a failure.
    # Also caches the announce URL for future use which is a nice bonus
    red_api.announce_url
    ops_api.announce_url

    return red_api, ops_api


if __name__ == "__main__":
    args = parse_args()

    try:
        cli_entrypoint(args)
    except KeyboardInterrupt:
        print(f"{Fore.RED}Exiting...{Fore.RESET}")
        exit(1)