import mock
import pytest
from mock import PropertyMock

from network.icloud_photos import IcloudPhotos


class DummyPhoto:
    @property
    def _master_record(self):
        pass

    @property
    def _asset_record(self):
        pass

    @property
    def dimensions(self):
        pass


@mock.patch("test_icloud.DummyPhoto._master_record", new_callable=PropertyMock)
def test_is_image_with_photos(mock_photo_record):
    """
    Test photo is recognised as an image with various MIME types.

    :param mock_photo_record: mock photo setup by the Mock framework
    """
    photo = DummyPhoto()

    mock_photo_record.return_value = {"fields": {"itemType": {"value": "public.jpeg"}}}
    assert IcloudPhotos.is_image(photo)

    mock_photo_record.return_value = {"fields": {"itemType": {"value": "public.png"}}}
    assert IcloudPhotos.is_image(photo)

    mock_photo_record.return_value = {"fields": {"itemType": {"value": "public.heic"}}}
    assert IcloudPhotos.is_image(photo)

    mock_photo_record.return_value = {"fields": {"itemType": {"value": "public.tiff"}}}
    assert IcloudPhotos.is_image(photo)


def test_is_image_with_none():
    """
    Test the is_image method handles None images without failing.

    :param mock_photo_record: mock photo setup by the Mock framework
    """
    assert not IcloudPhotos.is_image(None)


@mock.patch("test_icloud.DummyPhoto._master_record", new_callable=PropertyMock)
def test_is_image_with_none_photos(mock_photo_record):
    """
    Test photo is not classified as an image with various (non-image) MIME types.

    :param mock_photo_record: mock photo setup by the Mock framework
    """
    photo = DummyPhoto()
    mock_photo_record.return_value = {"fields": {"itemType": {"value": "public.mpeg"}}}
    assert not IcloudPhotos.is_image(photo)


def test_format_none():
    """
    Test the format (portrait/landscape) function raises an exception with None images.

    :param mock_photo_record: mock photo setup by the Mock framework
    """
    with pytest.raises(ValueError):
        assert not IcloudPhotos.is_correct_format(None, "portrait")

    with pytest.raises(ValueError):
        assert not IcloudPhotos.is_correct_format(None, "landscape")


def test_format_invalid_orientation():
    """
    Test the format method for a photo if the orientation is an invalid value.

    :param mock_photo_record: mock photo setup by the Mock framework
    """
    photo = DummyPhoto()
    with pytest.raises(ValueError):
        assert IcloudPhotos.is_correct_format(photo, "blah")


@mock.patch("test_icloud.DummyPhoto.dimensions", new_callable=PropertyMock)
@mock.patch("test_icloud.DummyPhoto._asset_record", new_callable=PropertyMock)
@mock.patch("test_icloud.DummyPhoto._master_record", new_callable=PropertyMock)
def test_format(mock_photo_master_record, mock_photo_asset_record, mock_photo_dimensions):
    """
    Test photo is recognised corrctly as portrait vs. landscape (including when rotated).

    :param mock_photo_record: mock photo setup by the Mock framework
    """
    photo = DummyPhoto()

    mock_photo_master_record.return_value = {"fields": {"originalOrientation": {"value": 3}}}
    mock_photo_asset_record.return_value = {"fields": {"orientation": {"value": 3}}}
    mock_photo_dimensions.return_value = (50, 100)
    assert IcloudPhotos.is_correct_format(photo, "portrait")
    assert not IcloudPhotos.is_correct_format(photo, "landscape")

    mock_photo_master_record.return_value = {"fields": {"originalOrientation": {"value": 3}}}
    mock_photo_asset_record.return_value = {"fields": {"orientation": {"value": 3}}}
    mock_photo_dimensions.return_value = (100, 50)
    assert not IcloudPhotos.is_correct_format(photo, "portrait")
    assert IcloudPhotos.is_correct_format(photo, "landscape")

    # photo is rotated so dimensions needs to be swapped
    mock_photo_master_record.return_value = {"fields": {"originalOrientation": {"value": 6}}}
    mock_photo_asset_record.return_value = {"fields": {"orientation": {"value": 6}}}
    mock_photo_dimensions.return_value = (100, 50)
    assert IcloudPhotos.is_correct_format(photo, "portrait")
    assert not IcloudPhotos.is_correct_format(photo, "landscape")

    mock_photo_master_record.return_value = {"fields": {"originalOrientation": {"value": 8}}}
    mock_photo_asset_record.return_value = {"fields": {"orientation": {"value": 8}}}
    mock_photo_dimensions.return_value = (100, 50)
    assert IcloudPhotos.is_correct_format(photo, "portrait")
    assert not IcloudPhotos.is_correct_format(photo, "landscape")
