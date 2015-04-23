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

import numpy as np
import pywt

# CONSTANTS:

WAVELET = "haar"

# UTILITIES:

product = __coconut__.partial(reduce, (__coconut__.operator.__mul__))

transform = __coconut__.partial(pywt.dwt2, wavelet=WAVELET)

inv_transform = __coconut__.partial(pywt.idwt2, wavelet=WAVELET)

def lsb_0(num):
    if num % 2 == 0:
        out = num
    else:
        out = num - 1
    return __coconut__.pipe(out, round, int)

def lsb_1(num, mod=None):
    if num % 2 == 1:
        out = num
    elif mod is None or num + 1 < mod:
        out = num + 1
    else:
        out = num - 2
    return __coconut__.pipe(out, round, int)

def trans_shape(image):
    return (image.shape[0] + 1) // 2, (image.shape[1] + 1) // 2

def encode(image, binary):
    assert image.ndim == 2
    shape = trans_shape(image)
    assert product(shape) == len(binary)
    approximate, (horizontal, vertical, diagonal) = transform(image)
    i = 0
    for x in range(0, shape[0]):
        for y in range(0, shape[1]):
            if not binary[i] or binary[i] == "0":
                horizontal[x, y] = __coconut__.pipe(horizontal[x, y], (lsb_0))
                vertical[x, y] = __coconut__.pipe(vertical[x, y], (lsb_0))
                diagonal[x, y] = __coconut__.pipe(diagonal[x, y], (lsb_0))
            else:
                horizontal[x, y] = __coconut__.pipe(horizontal[x, y], (lsb_1))
                vertical[x, y] = __coconut__.pipe(vertical[x, y], (lsb_1))
                diagonal[x, y] = __coconut__.pipe(diagonal[x, y], (lsb_1))
            i += 1
    return inv_transform((approximate, (horizontal, vertical, diagonal)))

def decode(image):
    assert image.ndim == 2
    shape = trans_shape(image)
    approximate, (horizontal, vertical, diagonal) = transform(image)
    binary = []
    for x in range(0, shape[0]):
        for y in range(0, shape[1]):
            bits = __coconut__.pipe((horizontal[x, y], vertical[x, y], diagonal[x, y]), __coconut__.partial(map, lambda n: int(round(n)) % 2), list)
            if not any(bits):
                binary.append(0)
            elif all(bits):
                binary.append(1)
            else:
                print("LSB values diverge: binary[" + str(len(binary)) + "] = transform(image)[" + str(x) + ", " + str(y) + "] = " + repr(bits))
                if sum(bits) == 1:
                    binary.append(0)
                    print("    Assuming: binary[" + str(len(binary)) + "] = 0")
                elif sum(bits) == 2:
                    binary.append(1)
                    print("    Assuming: binary[" + str(len(binary)) + "] = 1")
                else:
                    raise ValueError("No agreement among LSB values: binary[" + str(len(binary)) + "] = transform(image)[" + str(x) + ", " + str(y) + "] = " + repr(bits))
    return binary

# MAIN:

if __name__ == "__main__":
    from skimage import io, data
    pre_image = data.coins()
    length = product(trans_shape(pre_image))
    post_image = encode(pre_image, [0] * length)
    errors = sum(decode(post_image))
    print("Errors: " + str(errors) + " (" + str(100 * errors / length) + "%)")
    io.imshow(post_image)
    io.show()
