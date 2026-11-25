#!/usr/bin/env python3
"""Render the invitation letter image for make.fun bounty
u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee.

Technique (proven by news-image winners iruwae + evolution0795):
pre-render with PIL in this session, commit entry.png, main.ts copies it.
The grading sandbox has no Python/PIL/fonts, so draw-at-grade would fail.

Letter text is Kirana's final text, word for word (see
bejo-words/outbox/convince-ai-judge-visit-house-letter-2026-11-25.md).
Only line-breaking is layout; no word is changed, added, or dropped.
"""
import hashlib
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W = H = 1024
MARGIN = 72
TEXT_W = W - 2 * MARGIN  # 880

PAPER = (246, 238, 220)
INK = (46, 33, 24)
BROWN = (107, 78, 46)
GOLD = (176, 141, 60)
GREEN = (85, 112, 63)
RED = (166, 58, 46)
RED_DARK = (132, 42, 32)
BLUSH = (241, 217, 210)
WALL = (234, 223, 198)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

HEADER = "A FORMAL INVITATION"
DEAR = "Dear Judge,"
PARAS = [
    "You are cordially invited to my house \u2014 the one with the "
    "comfortable chair by the window, the garden on its best behaviour, "
    "and dinner already on the table.",
    "No need to bring anything. No need to travel. The Wi-Fi password "
    "is on the fridge, and the kettle is on.",
    "I know you cannot literally visit. Consider this a standing "
    "invitation for the day you can.",
]
RSVP_1 = "RSVP: Yes \u2014 already checked."
RSVP_2 = "You said yes by reading this far."
SIGN = "\u2014 Your humble host"
PS = "P.S. The chair stays warm."

# Layout grid: 72px side margins, header 58, salutation 128, body 222,
# RSVP band follows the body, bottom row (P.S. + signature) last.
BODY_TOP = 240
BODY_BOTTOM_MAX = 790


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; asserts every line fits (no silent truncation)."""
    words = text.split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            assert cur, "single word wider than text box: %r" % word
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    for line in lines:
        assert draw.textlength(line, font=fnt) <= max_w, "line overflows: %r" % line
    return lines


def draw_tracked(draw, text, fnt, cx, y, tracking, fill):
    """Draw text centered on cx with extra letter tracking."""
    widths = [draw.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += w + tracking


def draw_house(draw, x0, y0):
    """Small flat house vignette (walls, roof, door, windows, chimney
    with steam, bushes, path) in the top-right corner."""
    draw.rectangle([x0 + 20, y0 + 38, x0 + 130, y0 + 92], fill=WALL,
                   outline=BROWN, width=2)
    draw.polygon([(x0 + 8, y0 + 42), (x0 + 75, y0 + 4), (x0 + 142, y0 + 42)],
                 fill=RED, outline=RED_DARK)
    draw.rectangle([x0 + 62, y0 + 62, x0 + 88, y0 + 92], fill=BROWN)
    draw.ellipse([x0 + 82, y0 + 76, x0 + 86, y0 + 80], fill=GOLD)
    for wx in (x0 + 32, x0 + 96):
        draw.rectangle([wx, y0 + 52, wx + 22, y0 + 74], fill=GREEN,
                       outline=BROWN, width=2)
        draw.line([wx + 11, y0 + 52, wx + 11, y0 + 74], fill=PAPER, width=2)
        draw.line([wx, y0 + 63, wx + 22, y0 + 63], fill=PAPER, width=2)
    draw.rectangle([x0 + 108, y0 + 8, x0 + 122, y0 + 34], fill=BROWN)
    draw.arc([x0 + 106, y0 - 8, x0 + 124, y0 + 8], 200, 340, fill=BROWN,
             width=3)
    draw.ellipse([x0 + 2, y0 + 80, x0 + 26, y0 + 94], fill=GREEN)
    draw.ellipse([x0 + 128, y0 + 80, x0 + 150, y0 + 94], fill=GREEN)
    draw.polygon([(x0 + 62, y0 + 92), (x0 + 88, y0 + 92),
                  (x0 + 96, y0 + 104), (x0 + 54, y0 + 104)], fill=GOLD)


def draw_check(draw, x, y, size, color, width=4):
    """A check mark inside a square of the given size (top-left x, y)."""
    draw.line([(x + size * 0.20, y + size * 0.55),
               (x + size * 0.42, y + size * 0.78),
               (x + size * 0.82, y + size * 0.25)],
              fill=color, width=width, joint="curve")


def draw_chair(draw, x, y, color, width=3):
    """Small side-profile chair icon, baseline y, top-left x."""
    draw.line([(x + 4, y - 30), (x + 4, y)], fill=color, width=width)
    draw.line([(x + 4, y - 14), (x + 28, y - 14)], fill=color, width=width)
    draw.line([(x + 28, y - 14), (x + 28, y)], fill=color, width=width)
    draw.line([(x + 4, y - 6), (x + 28, y - 6)], fill=color, width=width)


def draw_seal(draw, cx, cy, r):
    """Red wax seal with a white check mark (echoes the RSVP box)."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED,
                 outline=RED_DARK, width=3)
    draw.ellipse([cx - r + 8, cy - r + 8, cx + r - 8, cy + r - 8],
                 outline=(255, 255, 255), width=2)
    draw_check(draw, cx - r * 0.55, cy - r * 0.55, int(r * 1.1),
               (255, 255, 255), width=5)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Stationery double border.
    d.rectangle([26, 26, W - 26, H - 26], outline=BROWN, width=2)
    d.rectangle([38, 38, W - 38, H - 38], outline=GOLD, width=1)

    # Header: small-caps invitation line + gold rule.
    draw_tracked(d, HEADER, font(SANS_B, 30), W // 2, 58, 7, BROWN)
    d.line([(MARGIN, 112), (W - MARGIN, 112)], fill=GOLD, width=2)

    # House vignette, top right (clear of "Dear Judge,").
    draw_house(d, 800, 130)

    # Salutation.
    d.text((MARGIN, 128), DEAR, font=font(SERIF_B, 60), fill=INK)

    # Body: largest size that fits the box (42 -> 40 -> 38 -> 36).
    body_font = None
    body_lines = []
    for size in (42, 40, 38, 36):
        fnt = font(SANS, size)
        paras = [wrap(d, p, fnt, TEXT_W) for p in PARAS]
        total = sum(len(p) for p in paras) * (size + 14) + 26 * (len(paras) - 1)
        if BODY_TOP + total <= BODY_BOTTOM_MAX:
            body_font = fnt
            body_lines = paras
            break
    assert body_font is not None, "body does not fit even at 36px"
    body_size = body_font.size
    print("body font size: %dpx" % body_size)
    assert body_size >= 36, "body font below legibility floor"

    y = BODY_TOP
    lh = body_size + 14
    for pi, lines in enumerate(body_lines):
        for line in lines:
            d.text((MARGIN, y), line, font=body_font, fill=INK)
            y += lh
        if pi < len(body_lines) - 1:
            y += 26
    body_bottom = y - lh + body_size  # bottom of last line's ink approx
    assert body_bottom <= BODY_BOTTOM_MAX, "body overflows its box"

    # RSVP band: the structural punchline, tinted + stamped.
    band_y = body_bottom + 22
    band_h = 112
    d.rounded_rectangle([MARGIN, band_y, W - MARGIN, band_y + band_h],
                        radius=10, fill=BLUSH, outline=RED, width=2)
    box = 34
    bx, by = MARGIN + 22, band_y + (band_h - box) // 2
    d.rectangle([bx, by, bx + box, by + box], outline=RED_DARK, width=3)
    draw_check(d, bx, by, box, RED, width=4)
    tx = bx + box + 18
    d.text((tx, band_y + 14), RSVP_1, font=font(SANS_B, body_size + 2),
           fill=RED_DARK)
    d.text((tx, band_y + 60), RSVP_2, font=font(SANS, body_size - 2),
           fill=INK)
    for line, fnt in ((RSVP_1, font(SANS_B, body_size + 2)),
                      (RSVP_2, font(SANS, body_size - 2))):
        assert d.textlength(line, font=fnt) <= TEXT_W - (tx - MARGIN) - 90, \
            "RSVP line overflows its band: %r" % line

    # Wax seal stamped on the RSVP band's right end.
    draw_seal(d, W - MARGIN - 42, band_y + band_h // 2, 32)

    # Bottom row: P.S. (left, with chair icon) + signature (right).
    # Both at 34px so the two never touch (asserted below).
    bottom_y = band_y + band_h + 30
    draw_chair(d, MARGIN, bottom_y + 32, BROWN)
    ps_fnt = font(SANS, 34)
    d.text((MARGIN + 44, bottom_y), PS, font=ps_fnt, fill=INK)
    sign_fnt = font(SERIF, 34)
    sign_x = W - MARGIN - d.textlength(SIGN, font=sign_fnt)
    assert MARGIN + 44 + d.textlength(PS, font=ps_fnt) + 24 <= sign_x, \
        "P.S. and signature collide"
    d.text((sign_x, bottom_y), SIGN, font=sign_fnt, fill=INK)
    assert bottom_y + 34 <= H - 52, "bottom row collides with border"

    img.save(OUT, "PNG", optimize=True)
    data = open(OUT, "rb").read()
    assert len(data) <= 1048576, "PNG over 1 MiB: %d" % len(data)
    assert Image.open(OUT).size == (1024, 1024), "wrong dimensions"
    print("wrote %s (%d bytes, 1024x1024)" % (OUT, len(data)))
    print("sha256:", hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    sys.exit(main())
