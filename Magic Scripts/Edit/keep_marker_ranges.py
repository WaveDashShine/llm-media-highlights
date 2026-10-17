# MagicScript script: rebuild the current timeline into a NEW one containing ONLY the ranges
# covered by markers of the chosen colour(s) — the inverse of cut_red_marker_ranges.
#
# Video and audio are rebuilt as pool-clip pieces placed at their exact compressed positions
# (AppendToTimeline's recordFrame + a trackIndex per selected source track), so no grades,
# titles, transitions or Fusion come across. Stills are trimmed to the marked span like any
# other clip; other track types would be left out. Subtitle items have no media pool item and
# no import API, so they are recreated as ordinary captions from the new timeline's audio.

import time

MARKER_COLOURS = ["Blue", "Cyan", "Green", "Yellow", "Red", "Pink", "Purple", "Fuchsia",
                  "Rose", "Lavender", "Sky", "Mint", "Lemon", "Sand", "Cocoa", "Cream"]
LANGS = ["Auto", "English", "Danish", "Dutch", "Finnish", "French", "German", "Hindi", "Indonesian", "Italian",
         "Japanese", "Korean", "Malay", "Mandarin Simplified", "Mandarin Traditional", "Norwegian", "Polish",
         "Portuguese", "Romanian", "Russian", "Spanish", "Swedish", "Tamil", "Thai", "Turkish", "Vietnamese"]

MANIFEST = {
    "id": "keep_marker_ranges",
    "name": "Keep only marker ranges",
    "category": "Edit",
    "keywords": "keep marked ranges only colour selects inverse cut out segments tracks audio captions",
    "needs": "timeline",
    "source": "AI-authored 2026-10-17 for Erik, from cut_red_marker_ranges",
    "description": (
        "Rebuilds the current timeline on a NEW one keeping only footage covered by ranged markers of "
        "the chosen colour(s), on the selected video and audio tracks."
    ),
    "warning": (
        "Rebuilt from pool clips: no grades, titles, transitions or Fusion are carried. Captions are "
        "recreated from the new audio, not copied. Retimed clips under a marked range stop the run."
    ),
    "variables": [
        {"id": "colours", "label": "Marker colours (blank = all, comma-separated list)", "type": "text",
         "default": "", "pick": False,
         "help": "Any of: Blue, Cyan, Green, Yellow, Red, Pink, Purple, Fuchsia, Rose, Lavender, "
                 "Sky, Mint, Lemon, Sand, Cocoa, Cream. Example: Red, Green"},
        {"id": "min_duration", "label": "Ignore markers shorter than (frames)", "type": "int", "default": 2, "min": 1, "max": 1000},
        {"id": "video_tracks", "label": "Video tracks (blank = all)", "type": "text", "default": "",
         "help": "Comma-separated numbers, e.g. 1,3. Blank keeps every video track."},
        {"id": "audio_tracks", "label": "Audio tracks (blank = all)", "type": "text", "default": "",
         "help": "Comma-separated numbers, e.g. 2,4. Blank keeps every audio track."},
        {"id": "recreate_captions", "label": "Recreate captions from the new audio", "type": "bool", "default": True,
         "help": "Source subtitle tracks cannot be rebuilt directly; this redoes them via transcription."},
        {"id": "caption_language", "label": "Caption language", "type": "choice", "default": "Auto", "choices": LANGS},
        {"id": "timeline_name", "label": "New timeline name (blank = <name>_marked)", "type": "text", "default": "", "pick": False},
    ],
}


def _const(resolve, name):
    key = "AUTO_CAPTION_" + name.upper().replace(" ", "_")
    if not hasattr(resolve, key):
        raise ValueError(f"This Resolve has no constant {key}")
    return getattr(resolve, key)


def run(ctx):
    L, v, R = ctx.lib, ctx.vars, ctx.resolve
    src = ctx.require_timeline()
    mp = ctx.media_pool
    t0 = src.GetStartFrame()
    name = (v.get("timeline_name") or "").strip() or src.GetName() + "_marked"
    name = L.unique_timeline_name(ctx.project, name)

    wanted = [c.strip() for c in (v.get("colours") or "").split(",") if c.strip()]
    canon = {c.lower(): c for c in MARKER_COLOURS}
    chosen = {canon[c.lower()] for c in wanted if c.lower() in canon}
    unknown = [c for c in wanted if c.lower() not in canon]
    if unknown:
        ctx.log("  unknown colour names ignored: " + ", ".join(unknown))

    # Markers are keyed relative to the timeline start; all subtraction below is in relative frames.
    marks = sorted((f, f + m.get("duration", 0)) for f, m in (src.GetMarkers() or {}).items()
                   if (not chosen or m.get("color") in chosen)
                   and m.get("duration", 0) >= int(v.get("min_duration") or 2))
    if not marks:
        which = " of " + ", ".join(sorted(chosen)) if chosen else ""
        return f"No ranged markers{which} on '{src.GetName()}'; nothing created"
    ranges = []
    for s0, s1 in marks:                       # merge overlapping/touching ranges: one span,
        if ranges and s0 <= ranges[-1][1]:     # so no frames land in the plan twice
            ranges[-1][1] = max(ranges[-1][1], s1)
        else:
            ranges.append([s0, s1])
    ctx.log(f"{len(marks)} marker range(s) -> {len(ranges)} kept span(s) "
            f"(colours: {', '.join(sorted(chosen)) or 'all'}): {ranges}")

    tl_fps = L.timeline_fps(src)
    spans = []                                 # (start, end, compressed offset) per kept span
    base = 0
    for s0, s1 in ranges:
        spans.append((s0, s1, base))
        base += s1 - s0

    def pieces(i, kind, dest, src_t):
        a, b = i.GetStart() - t0, i.GetEnd() - t0
        m = i.GetMediaPoolItem()
        try:
            ratio = float(m.GetClipProperty("FPS")) / tl_fps   # timeline frames -> source frames
        except Exception:
            ratio = 1.0
        if (i.GetSpeed() or {}).get("Percentage") not in (100, 100.0):
            raise ValueError(f"'{i.GetName()}' on {kind}{src_t} is retimed under a marked range; stop (its source maths would be wrong)")
        out = []
        for S, E, B in spans:
            k0, k1 = max(a, S), min(b, E)
            if k0 >= k1:                       # footage outside every marked span never reaches the new timeline
                continue
            s = i.GetSourceStartFrame() + int(round((k0 - a) * ratio))
            out.append({"trackIndex": dest, "mediaPoolItem": m,
                        "startFrame": s, "endFrame": s + int(round((k1 - k0) * ratio)),
                        "recordFrame": B + (k0 - S)})    # compressed position, made absolute after creation
        return out

    def build(kind, var):
        count = src.GetTrackCount(kind) or 0
        picked = [t for t in (L.parse_int_list(v.get(var)) or []) if 1 <= t <= count]
        plan = []
        for dest, t in enumerate(picked or list(range(1, count + 1)), 1):   # selection compacts onto new 1..k
            unpooled = 0
            for i in (src.GetItemListInTrack(kind, t) or []):
                m = i.GetMediaPoolItem()
                if m is None:                  # titles/generators have no source range to rebuild from
                    unpooled += 1
                    continue
                plan.extend(pieces(i, kind, dest, t))
            if picked:
                ctx.log(f"  {kind}{t} -> {kind}{dest}" + (f" ({unpooled} overlay item(s) not carried)" if unpooled else ""))
        return plan

    plan = build("video", "video_tracks") + build("audio", "audio_tracks")
    if not plan:
        raise ValueError("No clip footage inside the marker ranges on the selected tracks; nothing to keep")

    mp.SetCurrentFolder(mp.GetRootFolder())
    out = mp.CreateEmptyTimeline(name)
    if not out:
        raise RuntimeError(f"CreateEmptyTimeline('{name}') failed")
    g0 = out.GetStartFrame()
    for p in plan:
        p["recordFrame"] = g0 + p["recordFrame"]   # recordFrame is counted in absolute project frames
    need = max(p["trackIndex"] for p in plan)  # kinds share one numbering; a video piece's
    for kind in ("video", "audio"):            # embedded audio pairs onto the same audio track
        have = out.GetTrackCount(kind) or 0
        for _ in range(max(0, need - have)):
            if out.AddTrack(kind) is not True:
                ctx.log(f"  AddTrack {kind} returned not-True (continuing anyway)")

    got = mp.AppendToTimeline(plan) or []
    for kind in ("video", "audio"):
        ctx.log(f"  new timeline {kind} tracks: {out.GetTrackCount(kind)}")
    before = src.GetEndFrame() - src.GetStartFrame()
    marked = sum(s1 - s0 for s0, s1 in ranges)

    created_subs = 0
    if v.get("recreate_captions") and (src.GetTrackCount("subtitle") or 0) > 0:
        settings = {"language": _const(R, v.get("caption_language") or "Auto"),
                    "captionPreset": R.AUTO_CAPTION_SUBTITLE_DEFAULT}
        ok = out.CreateSubtitlesFromAudio(settings)
        if ok is not True:                     # first AI call after heavy work can fail once
            time.sleep(3)
            ok = out.CreateSubtitlesFromAudio(settings)
        if ok is True:
            st = out.GetTrackCount("subtitle") or 0
            created_subs = len(out.GetItemListInTrack("subtitle", st) or [])
            ctx.log(f"  captions recreated: {created_subs} cue(s)")
        else:
            ctx.log(f"  CreateSubtitlesFromAudio returned {ok!r}; no captions created")
    else:
        ctx.log("  caption recreation off; source subtitle tracks are not carried")

    ctx.save()
    return (f"'{name}': {len(got)}/{len(plan)} pieces placed at their compressed positions, "
            f"{marked} of {before} timeline frames marked"
            + (f", {created_subs} cue(s) recreated" if created_subs else ""))
