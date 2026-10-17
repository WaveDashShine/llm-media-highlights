# MagicScript script: a marker CSV with start and end timecode columns -> one marker per row, spanning start to end.

MARKER_COLOURS = ["Blue", "Cyan", "Green", "Yellow", "Red", "Pink", "Purple", "Fuchsia",
                  "Rose", "Lavender", "Sky", "Mint", "Lemon", "Sand", "Cocoa", "Cream"]

MANIFEST = {
    "id": "markers_from_csv_pairs",
    "name": "Spanning markers from a CSV",
    "category": "Markers & QC",
    "keywords": "markers csv start end range span import notes",
    "needs": "timeline",
    # No delete calls: an occupied frame is reported and skipped, never removed.
    "source": "AI-authored 2026-10-17 for Erik, from markers_from_csv",
    "description": "Adds one marker per CSV row, spanning its start timecode to its end "
                   "timecode. Rows outside the timeline are skipped and reported.",
    "warning": "Timecodes are read as non-drop, so drop-frame (;) values land early.",
    "save_first": True,
    "variables": [
        {"id": "csv_path", "label": "CSV file", "type": "text", "default": "~/Desktop/notes.csv"},
        {"id": "start_col", "label": "Start timecode column", "type": "text", "default": "start"},
        {"id": "end_col", "label": "End timecode column (blank = 1-frame marker)", "type": "text", "default": "end"},
        {"id": "color_col", "label": "Colour column (blank = default colour)", "type": "text", "default": "colour"},
        {"id": "name_col", "label": "Name column", "type": "text", "default": "name"},
        {"id": "note_col", "label": "Note column", "type": "text", "default": "note"},
        {"id": "default_color", "label": "Default marker colour", "type": "choice", "default": "Blue", "choices": MARKER_COLOURS},
        {"id": "tc_base", "label": "Timecodes in the CSV are", "type": "choice", "default": "Absolute (timeline timecode)",
         "choices": ["Absolute (timeline timecode)", "Relative (00:00:00:00 = timeline start)"]},
    ],
}


def run(ctx):
    lib = ctx.lib
    tl = ctx.require_timeline()
    fps = ctx.fps
    t0, t1 = tl.GetStartFrame(), tl.GetEndFrame()
    v = ctx.vars
    rows = lib.read_csv(lib.expand(v.get("csv_path")))
    start_col, end_col = v.get("start_col") or "start", v.get("end_col") or "end"
    name_col, note_col = v.get("name_col") or "name", v.get("note_col") or "note"
    color_col = (v.get("color_col") or "").strip()
    relative = (v.get("tc_base") or "").startswith("Relative")
    if rows and start_col not in rows[0]:
        raise ValueError("Column '%s' not in CSV header %s" % (start_col, list(rows[0].keys())))

    def to_frames(raw):  # same leniency as markers_from_csv: accepts M:SS / MM:SS:FF and ';' for ':'
        parts = raw.replace(";", ":").split(":")
        return lib.tc_to_frames(":".join(["00"] * (4 - len(parts)) + parts), fps)

    existing = tl.GetMarkers() or {}  # keyed by frame relative to the timeline start
    added = skipped = failed = 0
    for row in rows:
        ctx.progress()
        raw_s = (row.get(start_col) or "").strip()
        if not raw_s:
            continue
        fs = to_frames(raw_s) + (t0 if relative else 0)
        raw_e = (row.get(end_col) or "").strip()
        fe = to_frames(raw_e) + (t0 if relative else 0) if raw_e else fs
        apps = fe - fs
        if apps < 0:
            ctx.log("  %s: end before start, skipped" % raw_s)
            skipped += 1
            continue
        dur = max(apps, 1)
        rel = fs - t0  # AddMarker and GetMarkers frame frame numbers relative to the timeline start
        if not (t0 <= fs <= t1):
            ctx.log("  %s: outside %d..%d, skipped" % (raw_s, t0, t1))
            skipped += 1
            continue
        if rel in existing:  # AddMarker returns False on an occupied frame; this variant never merges
            ctx.log("  %s: frame already has a marker, skipped" % raw_s)
            skipped += 1
            continue
        name = (row.get(name_col) or "").strip() or "Note"
        note = (row.get(note_col) or "").strip()
        colour = (row.get(color_col) or "").strip() if color_col else ""
        colour = colour if colour in MARKER_COLOURS else v.get("default_color")
        r = tl.AddMarker(rel, colour, name, note, dur, "pairs")  # "pairs" so DeleteMarkerByCustomData can clean up
        if lib.ok(r):
            added += 1
            existing[rel] = True
        else:
            failed += 1
            ctx.log("  %s: AddMarker returned %r" % (raw_s, r))
    ctx.save()
    return "%d rows: %d added, %d skipped, %d failed" % (len(rows), added, skipped, failed)
