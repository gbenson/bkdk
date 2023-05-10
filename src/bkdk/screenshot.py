import numpy as np
from PIL import Image, ImageOps


def Screenshot(*args, **kwargs):
    img = Image.open(*args, **kwargs)
    # https://stackoverflow.com/a/11050571
    cls = img.__class__
    img.__class__ = cls.__class__(cls.__name__ + "Screenshot",
                                  (cls, ScreenshotDecoder), {})
    return img


class ScreenshotDecoder:
    @property
    def board(self):
        boardsize = min(self.size) * 17 // 18
        cellsize = boardsize // 9
        yoffset = self.width * 5 // 72
        return BoardDecoder(self,
                            (self.width // 2,
                             self.height // 2 - yoffset),
                            cellsize)


class BoardDecoder:
    def __init__(self, img, cen_xy, cellsize):
        self.img = img
        self.cen_xy = cen_xy
        self.cellsize = cellsize

    @property
    def cells(self):
        for row in range(-4, 5):
            ycen = self.cen_xy[1] + row * self.cellsize
            for col in range(-4, 5):
                xcen = self.cen_xy[0] + col * self.cellsize
                yield CellDecoder(self.img, (xcen, ycen), self.cellsize)

    def tolist(self):
        return np.asarray([cell.is_set for cell in self.cells],
                          dtype=np.uint8).reshape((9, 9)).tolist()


class CellDecoder:
    def __init__(self, img, cen_xy, cellsize):
        self.img = img
        self.cen_xy = cen_xy
        self.cellsize = cellsize

    @property
    def rect(self):
        x, y = self.cen_xy
        r = self.cellsize // 3
        return (x - r, y - r, x + r, y + r)

    @property
    def is_set(self):
        img = self.img.crop(self.rect)
        img = ImageOps.posterize(img, 1)
        num_pixels = img.width * img.height
        colors = img.getcolors(num_pixels)
        max_count, color = max(colors)
        assert max_count * 100 > num_pixels * 99
        return 0 in color
