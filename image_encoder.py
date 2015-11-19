#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# __coconut_hash__ = 0x7d18c0b3

# Compiled with Coconut version 0.3.4-post_dev [Macapuno]

# Coconut Header: --------------------------------------------------------------

from __future__ import with_statement, print_function, absolute_import, unicode_literals, division
import sys as _coconut_sys
if _coconut_sys.version_info < (3,):
    py2_filter, py2_hex, py2_map, py2_oct, py2_zip = filter, hex, map, oct, zip
    from future_builtins import *
    py2_range, range = range, xrange
    py2_int = int
    _coconut_int, _coconut_long = int, long
    class _coconut_metaint(type):
        def __instancecheck__(cls, inst):
            return isinstance(inst, (_coconut_int, _coconut_long))
    class int(_coconut_int):
        """Python 3 int."""
        __metaclass__ = _coconut_metaint
    py2_chr, chr = chr, unichr
    bytes, str = str, unicode
    _coconut_encoding = "UTF-8"
    py2_print = print
    _coconut_print = print
    def print(*args, **kwargs):
        """Python 3 print."""
        return _coconut_print(*(str(x).encode(_coconut_encoding) for x in args), **kwargs)
    py2_input = raw_input
    _coconut_input = raw_input
    def input(*args, **kwargs):
        """Python 3 input."""
        return _coconut_input(*args, **kwargs).decode(_coconut_encoding)

import os.path as _coconut_os_path
_coconut_sys.path.append(_coconut_os_path.dirname(_coconut_os_path.abspath(__file__)))
import __coconut__

__coconut_version__ = __coconut__.version
reduce = __coconut__.functools.reduce
takewhile = __coconut__.itertools.takewhile
dropwhile = __coconut__.itertools.dropwhile
tee = __coconut__.itertools.tee
recursive = __coconut__.recursive
datamaker = __coconut__.datamaker
MatchError = __coconut__.MatchError

# Compiled Coconut: ------------------------------------------------------------

# IMPORTS:

import numpy as np
import pywt
import os.path

# CONSTANTS:

COVER_IMAGE = "iconBW.png"
SECRET_IMAGE = "Copyright.png"
WAVELET = "haar"
ALPHA = .99
BETA = 1 - ALPHA

assert ALPHA > BETA

# UTILITIES:

product = __coconut__.functools.partial(reduce, __coconut__.operator.__mul__)

transform = __coconut__.functools.partial(pywt.dwt2, wavelet=WAVELET)

inv_transform = __coconut__.functools.partial(pywt.idwt2, wavelet=WAVELET)

def trans_shape(image): return (image.shape[0] + 1) // 2, (image.shape[1] + 1) // 2

def fuse(a, b): return (a * ALPHA + b * BETA) / (ALPHA + BETA)

def unfuse(out, a): return (out * (ALPHA + BETA) - a * ALPHA) / BETA

def encode(cover_image, secret_image):
    assert cover_image.ndim == 2
    assert secret_image.ndim == 2
    shape1 = trans_shape(cover_image)
    a1, (h1, v1, d1) = transform(cover_image)
    shape2 = trans_shape(secret_image)
    a2, (h2, v2, d2) = transform(secret_image)
    for x in range(0, shape1[0]):
        for y in range(0, shape1[1]):
            if x < shape2[0] and y < shape2[1]:
                a1[x, y] = fuse(a1[x, y], a2[x, y])
                h1[x, y] = fuse(h1[x, y], h2[x, y])
                v1[x, y] = fuse(v1[x, y], v2[x, y])
                d1[x, y] = fuse(d1[x, y], d2[x, y])
    return inv_transform((a1, (h1, v1, d1)))

def decode(encoded_image, cover_image):
    assert encoded_image.ndim == 2
    assert cover_image.ndim == 2
    shape1 = trans_shape(encoded_image)
    a1, (h1, v1, d1) = transform(encoded_image)
    shape2 = trans_shape(cover_image)
    a2, (h2, v2, d2) = transform(cover_image)
    for x in range(0, shape1[0]):
        for y in range(0, shape1[1]):
            if x < shape2[0] and y < shape2[1]:
                a1[x, y] = unfuse(a1[x, y], a2[x, y])
                h1[x, y] = unfuse(h1[x, y], h2[x, y])
                v1[x, y] = unfuse(v1[x, y], v2[x, y])
                d1[x, y] = unfuse(d1[x, y], d2[x, y])
    return inv_transform((a1, (h1, v1, d1)))

# MAIN:

if __name__ == "__main__":
    from skimage import io
    secret_image = io.imread(SECRET_IMAGE, as_grey=True)
    io.imshow(secret_image)
    print("SECRET IMAGE")
    io.show()
    cover_image = io.imread(COVER_IMAGE, as_grey=True)
    io.imshow(cover_image)
    print("COVER IMAGE")
    io.show()
    encoded_image = encode(cover_image, secret_image)
    io.imshow(encoded_image)
    print("ENCODED IMAGE")
    io.show()
    retrieved_image = decode(encoded_image, cover_image)
    io.imshow(retrieved_image)
    print("RETRIEVED IMAGE")
    io.show()
