#!/usr/bin/env python

# Compiled with Coconut version 0.2.1-dev [Fiji]

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
except NameError: unichr = chr
try: unicode
except NameError: pass
else:
    bytes, str = str, unicode
    _coconut_print = print
    def print(*args, **kwargs):
        """Wraps _coconut_print."""
        return _coconut_print(*(str(x).encode("utf8") for x in args), **kwargs)
try: raw_input
except NameError: pass
else:
    _coconut_input = raw_input
    def input(*args, **kwargs):
        """Wraps _coconut_input."""
        return _coconut_input(*args, **kwargs).decode("utf8")

import sys as _coconut_sys
import os.path as _coconut_os_path
_coconut_sys.path.append(_coconut_os_path.dirname(_coconut_os_path.abspath(__file__)))
import __coconut__

reduce = __coconut__.reduce
itemgetter = __coconut__.itemgetter
attrgetter = __coconut__.attrgetter
methodcaller = __coconut__.methodcaller
takewhile = __coconut__.takewhile
dropwhile = __coconut__.dropwhile
tee = __coconut__.tee
recursive = __coconut__.recursive

# Compiled Coconut: ------------------------------------------------------------

# IMPORTS:

import pywt

# CONSTANTS:

WAVELET = "haar"
ALPHA = .99
BETA = 1 - ALPHA

assert ALPHA > BETA

# UTILITIES:

product = __coconut__.partial(reduce, (__coconut__.operator.__mul__))

transform = __coconut__.partial(pywt.dwt2, wavelet=WAVELET)

inv_transform = __coconut__.partial(pywt.idwt2, wavelet=WAVELET)

def trans_shape(image):
    return (image.shape[0] + 1) // 2, (image.shape[1] + 1) // 2

def fuse(a, b):
    out = (a * ALPHA + b * BETA) / (ALPHA + BETA)
    return __coconut__.pipe(out, round, int)

def unfuse(out, a):
    b = (out * (ALPHA + BETA) - a * ALPHA) / BETA
    return __coconut__.pipe(b, round, int)

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
    assert encoded_image.shape == cover_image.shape
    shape = trans_shape(encoded_image)
    a1, (h1, v1, d1) = transform(encoded_image)
    a2, (h2, v2, d2) = transform(cover_image)
    for x in range(0, shape[0]):
        for y in range(0, shape[1]):
            a1[x, y] = unfuse(a1[x, y], a2[x, y])
            h1[x, y] = unfuse(h1[x, y], h2[x, y])
            v1[x, y] = unfuse(v1[x, y], v2[x, y])
            d1[x, y] = unfuse(d1[x, y], d2[x, y])
    return inv_transform((a1, (h1, v1, d1)))

# MAIN:

if __name__ == "__main__":
    from skimage import io, data
    cover_image = data.checkerboard()
    secret_image = data.coins()
    io.imshow(cover_image)
    io.show()
    encoded_image = encode(cover_image, secret_image)
    io.imshow(encoded_image)
    io.show()
    retrieved_image = decode(encoded_image, cover_image)
    io.imshow(retrieved_image)
    io.show()
