from .helpers import SetupTeardown\nfrom src.trackers import RedTracker, OpsTracker\n\n\nclass TestTrackerMethods(SetupTeardown):\n  def test_source_flags_for_search(self):\n    assert RedTracker.source_flags_for_search() == [b"RED", b"PTH"]\n    assert OpsTracker.source_flags_for_search() == [b"OPS", b"APL", b""]\n\n  def test_source_flags_for_creation(self):\n    assert RedTracker.source_flags_for_creation() == [b"RED", b"PTH", b""]\n    assert OpsTracker.source_flags_for_creation() == [b"OPS", b"APL", b""]\n\n  def test_announce_url(self):\n    assert RedTracker.announce_url() == b"flacsfor.me"\n    assert OpsTracker.announce_url() == b"home.opsfet.ch"\n\n  def test_site_shortname(self):\n    assert RedTracker.site_shortname() == "RED"\n    assert OpsTracker.site_shortname() == "OPS"\n\n  def test_reciprocal_tracker(self):\n    assert RedTracker.reciprocal_tracker() == OpsTracker\n    assert OpsTracker.reciprocal_tracker() == RedTracker\n