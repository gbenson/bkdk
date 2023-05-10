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

    @property
    def choices(self):
        xcen = self.width // 2
        xcen_plusminus = self.width * 5 // 16
        ycen = self.board.cen_xy[1] + self.width * 105 // 144
        cellsize = self.width // 18
        return tuple(
            ChoiceDecoder(self,
                          ((xcen + xcen_plusminus * (i - 1),
                            ycen)),
                          cellsize)
            for i in range(3))


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


class ChoiceDecoder:
    def __init__(self, img, cen_xy, cellsize):
        self.img = img
        self.cen_xy = cen_xy
        self.cellsize = cellsize
        for self.num_rows in 4, 5:
            for self.num_cols in 4, 5:
                try:
                    list(cell.is_set for cell in self.cells)
                    return
                except CellDecodingError:
                    pass

    @property
    def _shape(self):
        return self.num_rows, self.num_cols

    @property
    def cells(self):
        for row in range(self.num_rows):
            yoff = (row * 2 - (self.num_rows - 1)) * self.cellsize // 2
            ycen = self.cen_xy[1] + yoff
            for col in range(self.num_cols):
                xoff = (col * 2 - (self.num_cols - 1)) * self.cellsize // 2
                xcen = self.cen_xy[0] + xoff
                yield CellDecoder(self.img, (xcen, ycen), self.cellsize)

    def tolist(self):
        result = np.asarray([cell.is_set for cell in self.cells],
                            dtype=np.uint8).reshape(self._shape)
        if self.num_cols < 5:
            result = np.hstack((result, np.zeros((self.num_rows, 1),
                                                 dtype=result.dtype)))
        if self.num_rows < 5:
            result = np.vstack((result, np.zeros(5, dtype=result.dtype)))
        return result.tolist()


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
        confidence = 100 * max_count // num_pixels
        if confidence < 99:
            raise CellDecodingError(f"{confidence}% at {self.rect}")
        return 0 in color


class CellDecodingError(ValueError):
    pass
