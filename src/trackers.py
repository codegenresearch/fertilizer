class Tracker:
  @staticmethod
  def source_flags_for_search():
    raise NotImplementedError

  @staticmethod
  def source_flags_for_creation():
    raise NotImplementedError

  @staticmethod
  def announce_url():
    raise NotImplementedError

  @staticmethod
  def site_shortname():
    raise NotImplementedError

  @staticmethod
  def reciprocal_tracker():
    raise NotImplementedError

  @staticmethod
  def handle_alternate_sources():
    raise NotImplementedError

  @staticmethod
  def manage_blank_sources():
    raise NotImplementedError


class OpsTracker(Tracker):
  @staticmethod
  def source_flags_for_search():
    return [b"OPS"]

  @staticmethod
  def source_flags_for_creation():
    return [b"OPS", b"APL", b""]

  @staticmethod
  def announce_url():
    return b"home.opsfet.ch"

  @staticmethod
  def site_shortname():
    return "OPS"

  @staticmethod
  def reciprocal_tracker():
    return RedTracker

  @staticmethod
  def handle_alternate_sources(torrent):
    # Example implementation: handle alternate sources for OPS
    pass

  @staticmethod
  def manage_blank_sources(output_path):
    # Example implementation: manage blank sources in output file paths for OPS
    if output_path.endswith('/'):
        return output_path + 'default_filename'
    return output_path


class RedTracker(Tracker):
  @staticmethod
  def source_flags_for_search():
    return [b"RED", b"PTH"]

  @staticmethod
  def source_flags_for_creation():
    return [b"RED", b"PTH", b""]

  @staticmethod
  def announce_url():
    return b"flacsfor.me"

  @staticmethod
  def site_shortname():
    return "RED"

  @staticmethod
  def reciprocal_tracker():
    return OpsTracker

  @staticmethod
  def handle_alternate_sources(torrent):
    # Example implementation: handle alternate sources for RED
    pass

  @staticmethod
  def manage_blank_sources(output_path):
    # Example implementation: manage blank sources in output file paths for RED
    if output_path.endswith('/'):
        return output_path + 'default_filename'
    return output_path