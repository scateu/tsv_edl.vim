#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tsv2fcpxml2 - convert a tsv_edl stream into a Final Cut Pro X FCPXML 1.11 document.

This is a from-scratch rewrite of tsv2fcpxml.py that targets the current FCPXML
spec (version 1.11), uses exact per-fps rational time (no frame drift), escapes
all XML text, and builds the document with a structured tree instead of string
concatenation.

Input (one clip per line, tab separated; lines not starting with EDL are ignored):

    EDL <TAB> HH:MM:SS,mmm <TAB> HH:MM:SS,mmm <TAB> | clipname | <TAB> subtitle

Conventions carried over from the tsv_edl workflow:
    - `\\N` in a subtitle is a line break.
    - `[ SPACE ... ]` and `[B]...` subtitles are excluded from the .srt sidecar.
    - `[B]text`  marks a B-roll clip, composited on a lane above the storyline.
    - clipname (no extension) is matched to a file on disk via glob.

Usage:
    cat selection.tsv | tsv2fcpxml2 --fps 25 > out.fcpxml
"""
from __future__ import annotations

import argparse
import glob
import math
import os
import sys
import urllib.parse
from fractions import Fraction
from xml.etree import ElementTree as ET
from xml.dom import minidom

FCPXML_VERSION = "1.11"

VIDEO_FORMATS = ("mkv", "mp4", "mov", "mpeg", "ts", "avi", "webm")
AUDIO_FORMATS = ("wav", "mp3", "m4a", "ogg", "flac")
IMAGE_FORMATS = ("png", "jpg", "jpeg", "bmp")

# 10-hour ceiling for a source asset. FCP does not care, but DaVinci Resolve
# ignores a source tape beyond ~10 hours, so keep media_duration bounded.
MEDIA_DURATION_SECONDS = 36000

# Exact FCP frame durations and the predefined 1080p format name for each rate.
# Keyed by the fps value rounded to 2 decimals so 23.976 / 29.97 / 59.94 match.
#   fps: (frameDuration_num, frameDuration_den, FFVideoFormat name)
FRAME_RATES = {
    23.98: (1001, 24000, "FFVideoFormat1080p2398"),
    24.0:  (100, 2400, "FFVideoFormat1080p24"),
    25.0:  (100, 2500, "FFVideoFormat1080p25"),
    29.97: (1001, 30000, "FFVideoFormat1080p2997"),
    30.0:  (100, 3000, "FFVideoFormat1080p30"),
    50.0:  (100, 5000, "FFVideoFormat1080p50"),
    59.94: (1001, 60000, "FFVideoFormat1080p5994"),
    60.0:  (100, 6000, "FFVideoFormat1080p60"),
}


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


class Timebase:
    """Maps timecodes to frame-aligned rational time in a single sequence timescale.

    All timeline values are integer multiples of one frame duration, expressed
    over a shared timescale, so every offset/duration snaps exactly to a frame.
    """

    def __init__(self, fps: float):
        key = round(fps, 2)
        if key not in FRAME_RATES:
            # Fall back to an exact rational for an arbitrary rate; use a generic
            # format name so FCP still parses it (it treats unknown names as custom).
            num, den = 1000, int(round(fps * 1000))
            self.format_name = "FFVideoFormat1080p%g" % fps
            eprint("WARNING: non-standard fps %g; using frameDuration %d/%ds." % (fps, num, den))
        else:
            num, den, self.format_name = FRAME_RATES[key]
        self.fps = fps
        # One frame as a Fraction of a second.
        self.frame = Fraction(num, den)
        # Sequence timescale = frame duration denominator; each frame is `num` units.
        self.timescale = den
        self.frame_units = num  # units per frame

    def frame_duration_str(self) -> str:
        return "%d/%ds" % (self.frame_units, self.timescale)

    def timecode_to_frames(self, timecode: str) -> int:
        """HH:MM:SS,mmm (or with ':' ms separator) -> nearest whole frame index."""
        tc = timecode.strip().strip('"').replace(",", ":")
        parts = tc.split(":")
        if len(parts) != 4:
            raise ValueError("bad timecode %r" % timecode)
        h, m, s, ms = (int(p) for p in parts)
        seconds = Fraction(h * 3600 + m * 60 + s) + Fraction(ms, 1000)
        return int(round(seconds / self.frame))

    def frames_to_units(self, frames: int) -> int:
        return frames * self.frame_units

    def units_to_seconds(self, units: int) -> float:
        return units / self.timescale

    def time_str(self, units: int) -> str:
        if units == 0:
            return "0s"
        return "%d/%ds" % (units, self.timescale)


def sec_to_srttime(sec: float) -> str:
    hh = int(sec // 3600)
    mm = int((sec - 3600 * hh) // 60)
    ss = int(sec - hh * 3600 - mm * 60)
    ms = int(round((sec - int(sec)) * 1000))
    if ms == 1000:  # guard rounding up into the next second
        ms = 0
        ss += 1
    return "%02d:%02d:%02d,%03d" % (hh, mm, ss, ms)


def classify_extension(path: str) -> str:
    ext = os.path.splitext(path)[1][1:].lower()
    if ext in VIDEO_FORMATS:
        return "video"
    if ext in AUDIO_FORMATS:
        return "audio"
    if ext in IMAGE_FORMATS:
        return "image"
    return ""


def determine_file_for_clipname(clipname: str) -> dict:
    """Glob the working directory for a file matching clipname.

    Preference order: video > audio > image. Returns a dict describing the asset.
    """
    matches = glob.glob("*%s*" % clipname)
    by_kind = {"video": [], "audio": [], "image": []}
    for m in matches:
        kind = classify_extension(m)
        if kind:
            by_kind[kind].append(m)

    for kind in ("video", "audio", "image"):
        files = by_kind[kind]
        if not files:
            continue
        if len(files) > 1:
            eprint('WARNING: multiple files match clip "%s"; choosing %s' % (clipname, files[0]))
        filename = files[0]
        abspath = os.path.abspath(filename)
        if kind == "video":
            return dict(abspath=abspath, has_video=1, has_audio=1,
                        media_duration=MEDIA_DURATION_SECONDS, is_still=False)
        if kind == "audio":
            return dict(abspath=abspath, has_video=0, has_audio=1,
                        media_duration=MEDIA_DURATION_SECONDS, is_still=False)
        # image / still picture
        return dict(abspath=abspath, has_video=1, has_audio=0,
                    media_duration=0, is_still=True)

    eprint('WARNING: no file matches clip "%s"; emitting placeholder.' % clipname)
    return dict(abspath=clipname, has_video=1, has_audio=1,
                media_duration=MEDIA_DURATION_SECONDS, is_still=False)


class Clip:
    """A single timeline clip in sequence units."""

    __slots__ = ("clipname", "ref_id", "offset", "start", "duration", "lane", "subtitle")

    def __init__(self, clipname, ref_id, offset, start, duration, lane, subtitle):
        self.clipname = clipname
        self.ref_id = ref_id
        self.offset = offset      # position in the sequence (units)
        self.start = start        # source in-point (units)
        self.duration = duration  # length (units)
        self.lane = lane
        self.subtitle = subtitle

    def as_tuple(self):
        return (self.clipname, self.ref_id, self.offset, self.start,
                self.duration, self.lane, self.subtitle)


def parse_tsv(stream, tb: Timebase, offset_one_hour: bool, generate_srt: bool):
    """Read the tsv_edl stream and return (media_assets, a_queue, b_queue, srt_queue)."""
    media_assets = {}   # clipname -> dict(ref_id, abspath, has_video, has_audio, media_duration, is_still)
    a_queue = []        # primary storyline clips
    b_queue = []        # B-roll clips (lane assigned later)
    srt_queue = []
    srt_counter = 1
    offset = 0          # running sequence position for primary storyline (units)
    one_hour_units = tb.frames_to_units(tb.timecode_to_frames("01:00:00,000")) if offset_one_hour else 0

    for line in stream:
        if not line.startswith("EDL"):
            continue
        stripped = line.rstrip("\n")
        if "|" not in stripped:
            continue

        items = stripped.split("|")
        clipname = items[1].strip()
        subtitle = items[2].strip() if len(items) > 2 else ""

        if clipname not in media_assets:
            ref_id = "r%d" % (len(media_assets) + 2)  # r1 is the sequence format
            info = determine_file_for_clipname(clipname)
            info["ref_id"] = ref_id
            media_assets[clipname] = info
        info = media_assets[clipname]
        ref_id = info["ref_id"]

        tc = items[0].split()  # ['EDL', 'HH:MM:SS,mmm', 'HH:MM:SS,mmm']
        record_in = tb.frames_to_units(tb.timecode_to_frames(tc[1]))
        record_out = tb.frames_to_units(tb.timecode_to_frames(tc[2]))
        duration = record_out - record_in
        if duration <= 0:  # zero/negative-length clip: keep one frame so FCP is happy
            duration = tb.frame_units
        start = record_in + one_hour_units

        is_broll = subtitle.startswith("[B]")

        if generate_srt and subtitle and "[ SPACE" not in subtitle and not is_broll:
            srt_in = sec_to_srttime(tb.units_to_seconds(offset))
            srt_out = sec_to_srttime(tb.units_to_seconds(offset + duration))
            srt_queue.append(str(srt_counter))
            srt_queue.append("%s --> %s" % (srt_in, srt_out))
            srt_queue.append(subtitle.replace("\\N", "\n"))
            srt_queue.append("")
            srt_counter += 1

        if is_broll:
            # lane assigned after the whole stream is read (needs full context)
            b_queue.append(Clip(clipname, ref_id, offset, start, duration, 1, subtitle))
        else:
            a_queue.append(Clip(clipname, ref_id, offset, start, duration, 0, subtitle))
            offset += duration

    return media_assets, a_queue, b_queue, srt_queue


def stitch(queue):
    """Merge runs of adjacent same-source clips whose source ranges are contiguous."""
    if not queue:
        return []
    out = []
    i = 0
    n = len(queue)
    while i < n:
        cur = queue[i]
        clipname, ref, offset, start, duration, lane, subtitle = cur.as_tuple()
        j = i + 1
        while j < n:
            nxt = queue[j]
            if (nxt.clipname == clipname and nxt.ref_id == ref
                    and nxt.lane == lane and start + duration == nxt.start):
                duration += nxt.duration
                subtitle = subtitle + "\n" + nxt.subtitle
                j += 1
            else:
                break
        out.append(Clip(clipname, ref, offset, start, duration, lane, subtitle))
        i = j
    return out


def assign_broll_lanes(b_queue):
    """Assign each B-roll clip the lowest positive lane that does not overlap."""
    lane_ends = {}  # lane -> end offset of the last clip placed on it
    for clip in b_queue:
        lane = 1
        while lane in lane_ends and clip.offset < lane_ends[lane]:
            lane += 1
        clip.lane = lane
        lane_ends[lane] = clip.offset + clip.duration
    return b_queue


def take_broll_for(a_clip, b_queue):
    """Return (nested B clips whose offset falls within a_clip, remaining B queue)."""
    a_start, a_end = a_clip.offset, a_clip.offset + a_clip.duration
    nested, rest = [], []
    for b in b_queue:
        if a_start <= b.offset < a_end:
            nested.append(b)
        else:
            rest.append(b)
    return nested, rest


def build_media_element(tag, clip, tb, is_still, nested_offset=None, audio_role=None):
    """Create a <video>/<asset-clip> element for a timeline clip."""
    el = ET.Element(tag)
    el.set("ref", clip.ref_id)
    el.set("name", clip.clipname)
    el.set("offset", tb.time_str(clip.offset if nested_offset is None else nested_offset))
    el.set("start", tb.time_str(clip.start))
    el.set("duration", tb.time_str(clip.duration))
    if clip.lane:
        el.set("lane", str(clip.lane))
    if audio_role and not is_still:
        el.set("audioRole", audio_role)
    return el


def add_annotations(el, clip):
    """Attach a <note> carrying the subtitle text (minus the [B] marker)."""
    subtitle = clip.subtitle
    if subtitle.startswith("[B]"):
        subtitle = subtitle[3:].strip()
    if subtitle:
        note = ET.SubElement(el, "note")
        note.text = subtitle


def build_fcpxml(media_assets, a_queue, b_queue, tb, audio_role="dialogue"):
    fcpxml = ET.Element("fcpxml", version=FCPXML_VERSION)
    resources = ET.SubElement(fcpxml, "resources")

    fmt = ET.SubElement(resources, "format")
    fmt.set("id", "r1")
    fmt.set("name", tb.format_name)
    fmt.set("frameDuration", tb.frame_duration_str())
    fmt.set("width", "1920")
    fmt.set("height", "1080")
    fmt.set("colorSpace", "1-1-1 (Rec. 709)")

    for clipname, info in media_assets.items():
        asset = ET.SubElement(resources, "asset")
        asset.set("id", info["ref_id"])
        asset.set("name", clipname)
        asset.set("start", "0s")
        asset.set("duration", "%ds" % info["media_duration"])
        asset.set("hasVideo", str(info["has_video"]))
        asset.set("hasAudio", str(info["has_audio"]))
        asset.set("format", "r1")
        if info["has_audio"]:
            asset.set("audioSources", "1")
            asset.set("audioChannels", "2")
            asset.set("audioRate", "48000")
        src = "file://" + urllib.parse.quote(info["abspath"])
        media_rep = ET.SubElement(asset, "media-rep")
        media_rep.set("kind", "original-media")
        media_rep.set("src", src)

    total_units = sum(c.duration for c in a_queue) if a_queue else 0

    library = ET.SubElement(fcpxml, "library")
    event = ET.SubElement(library, "event", name="DEFAULT")
    project = ET.SubElement(event, "project", name="DEFAULT")
    sequence = ET.SubElement(project, "sequence")
    sequence.set("format", "r1")
    sequence.set("duration", tb.time_str(total_units))
    sequence.set("tcStart", "0s")
    sequence.set("tcFormat", "NDF")
    sequence.set("audioLayout", "stereo")
    sequence.set("audioRate", "48k")
    spine = ET.SubElement(sequence, "spine")

    remaining_b = list(b_queue)
    for a_clip in a_queue:
        is_still = media_assets[a_clip.clipname]["is_still"]
        tag = "video" if is_still else "asset-clip"
        el = build_media_element(tag, a_clip, tb, is_still, audio_role=audio_role)
        spine.append(el)
        add_annotations(el, a_clip)

        nested, remaining_b = take_broll_for(a_clip, remaining_b)
        for b in nested:
            b_still = media_assets[b.clipname]["is_still"]
            b_tag = "video" if b_still else "asset-clip"
            # B-roll offset is relative to the parent clip's timeline position,
            # shifted by the parent's source start (record_in), per FCPXML nesting.
            nested_offset = b.offset + a_clip.start - a_clip.offset
            b_el = build_media_element(b_tag, b, tb, b_still,
                                       nested_offset=nested_offset, audio_role=audio_role)
            el.append(b_el)
            add_annotations(b_el, b)

    if remaining_b:
        eprint("WARNING: %d B-roll clip(s) did not fall within any A clip and were dropped."
               % len(remaining_b))

    return fcpxml


def serialize(fcpxml) -> str:
    rough = ET.tostring(fcpxml, encoding="unicode")
    pretty = minidom.parseString(rough).toprettyxml(indent="    ")
    # minidom emits its own <?xml?>; replace it with the DOCTYPE-bearing header FCP expects.
    body = pretty.split("\n", 1)[1]
    header = '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE fcpxml>\n'
    # drop blank lines minidom leaves between elements
    body = "\n".join(l for l in body.splitlines() if l.strip())
    return header + body + "\n"


def main():
    parser = argparse.ArgumentParser(description="convert tsv_edl to FCPXML 1.11")
    parser.add_argument("--fps", type=float, default=25,
                        help="sequence frame rate (default 25)")
    parser.add_argument("--offsetonehour", action="store_true", default=False,
                        help="shift source timecodes by 1h (DaVinci Resolve friendly)")
    parser.add_argument("--nosrt", dest="generate_srt", action="store_false", default=True,
                        help="do not write the fcpxml.srt sidecar")
    parser.add_argument("--srt-name", default="fcpxml.srt",
                        help="filename for the srt sidecar (default fcpxml.srt)")
    args = parser.parse_args()

    tb = Timebase(args.fps)
    eprint("Be advised: %.3f FPS, 48000 Hz, FCPXML %s." % (args.fps, FCPXML_VERSION))
    if args.offsetonehour:
        eprint("OFFSET_1HOUR: timecodes shifted by 1 hour (DaVinci Resolve friendly).")

    media_assets, a_queue, b_queue, srt_queue = parse_tsv(
        sys.stdin, tb, args.offsetonehour, args.generate_srt)

    if len(a_queue) > 99999 or len(b_queue) > 99999:
        eprint("Too much. That's too much.")
        sys.exit(1)

    before_a = len(a_queue)
    a_queue = stitch(a_queue)
    eprint("[stitch] %d --> %d lines" % (before_a, len(a_queue)))
    if b_queue:
        before_b = len(b_queue)
        b_queue = stitch(b_queue)
        eprint("[stitch B] %d --> %d lines" % (before_b, len(b_queue)))
        assign_broll_lanes(b_queue)

    any_pure_audio = any(a["has_video"] == 0 for a in media_assets.values())
    if any_pure_audio:
        eprint("NOTE: some assets have hasVideo=0. For a DaVinci Resolve multicam import "
               "you may need to set hasVideo=1 manually.")

    fcpxml = build_fcpxml(media_assets, a_queue, b_queue, tb)
    sys.stdout.write(serialize(fcpxml))

    if args.generate_srt and srt_queue:
        eprint("[srt] writing %s" % args.srt_name)
        with open(args.srt_name, "w", encoding="utf-8") as f:
            f.write("\n".join(srt_queue))


if __name__ == "__main__":
    main()
