import zbar
import zbar.misc
import numpy as np
from PIL import Image, ImageEnhance


def scan_for_isbn(image_file):
    """A method to extract the ISBN from the image"""
    isbns = []

    max_length = 850
    scanner = zbar.Scanner(config=[('ZBAR_ISBN13', 'ZBAR_CFG_ENABLE', 1)])

    # import image, converting to black and white
    image = Image.open(image_file).convert('L')

    # resize big images for speed and improved scanning in most cases
    if [d > max_length for d in image.size]:
        image = image.resize((500, 700), Image.ANTIALIAS)

    # first scan image as it is
    img_arr = np.fromstring(image.tobytes(), dtype=np.uint8)
    img_arr = img_arr.reshape((image.size[1], image.size[0]))

    results = scanner.scan(img_arr)

    # if no ISBN or non-ISBN code found, enhance contrast and scan again
    if not results or not all(r.type == 'ISBN-13' for r in results):
        image = ImageEnhance.Contrast(image).enhance(2)

        img_arr = np.fromstring(image.tobytes(), dtype=np.uint8)
        img_arr = img_arr.reshape((image.size[1], image.size[0]))

        results = scanner.scan(img_arr)

    # if no ISBN or non-ISBN codes found, change size and scan again
    if not results or not all(r.type == 'ISBN-13' for r in results):
        image = image.resize((700, 500), Image.ANTIALIAS)

        img_arr = np.fromstring(image.tobytes(), dtype=np.uint8)
        img_arr = img_arr.reshape((image.size[1], image.size[0]))

        results = scanner.scan(img_arr)

    if results:
        for result in [r for r in results if r.type == 'ISBN-13']:
            isbns.append(result.data.decode('ascii'))

    return isbns
