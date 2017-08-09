import zbar
import zbar.misc
from matplotlib.image import imread


def scan_image(image_filename):
    """A method to extract the ISBN from the image"""
    barcodes = []
    img_np_array = imread(image_filename)
    if len(img_np_array.shape) == 3:
        img_np_array = zbar.misc.rgb2gray(img_np_array)

    scanner = zbar.Scanner(config=[('ZBAR_ISBN13', 'ZBAR_CFG_ENABLE', 1)])

    for barcode in scanner.scan(img_np_array):
        barcodes.append(barcode.data.decode('ascii'))

    return barcodes
