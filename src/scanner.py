import os\nfrom .api import RedAPI, OpsAPI\nfrom .filesystem import mkdir_p, list_files_of_extension, assert_path_exists\nfrom .progress import Progress\nfrom .torrent import generate_new_torrent_from_file\nfrom .parser import get_bencoded_data, calculate_infohash\nfrom .errors import (\n    TorrentDecodingError,\n    UnknownTrackerError,\n    TorrentNotFoundError,\n    TorrentAlreadyExistsError,\n    TorrentExistsInClientError,\n)\nfrom .injection import Injection\n\ndef scan_torrent_file(\n    source_torrent_path: str,\n    output_directory: str,\n    red_api: RedAPI,\n    ops_api: OpsAPI,\n    injector: Injection | None,\n) -> str:\n    """\n    Scans a single .torrent file and generates a new one using the tracker API.\n\n    Args:\n        `source_torrent_path` (`str`): The path to the .torrent file.\n        `output_directory` (`str`): The directory to save the new .torrent files.\n        `red_api` (`RedAPI`): The pre-configured RED tracker API.\n        `ops_api` (`OpsAPI`): The pre-configured OPS tracker API.\n        `injector` (`Injection`): The pre-configured torrent Injection object.\n\n    Returns:\n        str: The path to the new .torrent file.\n\n    Raises:\n        See `generate_new_torrent_from_file`.\n    """\n    source_torrent_path = assert_path_exists(source_torrent_path)\n    output_directory = mkdir_p(output_directory)\n\n    output_torrents = list_files_of_extension(output_directory, ".torrent")\n    output_infohashes = __collect_infohashes_from_files(output_torrents)\n\n    try:\n        new_tracker, new_torrent_filepath, _ = generate_new_torrent_from_file(\n            source_torrent_path,\n            output_directory,\n            red_api,\n            ops_api,\n            input_infohashes={},\n            output_infohashes=output_infohashes,\n        )\n\n        if injector:\n            injector.inject_torrent(\n                source_torrent_path,\n                new_torrent_filepath,\n                new_tracker.site_shortname(),\n            )\n\n        return new_torrent_filepath\n    except (\n        TorrentDecodingError,\n        UnknownTrackerError,\n        TorrentNotFoundError,\n        TorrentAlreadyExistsError,\n        TorrentExistsInClientError,\n    ) as e:\n        print(f"Error processing {source_torrent_path}: {e}")\n        raise\n\ndef scan_torrent_directory(\n    input_directory: str,\n    output_directory: str,\n    red_api: RedAPI,\n    ops_api: OpsAPI,\n    injector: Injection | None,\n) -> str:\n    """\n    Scans a directory for .torrent files and generates new ones using the tracker APIs.\n\n    Args:\n        `input_directory` (`str`): The directory containing the .torrent files.\n        `output_directory` (`str`): The directory to save the new .torrent files.\n        `red_api` (`RedAPI`): The pre-configured RED tracker API.\n        `ops_api` (`OpsAPI`): The pre-configured OPS tracker API.\n        `injector` (`Injection`): The pre-configured torrent Injection object.\n\n    Returns:\n        str: A report of the scan.\n\n    Raises:\n        `FileNotFoundError`: if the input directory does not exist.\n    """\n    input_directory = assert_path_exists(input_directory)\n    output_directory = mkdir_p(output_directory)\n\n    input_torrents = list_files_of_extension(input_directory, ".torrent")\n    output_torrents = list_files_of_extension(output_directory, ".torrent")\n    input_infohashes = __collect_infohashes_from_files(input_torrents)\n    output_infohashes = __collect_infohashes_from_files(output_torrents)\n\n    p = Progress(len(input_torrents))\n\n    for i, source_torrent_path in enumerate(input_torrents, 1):\n        basename = os.path.basename(source_torrent_path)\n        print(f"({i}/{p.total}) {basename}")\n\n        try:\n            new_tracker, new_torrent_filepath, was_previously_generated = generate_new_torrent_from_file(\n                source_torrent_path,\n                output_directory,\n                red_api,\n                ops_api,\n                input_infohashes,\n                output_infohashes,\n            )\n\n            if injector:\n                injector.inject_torrent(\n                    source_torrent_path,\n                    new_torrent_filepath,\n                    new_tracker.site_shortname(),\n                )\n\n            if was_previously_generated:\n                if injector:\n                    p.already_exists.print("Torrent was previously generated but was injected into your torrent client.")\n                else:\n                    p.already_exists.print("Torrent was previously generated.")\n            else:\n                p.generated.print(\n                    f"Found with source '{new_tracker.site_shortname()}' and generated as '{new_torrent_filepath}'."\n                )\n        except TorrentDecodingError as e:\n            p.error.print(str(e))\n            continue\n        except UnknownTrackerError as e:\n            p.skipped.print(str(e))\n            continue\n        except TorrentAlreadyExistsError as e:\n            p.already_exists.print(str(e))\n            continue\n        except TorrentExistsInClientError as e:\n            p.already_exists.print(str(e))\n            continue\n        except TorrentNotFoundError as e:\n            p.not_found.print(str(e))\n            continue\n        except Exception as e:\n            p.error.print(str(e))\n            continue\n\n    return p.report()\n\ndef __collect_infohashes_from_files(files: list[str]) -> dict:\n    infohash_dict = {}\n\n    for filepath in files:\n        try:\n            torrent_data = get_bencoded_data(filepath)\n\n            if torrent_data:\n                infohash = calculate_infohash(torrent_data)\n                infohash_dict[infohash] = filepath\n        except UnicodeDecodeError:\n            continue\n\n    return infohash_dict\n