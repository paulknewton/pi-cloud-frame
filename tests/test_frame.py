import media_players


def skip_test_playlist():
    player = media_players.PhotoPlayer("test_photo_player", "tests/test_photos")
    assert player.get_folder() == "tests/test_photos"
    assert player.get_playlist() == ["1.jpg", "2.jpg"]
