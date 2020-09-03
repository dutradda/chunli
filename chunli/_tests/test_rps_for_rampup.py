from chunli.caller import rps_for_rampup


def test_should_get_rps_for_rampup_10_percent():
    assert rps_for_rampup(1, 10, 100) == 10


def test_should_get_rps_for_rampup_90_percent():
    assert rps_for_rampup(9, 10, 100) == 90


def test_should_not_get_rps_for_rampup():
    assert rps_for_rampup(10, 10, 100) == 100
