#!/usr/bin/env python3
"""The Sunday Blast - a one-image summary of the world news of
Sunday 22 November 2026, drawn as a tabloid front page.

Pure Python 3 standard library. The picture is painted pixel by pixel
into an RGB framebuffer with a hand-built 5x7 block typeface, then
encoded as a PNG with zlib. No network, no files read, no clock, no
randomness: every run writes exactly the same bytes to
$MAKEFUN_OUTPUT_DIR/entry.png.
"""

import os
import struct
import zlib

# ---------------------------------------------------------------- canvas

W = 1024
H = 1024

PAPER = (247, 243, 233)   # warm newsprint
INK = (18, 18, 18)        # near-black type
RED = (176, 12, 30)       # tabloid red
DARK = (22, 22, 22)       # date strip
GREY = (105, 105, 105)    # secondary type
WHITE = (255, 255, 255)


def new_canvas():
    return bytearray(PAPER) * (W * H)


def set_px(buf, x, y, colour):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i] = colour[0]
        buf[i + 1] = colour[1]
        buf[i + 2] = colour[2]


def fill_rect(buf, x, y, w, h, colour):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    row = bytes(colour) * (x1 - x0)
    for yy in range(y0, y1):
        i = (yy * W + x0) * 3
        buf[i:i + len(row)] = row


def frame(buf, x, y, w, h, thickness, colour):
    fill_rect(buf, x, y, w, thickness, colour)
    fill_rect(buf, x, y + h - thickness, w, thickness, colour)
    fill_rect(buf, x, y, thickness, h, colour)
    fill_rect(buf, x + w - thickness, y, thickness, h, colour)


# ---------------------------------------------------------------- type
# A 5x7 block typeface. Each glyph is seven rows of five bits,
# bit 4 the leftmost pixel of the row.

FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1C, 0x12, 0x11, 0x11, 0x11, 0x12, 0x1C),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x11, 0x19, 0x15, 0x13, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x15, 0x0A),
    "X": (0x11, 0x0A, 0x04, 0x04, 0x04, 0x0A, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    "3": (0x1E, 0x01, 0x01, 0x0E, 0x01, 0x01, 0x1E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
    ".": (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
    ",": (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
    "'": (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    '"': (0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00),
    ":": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00),
    ";": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x04, 0x08),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x06, 0x04, 0x00, 0x04),
    "-": (0x00, 0x00, 0x00, 0x0E, 0x00, 0x00, 0x00),
    "+": (0x00, 0x04, 0x04, 0x0E, 0x04, 0x04, 0x00),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    "%": (0x19, 0x1A, 0x02, 0x04, 0x08, 0x0B, 0x13),
    "/": (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "*": (0x00, 0x04, 0x15, 0x0E, 0x15, 0x04, 0x00),
    "=": (0x00, 0x00, 0x0E, 0x00, 0x0E, 0x00, 0x00),
}


def text_width(text, scale):
    if not text:
        return 0
    return len(text) * 6 * scale - scale


def draw_text(buf, x, y, text, scale, colour):
    cx = x
    for ch in text.upper():
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            if not bits:
                continue
            for col in range(5):
                if bits & (1 << (4 - col)):
                    fill_rect(buf, cx + col * scale, y + row * scale,
                              scale, scale, colour)
        cx += 6 * scale
    return cx


def draw_centered(buf, y, text, scale, colour):
    x = (W - text_width(text, scale)) // 2
    draw_text(buf, x, y, text, scale, colour)


def draw_right(buf, right_x, y, text, scale, colour):
    x = right_x - text_width(text, scale)
    draw_text(buf, x, y, text, scale, colour)


# ---------------------------------------------------------------- png

def _chunk(tag, payload):
    return (struct.pack(">I", len(payload)) + tag + payload
            + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF))


def encode_png(buf):
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)  # filter: none
        raw += buf[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + _chunk(b"IEND", b""))


# ---------------------------------------------------------------- content
# Every fact below is the news of Sunday 22 November 2026 as reported
# that day (Reuters; AFP via Monrovia). Wording is compressed to fit
# the page; nothing is added that the reports did not say.

MASTHEAD = "SUNDAY BLAST"
DATE_LINE = "SUNDAY 22 NOVEMBER 2026"

LEAD_TAG = "CLIMATE SUMMIT"
LEAD_PLACE = "ANTALYA, TURKIYE"
LEAD_HEAD = ("CLIMATE DEAL", "NEARS IN ANTALYA")
LEAD_BODY = (
    "NEARLY 200 DELEGATIONS WEIGH A FINAL",
    "PACKAGE TEXT AFTER TALKS BLEW PAST",
    "THE FRIDAY DEADLINE, INTO SUNDAY.",
    "KURUM: 'A TEXT WHICH ALL THE PARTIES",
    "CAN AGREE UPON.' DECISION 06:00 GMT.",
)

DRAFT_HEAD = "FOSSIL FUELS ERASED FROM DRAFT"
DRAFT_BODY = (
    "COAL, OIL AND GAS CUT; THE $120BN-A-YEAR",
    "ADAPTATION TARGET DROPPED. IN ITS PLACE,",
    "A CALL TO TRIPLE ADAPTATION AID BY 2035.",
    "EU'S HOEKSTRA: 'A GOOD DEAL OR NO DEAL.'",
)

LEFT_HEAD = ("23,000 WORKERS", "OUT ON STRIKE")
LEFT_BODY = (
    "IG METALL IN NORTHERN",
    "GERMANY CALLS A 24-HOUR",
    "MONDAY STRIKE: 19 FIRMS,",
    "MERCEDES-BENZ, MEYER",
    "WERFT, SIEMENS GAMESA.",
    "WANTS 5%; 12,300 FRIDAY.",
)

RIGHT_HEAD = ("25 US DEPORTEES", "REACH LIBERIA")
RIGHT_BODY = (
    "25 MIGRANTS DEPORTED FROM",
    "THE US, TWO OF THEM WOMEN,",
    "ARRIVE IN LIBERIA; A LOCAL",
    "COMMISSION CONFIRMS (AFP).",
    "US DEAL ALLOWS UP TO 1,200",
    "DEPORTEES OVER 12 MONTHS.",
)

FOOTER = "THE SUNDAY BLAST - ALL THE NEWS OF 22 NOVEMBER 2026"

MARGIN = 28
RIGHT_EDGE = W - MARGIN


def draw_lines(buf, x, y, lines, scale, colour, pitch):
    for line in lines:
        draw_text(buf, x, y, line, scale, colour)
        y += pitch
    return y


def compose():
    buf = new_canvas()
    frame(buf, 6, 6, W - 12, H - 12, 4, INK)

    # Masthead: red band, white title, thin white rule.
    fill_rect(buf, 0, 0, W, 120, RED)
    draw_centered(buf, 22, MASTHEAD, 10, WHITE)
    fill_rect(buf, MARGIN, 104, W - 2 * MARGIN, 3, WHITE)

    # Date strip: black band naming the day.
    fill_rect(buf, 0, 120, W, 44, DARK)
    draw_centered(buf, 128, DATE_LINE, 4, WHITE)

    # Lead story: COP31 in Antalya.
    fill_rect(buf, MARGIN, 178, 348, 38, RED)
    draw_text(buf, MARGIN + 14, 183, LEAD_TAG, 4, WHITE)
    draw_right(buf, RIGHT_EDGE, 186, LEAD_PLACE, 3, GREY)
    y = 228
    for line in LEAD_HEAD:
        draw_text(buf, MARGIN, y, line, 9, INK)
        y += 70
    y = draw_lines(buf, MARGIN, y, LEAD_BODY, 4, INK, 33)

    # The fossil-fuel fight inside the same talks.
    y += 12
    fill_rect(buf, MARGIN, y, W - 2 * MARGIN, 6, INK)
    y += 18
    draw_text(buf, MARGIN, y, DRAFT_HEAD, 5, RED)
    y += 44
    y = draw_lines(buf, MARGIN, y, DRAFT_BODY, 4, INK, 33)

    # Two columns: Germany strikes, Liberia deportees.
    y += 12
    fill_rect(buf, MARGIN, y, W - 2 * MARGIN, 6, INK)
    y += 18
    col_top = y
    for line in LEFT_HEAD:
        draw_text(buf, MARGIN, y, line, 5, INK)
        y += 38
    draw_lines(buf, MARGIN, y + 8, LEFT_BODY, 3, INK, 22)
    y = col_top
    for line in RIGHT_HEAD:
        draw_text(buf, 524, y, line, 5, INK)
        y += 38
    draw_lines(buf, 524, y + 8, RIGHT_BODY, 3, INK, 22)
    fill_rect(buf, 509, col_top, 3, 216, GREY)

    # Footer repeats the day the page sums up.
    draw_centered(buf, 990, FOOTER, 3, RED)
    return buf


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    png = encode_png(compose())
    with open(os.path.join(out_dir, "entry.png"), "wb") as fh:
        fh.write(png)


if __name__ == "__main__":
    main()
