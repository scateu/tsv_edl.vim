#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fcpxml2tsv - convert an FCPXML document back into a tsv_edl stream.

Reverse of tsv2fcpxml2.py. Reads an FCPXML file (path argument or stdin) and
prints tsv_edl lines to stdout:

    EDL <TAB> HH:MM:SS,mmm <TAB> HH:MM:SS,mmm <TAB> | clipname | <TAB> subtitle

Rules:
    - The two timecodes are the clip's source in-point (`start`) and out-point
      (`start` + `duration`) -- these round-trip with tsv2fcpxml2.
    - clipname is the referenced <asset> name, falling back to the basename of
      its media-rep `src`. Media files are assumed to live in the same directory.
    - Any story element anchored to another (a nested clip carrying a `lane`
      attribute) is a place-on-top clip; it is emitted as a B-roll line whose
      subtitle is prefixed with `[B]`. This works for plain video, pure video,
      and pure audio clips alike -- they are all asset-clip / video elements.
    - `<note>` text becomes the subtitle (newlines -> `\\N`).

This converter models only the subset tsv2fcpxml2 emits: a single sequence with
a spine of asset-clip / video elements, optionally with nested lane clips.
Constructs it does not understand (transitions, effects, adjust-*, gaps, time
maps, compound / multicam / sync clips) are skipped with a warning on stderr.
If the document has no parseable sequence at all, it reports an error and aborts.

Usage:
    fcpxml2tsv project.fcpxml > project.tsv
    cat project.fcpxml | fcpxml2tsv > project.tsv
"""
from __future__ import annotations

import os
import sys
import urllib.parse
from fractions import Fraction
from xml.etree import ElementTree as ET

# Story elements we know how to turn into an EDL line.
CLIP_TAGS = ("asset-clip", "video", "clip", "ref-clip")
# Anchored/nested elements we skip (not place-on-top media we can represent).
SKIP_TAGS = ("transition", "gap", "audio", "caption", "spine")


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def die(msg: str):
    eprint("ERROR: " + msg)
    sys.exit(1)


def parse_time(value: str) -> Fraction:
    """Parse an FCPXML rational time ("N/Ds" or "Ns" or "0s") into seconds."""
    if value is None:
        return Fraction(0)
    v = value.strip()
    if v.endswith("s"):
        v = v[:-1]
    if v == "" or v == "0":
        return Fraction(0)
    if "/" in v:
        num, den = v.split("/", 1)
        return Fraction(int(num), int(den))
    return Fraction(v)


def seconds_to_timecode(seconds: Fraction) -> str:
    """Fraction of seconds -> HH:MM:SS,mmm (millisecond precision, rounded)."""
    if seconds < 0:
        seconds = Fraction(0)
    total_ms = int(round(float(seconds) * 1000))
    ms = total_ms % 1000
    total_s = total_ms // 1000
    ss = total_s % 60
    mm = (total_s // 60) % 60
    hh = total_s // 3600
    return "%02d:%02d:%02d,%03d" % (hh, mm, ss, ms)


def strip_ns(tag: str) -> str:
    """Drop any XML namespace prefix (FCPXML has none, but be safe)."""
    return tag.split("}", 1)[1] if "}" in tag else tag


def build_asset_index(resources) -> dict:
    """Map resource id -> clipname (asset name, fallback to media-rep src basename)."""
    index = {}
    if resources is None:
        return index
    for el in resources:
        tag = strip_ns(el.tag)
        if tag not in ("asset", "media"):
            continue
        rid = el.get("id")
        if not rid:
            continue
        name = el.get("name")
        if not name:
            name = src_basename(el)
        index[rid] = name or rid
    return index


def src_basename(asset_el) -> str:
    """Basename (no extension) of an asset's media-rep src, url-decoded."""
    for child in asset_el:
        if strip_ns(child.tag) == "media-rep":
            src = child.get("src") or ""
            if src.startswith("file://"):
                src = src[len("file://"):]
            src = urllib.parse.unquote(src)
            base = os.path.basename(src.rstrip("/"))
            return os.path.splitext(base)[0]
    return ""


def get_note(el) -> str:
    """First <note> child's text, with newlines encoded as \\N. '' if none."""
    for child in el:
        if strip_ns(child.tag) == "note":
            text = (child.text or "").strip()
            return text.replace("\n", "\\N")
    return ""


def find_sequence(root):
    """Locate the single <sequence>. Abort if there is not exactly one usable one."""
    sequences = [el for el in root.iter() if strip_ns(el.tag) == "sequence"]
    if not sequences:
        die("no <sequence> found in FCPXML; nothing to convert.")
    if len(sequences) > 1:
        eprint("WARNING: %d sequences found; converting the first only." % len(sequences))
    return sequences[0]


def format_for_sequence(root, sequence):
    """Return (frameDuration string, frame duration in seconds) for the sequence."""
    fmt_id = sequence.get("format")
    for el in root.iter():
        if strip_ns(el.tag) == "format" and el.get("id") == fmt_id:
            fd = el.get("frameDuration")
            if fd:
                return fd, parse_time(fd)
    return None, Fraction(0)


def emit_clip(el, assets, is_broll, out):
    """Turn one clip element into an EDL line and append it to `out`."""
    tag = strip_ns(el.tag)
    ref = el.get("ref")
    clipname = assets.get(ref) or el.get("name") or ref or "MISSING"

    start = parse_time(el.get("start"))
    duration = parse_time(el.get("duration"))
    tc_in = seconds_to_timecode(start)
    tc_out = seconds_to_timecode(start + duration)

    subtitle = get_note(el)
    if is_broll:
        subtitle = "[B]" + subtitle

    out.append("EDL\t%s\t%s\t| %s |\t%s" % (tc_in, tc_out, clipname, subtitle))


def walk_spine(spine, assets, out):
    """Emit primary-storyline clips, then their nested lane clips as [B] lines."""
    for el in spine:
        tag = strip_ns(el.tag)
        if tag in SKIP_TAGS:
            if tag != "spine":
                eprint("NOTE: skipping unmodeled <%s> in spine." % tag)
            continue
        if tag not in CLIP_TAGS:
            eprint("NOTE: skipping unknown story element <%s>." % tag)
            continue

        emit_clip(el, assets, is_broll=False, out=out)

        # Nested children with a `lane` attribute are place-on-top (B-roll).
        for child in el:
            ctag = strip_ns(child.tag)
            if ctag in ("note", "marker", "chapter-marker", "keyword", "rating"):
                continue
            if ctag not in CLIP_TAGS:
                if ctag not in ("adjust-volume",) and not ctag.startswith("adjust-"):
                    eprint("NOTE: skipping nested <%s>." % ctag)
                continue
            if child.get("lane"):
                emit_clip(child, assets, is_broll=True, out=out)
            else:
                # A contained clip without a lane (e.g. sync-clip content); emit
                # as B-roll too since it composites with the parent.
                emit_clip(child, assets, is_broll=True, out=out)


def main():
    args = sys.argv[1:]
    if args and args[0] in ("-h", "--help"):
        print(__doc__)
        return
    path = args[0] if args else None

    try:
        if path:
            tree = ET.parse(path)
            root = tree.getroot()
        else:
            data = sys.stdin.read()
            if not data.strip():
                die("empty input on stdin.")
            root = ET.fromstring(data)
    except ET.ParseError as e:
        die("could not parse FCPXML: %s" % e)
    except (OSError, IOError) as e:
        die("could not read %s: %s" % (path, e))

    if strip_ns(root.tag) != "fcpxml":
        die("root element is <%s>, not <fcpxml>." % strip_ns(root.tag))

    resources = None
    for el in root:
        if strip_ns(el.tag) == "resources":
            resources = el
            break
    assets = build_asset_index(resources)

    sequence = find_sequence(root)
    fd_str, frame = format_for_sequence(root, sequence)
    if frame:
        eprint("Be advised: frameDuration %s (~%.3f fps)." % (fd_str, 1.0 / float(frame)))

    spine = None
    for el in sequence:
        if strip_ns(el.tag) == "spine":
            spine = el
            break
    if spine is None:
        die("sequence has no <spine>; nothing to convert.")

    out = []
    walk_spine(spine, assets, out)

    if not out:
        die("no convertible clips found in spine.")

    sys.stdout.write("\n".join(out) + "\n")
    eprint("[fcpxml2tsv] wrote %d EDL line(s)." % len(out))


if __name__ == "__main__":
    main()
