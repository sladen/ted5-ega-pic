#!/usr/bin/python
"""
Paul Sladen, 27 September 2017, hereby placed in the Public Domain / CC0 / BSD 2-clause

One of the Debian Doom maintainers requested help regarding whether a
25-year old binary file with the extension '.PIC' could be decoded to
confirm its contents and if was indeed a picture of some sort.

Apologies were latterly received once the contents of the portrait
were understood.

File format
===========
  magic: 'PIC\x00' header
  columns: 16-bit little endian
  rows: 16-bit little endian
  blue: bitwise data plane
  green: bitwise data plane
  red: bitwise data plane
  intensity: bitwise data plane

The data itself corresponds closely to a 1980s EGA (Extended Graphics
Adaptor) in 320x200x16 colour mode.  If one had such a card to hand,
the bitplane data could be pasted into memory without modification.

Because the data is bitwise, the column width must be multipled by eight.
There are four bitplanes in the order Blue, Green, Red, Intensity.
These together give indexes into an EGA-style palette:
The RGB bits each contribute 0xaa (170) to their respective channel.
The Intensity bit contributes 0x55 (85) to all output channels.

The Debian Developer was only able to provide a single sample file
so usual comparative analysis was not possible.  The conclusions
reached are therefore on a sample size of one, and alternative
methods were required to sanity check the deductions reached and
that a correct decoding could be archieved.

Context
=======
A file of this type appears twice in the "TED 5" (iD Software Tile
Editor 5) source code release, once in native form with a '.PIC' extension,
and once embedded into a pre-compiled Object file with the extension '.OBJ'.
The Object file contains a string symbol with a textual description
corresponding to the '.PIC' contents.  An accompanying header file
declaration appears to correspond to the data.  This is commented out
using C preprocessor declarations, so is not included in the '.EXE' executable.

  #if 0
  extern char far TOM;    // JOKE SHIT!
  #endif

Further reading
===============
The same Debian Developer subsequently located a published reference giving
additional insight into the background and the picture's inclusion
in the TED 5 source code:

  By Sanglard, Fabien (31 August 2017).
  "Game Engine Black Book: Wolfenstein 3D".
  Page 89.  Chapter 3.5. Trivia.  
  https://books.google.co.uk/books?id=Lq4yDwAAQBAJ&pg=PA89

This contains a statement from John Romero of iD Software, naming the
artist as Adrian Carmack, and the caricature being of Tom Hall.  In
the early 1990s, all three were employees of iD along with John
Carmack.

A section of the lower part of the picture is partially obscured, and
so a direct comparision is unlikely to be possible.

Output format
=============
The convertor deinterlaces the bitplanes and writes 24-bit RGB triplets to
stdout, ensuring that further work is required by the user to easily
display the result.

Wider use
=========
A matching 'PIC\x0' header is described at:

  http://www.shikadi.net/moddingwiki/PIC_Format#PIC_format_version_2
  http://www.shikadi.net/moddingwiki/Rescue_Rover

With a reference to "Rescue Rover" (but without the described
RLE (Run Length Encoding) step.
"""
import sys
import struct

def main():
    header_size = 8
    s = open(sys.argv[1], 'rb').read()
    magic, cols, rows = struct.unpack('<4sHH', s[0:header_size])
    assert magic == 'PIC\x00'
    assert cols == 40
    assert rows == 200
    planes = 4

    blue = s[8:8008]
    green = s[8008:16008]
    red = s[16008:24008]
    intensity = s[24008:32008] # intensity

    def ega(bitplane, index, shift, value = 0xaa):
        return ((ord(bitplane[index]) >> shift) & 0x01) * value

    out = ''
    for i in range(0, cols * rows):
        for shift in range(7,-1,-1): # bit 7..0
            for plane in red, green, blue:
                out += chr(ega(plane, i, shift, value = 0xaa) +
                           ega(intensity, i, shift, value = 0x55))
    print out,

if __name__=='__main__':
    main()
