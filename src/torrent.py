import os\nimport copy\nfrom html import unescape\n\nfrom .api import RedAPI, OpsAPI\nfrom .trackers import RedTracker, OpsTracker\nfrom .errors import (\n    TorrentDecodingError,\n    UnknownTrackerError,\n    TorrentNotFoundError,\n    TorrentAlreadyExistsError,\n    TorrentExistsInClientError,\n)\nfrom .filesystem import replace_extension\nfrom .parser import (\n    get_bencoded_data,\n    get_origin_tracker,\n    recalculate_hash_for_new_source,\n    save_bencoded_data,\n)\n\ndef generate_new_torrent_from_file(\n    source_torrent_path: str,\n    output_directory: str,\n    red_api: RedAPI,\n    ops_api: OpsAPI,\n    input_infohashes: dict = {},\n    output_infohashes: dict = {},\n) -> tuple[OpsTracker | RedTracker, str, bool]:\n    """\n    Generates a new torrent file for the reciprocal tracker of the original torrent file if it exists on the reciprocal tracker.\n\n    Args:\n        source_torrent_path (str): The path to the original torrent file.\n        output_directory (str): The directory to save the new torrent file.\n        red_api (RedAPI): The pre-configured API object for RED.\n        ops_api (OpsAPI): The pre-configured API object for OPS.\n        input_infohashes (dict, optional): A dictionary of infohashes and their filenames from the input directory for caching purposes. Defaults to an empty dictionary.\n        output_infohashes (dict, optional): A dictionary of infohashes and their filenames from the output directory for caching purposes. Defaults to an empty dictionary.\n\n    Returns:\n        A tuple containing the new tracker class (RedTracker or OpsTracker), the path to the new torrent file, and a boolean\n        representing whether the torrent already existed (False: created just now, True: torrent file already existed).\n\n    Raises:\n        TorrentDecodingError: if the original torrent file could not be decoded.\n        UnknownTrackerError: if the original torrent file is not from OPS or RED.\n        TorrentNotFoundError: if the original torrent file could not be found on the reciprocal tracker.\n        TorrentAlreadyExistsError: if the new torrent file already exists in the input or output directory.\n        TorrentExistsInClientError: if the torrent already exists in the client.\n        Exception: if an unknown error occurs.\n    """\n    source_torrent_data, source_tracker = __get_bencoded_data_and_tracker(source_torrent_path)\n    new_torrent_data = copy.deepcopy(source_torrent_data)\n    new_tracker = source_tracker.reciprocal_tracker()\n    new_tracker_api = __get_reciprocal_tracker_api(new_tracker, red_api, ops_api)\n    stored_api_response = None\n\n    all_possible_hashes = __calculate_all_possible_hashes(source_torrent_data, new_tracker.source_flags_for_creation())\n    found_input_hash = __check_matching_hashes(all_possible_hashes, input_infohashes)\n    found_output_hash = __check_matching_hashes(all_possible_hashes, output_infohashes)\n\n    if found_input_hash:\n        raise TorrentAlreadyExistsError(\n            f"Torrent already exists in input directory at {input_infohashes[found_input_hash]}"\n        )\n    if found_output_hash:\n        return (new_tracker, output_infohashes[found_output_hash], True)\n\n    for new_source in new_tracker.source_flags_for_creation():\n        new_hash = recalculate_hash_for_new_source(source_torrent_data, new_source)\n        stored_api_response = new_tracker_api.find_torrent(new_hash)\n\n        if stored_api_response["status"] == "success":\n            new_torrent_filepath = __generate_torrent_output_filepath(\n                stored_api_response,\n                new_tracker,\n                new_source.decode("utf-8"),\n                output_directory,\n            )\n\n            if os.path.exists(new_torrent_filepath):\n                return (new_tracker, new_torrent_filepath, True)\n\n            if new_torrent_filepath:\n                torrent_id = __get_torrent_id(stored_api_response)\n\n                new_torrent_data[b"info"][b"source"] = new_source  # This is already bytes rather than str\n                new_torrent_data[b"announce"] = new_tracker_api.announce_url.encode()\n                new_torrent_data[b"comment"] = __generate_torrent_url(new_tracker_api.site_url, torrent_id).encode()\n                save_bencoded_data(new_torrent_filepath, new_torrent_data)\n\n                return (new_tracker, new_torrent_filepath, False)\n\n    if stored_api_response["error"] in ("bad hash parameter", "bad parameters"):\n        raise TorrentNotFoundError(f"Torrent could not be found on {new_tracker.site_shortname()}")\n\n    raise Exception(f"An unknown error occurred in the API response from {new_tracker.site_shortname()}")\n\ndef __calculate_all_possible_hashes(source_torrent_data: dict, sources: list[str]) -> list[str]:\n    return [recalculate_hash_for_new_source(source_torrent_data, source) for source in sources]\n\ndef __check_matching_hashes(all_possible_hashes: list[str], infohashes: dict) -> str:\n    for hash in all_possible_hashes:\n        if hash in infohashes:\n            return hash\n\n    return None\n\ndef __generate_torrent_output_filepath(\n    api_response: dict,\n    new_tracker: OpsTracker | RedTracker,\n    new_source: str,\n    output_directory: str,\n) -> str:\n    tracker_name = new_tracker.site_shortname()\n    source_name = f" [{new_source}]" if new_source else ""\n\n    filepath_from_api_response = unescape(api_response["response"]["torrent"]["filePath"])\n    filename = f"{filepath_from_api_response}{source_name}.torrent"\n    torrent_filepath = os.path.join(output_directory, tracker_name, filename)\n\n    return torrent_filepath\n\ndef __get_torrent_id(api_response: dict) -> str:\n    return api_response["response"]["torrent"]["id"]\n\ndef __generate_torrent_url(site_url: str, torrent_id: str) -> str:\n    return f"{site_url}/torrents.php?torrentid={torrent_id}"\n\ndef __get_bencoded_data_and_tracker(torrent_path):\n    # The fastresume stuff is to support qBittorrent since it doesn't store\n    # announce URLs in the torrent file IFF we're taking the file from `BT_backup`.\n    #\n    # qbit stores that information in a sidecar file that has the exact same name\n    # as the torrent file but with a `.fastresume` extension instead. It's also stored\n    # in a list of lists called `trackers` in this `.fastresume` file instead of `announce`.\n    fastresume_path = replace_extension(torrent_path, ".fastresume")\n    source_torrent_data = get_bencoded_data(torrent_path)\n    fastresume_data = get_bencoded_data(fastresume_path)\n\n    if not source_torrent_data:\n        raise TorrentDecodingError("Error decoding torrent file")\n\n    torrent_tracker = get_origin_tracker(source_torrent_data)\n    fastresume_tracker = get_origin_tracker(fastresume_data) if fastresume_data else None\n    source_tracker = torrent_tracker or fastresume_tracker\n\n    if not source_tracker:\n        raise UnknownTrackerError("Torrent not from OPS or RED based on source or announce URL")\n\n    return source_torrent_data, source_tracker\n\ndef __get_reciprocal_tracker_api(new_tracker, red_api, ops_api):\n    return red_api if new_tracker == RedTracker else ops_api\n