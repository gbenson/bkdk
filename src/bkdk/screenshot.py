from PIL import Image


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
        cellsize = min(self.size) * 2 // 19
        boardsize = cellsize * 9
        return BoardDecoder(self,
                            ((self.width - boardsize) // 2 + 1,
                             (self.height - boardsize) // 2 - 53),
                            cellsize)


class BoardDecoder:
    def __init__(self, img, topleft, cellsize):
        self.img = img
        self.topleft = topleft
        self.cellsize = cellsize

    @property
    def cells(self):
        left, top = self.topleft
        for row in range(9):
            ycen = ((row * 2 + 1) * self.cellsize) // 2 + top
            for col in range(9):
                xcen = ((col * 2 + 1) * self.cellsize) // 2 + left
                yield CellDecoder(self.img, (xcen, ycen), self.cellsize)


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
