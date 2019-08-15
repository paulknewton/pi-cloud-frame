import random


def get_sample(photos, n):
    """
    Select a random sample from a list of photos.

    :param photos: list of photos
    :param n: number of photos to sample
    :return: a random list of samples containing n items (or fewer if there are not enough photos)
    """
    n = min(n, len(photos))
    n = max(n, 0)   # avoid -ve numbers
    return random.sample(photos, n)


def crop_image(image, aspect_ratio):
    """Crop an image to match the desired aspect ratio. This is not used because Pillow cannot handle HEIC libraries."""
    print("Cropping with aspect ratio", aspect_ratio)

    width, height = image.size
    left = 0
    right = width
    new_height = width / aspect_ratio
    top = (height - new_height) / 2
    bottom = top + new_height

    box = (left, top, right, bottom)
    print("box = ", box)
    image = image.crop(box)
    # image.show()

    return image
