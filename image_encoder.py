#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Compiled with Coconut version 0.3.1-dev [Ilocos]

# Coconut Header: --------------------------------------------------------------

from __future__ import with_statement, print_function, absolute_import, unicode_literals, division
try: from future_builtins import *
except ImportError: pass
try: xrange
except NameError: pass
else:
    range = xrange
try: ascii
except NameError: ascii = repr
try: unichr
except NameError: pass
else:
    py2_chr = chr
    chr = unichr
_coconut_encoding = "UTF-8"
try: unicode
except NameError: pass
else:
    bytes, str = str, unicode
    py2_print = print
    def print(*args, **kwargs):
        """Wraps py2_print."""
        return py2_print(*(str(x).encode(_coconut_encoding) for x in args), **kwargs)
try: raw_input
except NameError: pass
else:
    py2_input = raw_input
    def input(*args, **kwargs):
        """Wraps py2_input."""
        return py2_input(*args, **kwargs).decode(_coconut_encoding)

import sys as _coconut_sys
import os.path as _coconut_os_path
_coconut_sys.path.append(_coconut_os_path.dirname(_coconut_os_path.abspath(__file__)))
import __coconut__

reduce = __coconut__.functools.reduce
itemgetter = __coconut__.operator.itemgetter
attrgetter = __coconut__.operator.attrgetter
methodcaller = __coconut__.operator.methodcaller
takewhile = __coconut__.itertools.takewhile
dropwhile = __coconut__.itertools.dropwhile
tee = __coconut__.itertools.tee
recursive = __coconut__.recursive
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
