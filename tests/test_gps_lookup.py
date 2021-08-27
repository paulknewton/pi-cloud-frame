from utils import photo_utils


def test_gps_location():
    gps_data = [50, 49, 859 / 100, "N", 0, 8, 249 / 20, "W"]
    expected = "Big Fish Trading Co., Grand Junction Road, Queen's Park, Brighton, Brighton and Hove, South East England, England, BN2 1TD, United Kingdom"
    assert photo_utils.get_gps_dms_location(*gps_data) == expected
