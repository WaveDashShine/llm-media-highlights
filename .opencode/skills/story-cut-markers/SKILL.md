---
name: story-cut-markers
description: Convert LLM story/highlight timestamp blocks (.story.txt or .highlights.txt, e.g. from output/*/<file>.mp3.story.txt) into a Resolve marker CSV of spanning start-to-end markers, one row per segment, for MagicScript's "Spanning markers from a CSV" (markers_from_csv_pairs). Use when asked to generate a markers CSV, cut markers, or export timestamps from transcript/story files.
---

# Story cut markers

Converts the timestamp segments produced by the story/highlight LLM prompts into a
marker CSV of start→end spanning markers, one row per segment, imported into
DaVinci Resolve with MagicScript's "Spanning markers from a CSV".

## Source trips

The `.story.txt` (or `.highlights.txt`) output from `llm/prompts.py` prompts contains:

- a `Cold open:` line listing one or more `[HH:MM:SS-HH:MM:SS]` ranges,
- a `Sequence:` list where each item is `- [start-end] -> purpose: description`,
- ranges spliced with `+`, e.g. `[00:08:14-00:08:44] + [00:09:03-00:09:24]`.

Rows are emitted in the file's play order (cold open first), not video order.

## Extraction criteria

1. Extract every `[HH:MM:SS-HH:MM:SS]` range in play order.
2. Merge ranges separated by a 1-second boundary (e.g. one ends `00:00:17`, next
   starts `00:00:18`) into a single range with the earlier start and later end.
3. Keep ranges with real gaps (even a few seconds) as separate rows.
4. Keep intentional reprises (e.g. the cold open teaser range and the later full
   reveal of the same footage) as distinct marker pairs in their play positions.
5. Never invent timestamps; use only times present in the source file.

## CSV format

Header row: `start,end,colour,name,note` — one row per segment; notes with
commas/spaces are double-quoted.

- **start** / **end**: 4-segment `HH:MM:SS:FF` (hours:min:sec:frames), e.g.
  `00:08:14:00`. The transcript's 3-segment timestamps get `:00` appended. `end`
  is the cut point; a blank `end` yields a 1-frame marker (use it only for a
  timestamp with no range).
- **colour**: one of Resolve's marker colours (`Blue`, `Cyan`, `Green`, `Yellow`, `Red`,
  `Pink`, `Purple`, `Fuchsia`, `Rose`, `Lavender`, `Sky`, `Mint`, `Lemon`, `Sand`,
  `Cocoa`, `Cream`) — Resolve has no `Orange` marker; unknown names fall back to the
  import tool's default.
- **name**: concise descriptive title of the beat (see Marker rows).
- **note**: description; range/duration detail lives here.

## Marker rows

Each segment becomes ONE row — the marker spans start to end, so selecting the
marker selects the whole story beat:

- `start` = segment start, `end` = segment end (the old `Cut here` timecode —
  no separate out-marker row).
- name = a concise title derived from the segment's note/description
  (e.g. `Dealer riichi panic`, `More cumin payoff`, `Overcooked cumin lamb`) —
  NOT generic labels like `Highlight 1a`, `Segment 2` or `Setup`.
  Keep it short, no commas, so the CSV field stays unquoted.

## Colour rules

- Consecutive rows must NOT share a colour (each row differs from the rows
  before and after it). Role colours help distinguish purposes.

## Example

```csv
start,end,colour,name,note
00:08:14:00,00:08:20:00,Red,Dealer riichi panic,"dealer riichi, 'this is bad' hook"
00:08:31:00,00:08:44:00,Cyan,Time is of the essence,"'time is of the essence' — opens the loop"
00:00:00:00,00:02:08:00,Green,Prep montage,"dual mission + ingredient/prep montage (merged contiguous)"
```

## Procedure

1. Read the `.story.txt` and collect all ranges in play order.
2. Apply the extraction criteria (merge 1-second boundaries, keep gaps and reprises).
3. Assign colours so no two consecutive rows match.
4. Emit one start→end row per segment.
5. Write the CSV next to the transcript as `<name>.<prompt>.csv`
   (e.g. `TQLW5034.mp3.story.csv`). Import story timestamps with tc_base =
   "Relative (00:00:00:00 = timeline start)", since they count from the file
   start, not the timeline's start timecode.
