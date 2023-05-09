from PIL import Image


def Screenshot(*args, **kwargs):
    img = Image.open(*args, **kwargs)
    # https://stackoverflow.com/a/11050571
    cls = img.__class__
    img.__class__ = cls.__class__(cls.__name__ + "Screenshot",
                                  (cls, ScreenshotDecoder), {})
    return img


class ScreenshotDecoder:
    pass
