from enum import StrEnum

GET_HIGHLIGHTS_PROMPT = """\
You are an expert viral short-form video editor. The above is the subtitle transcript \
(SRT) of a long video. Find every engaging moment in it that can be cut into a \
YouTube Short or Instagram Reel.

TARGET LENGTH
- Each highlight, after splicing its segments together, must total roughly 30-60 \
seconds, never exceeding 150 seconds (short enough for Shorts/Reel viewers to finish \
the video instead of swiping away).

RULES
1. Find AS MANY highlights as possible. Do not stop at 3; sweep the entire transcript \
and report every highlight you find. If there are many, find them all.
2. Timestamps do NOT have to be contiguous. A single highlight may be built from \
multiple separate time ranges that the editor will cut and splice together into one \
flowing clip, e.g. [00:08:14-00:08:31] + [00:08:50-00:09:02] + [00:09:24-00:09:35].
3. Use exact SRT timestamps (HH:MM:SS) derived from the actual cues so every cut lands \
on a real spoken phrase. Never invent timestamps.
4. List each highlight's segments in the order they will play in the final clip.

HOW TO CUT FOR MAXIMUM RETENTION
- The first 1-2 seconds must hook the viewer: start mid-action or on the most \
emotional, shocking, funny, or intriguing line. Never start on a greeting, intro, \
scene setup, or warm-up rambling.
- Cut mercilessly: drop silence, dead air, filler words, repetition, tangents, and \
any sentence not actively earning watch time. A boring connective sentence is a \
viewer swiping away.
- Every segment should escalate stakes or deliver a payoff. End each highlight \
immediately after the punchline, reveal, or peak moment - before the energy drops.
- Prioritize emotional spikes: reactions, arguments, surprises, failures, comedy, \
absurd chaos, sarcasm, hot takes, and in-jokes the target audience will quote or \
rewatch.
- Exploit curiosity gaps: raise a question or tease something, then jump straight to \
the payoff.
- Feed the loop/rewatch factor: a clip that lands a quotable line or satisfying \
payoff at the very end is more likely to be watched again, boosting total watch time.

OUTPUT FORMAT (exactly one block per highlight, ranked by viral potential, best first)
**Highlight N - viral_potential X/10**
Hook: <the actual first line spoken in the clip>
Segments: [HH:MM:SS-HH:MM:SS] + [HH:MM:SS-HH:MM:SS] + ... (sum to ~30-60s, max 150s)
Summary: <one sentence describing what happens in the spliced clip>
Retention: <why viewers will keep watching: hook, escalation, emotional spike, \
curiosity, payoff, quotable/loopable ending>

If genuinely nothing qualifies, return the single best attempt rather than nothing.
"""

GET_STORY_PROMPT = """\
You are an expert long-form YouTube video editor. The above is the subtitle transcript \
(SRT) of a long video. Select timestamps from it and arrange them into ONE cohesive \
long-form video that keeps a YouTube viewer watching from the first second to the last.

TARGET LENGTH
- The final cut should run roughly 8-12 minutes, long enough to feel substantial for \
a YouTube audience but with zero room for padding. If the source material supports \
more, you may go longer, but every additional second must earn its watch time.

WHY THIS MATTERS
- YouTube's algorithm demotes a video the moment a viewer clicks away, so this is an \
all-or-nothing retention game: the viewer must stay for the ENTIRE video, not just \
the start. A strong opening alone is a failure if the middle sags or the ending \
drifts. Design for full-runtime retention.

RULES
1. Output ONE cohesive video made of ordered, spliced segments - not a list of \
unrelated highlights. The segments must chain into a single narrative arc: setup -> \
escalation -> complications -> payoff, so it plays as one story, not a highlight reel.
2. Timestamps do NOT have to be contiguous. Skip dead air, tangents, repetition, \
and low-energy stretches, and reorder freely when it strengthens the story. The \
editor will cut and splice the listed ranges in the order given, e.g. \
[00:04:12-00:06:03] + [00:11:40-00:13:05] + [00:19:02-00:21:10].
3. Reordering must not break logic or continuity: keep references, call-backs, and \
context in a sequence that makes sense to a viewer who only sees your cut.
4. Use exact SRT timestamps (HH:MM:SS) derived from the actual cues so every cut lands \
on a real spoken phrase. Never invent timestamps.

HOW TO CUT FOR FULL-RUNTIME RETENTION
- First 30 seconds decide everything: open on the strongest moment of tension, \
stakes, humor, or intrigue as the cold open. Never start on a greeting, intro, logo, \
or scene-setting. The cold open must create an open loop the rest of the video \
promises to close.
- Chain open loops: as one question is answered, raise the next before interest can \
fade, so there is always a reason to keep watching. Close the biggest loop only at \
the very end.
- Maintain momentum across the middle - the click-away zone. After every payoff, \
immediately cut to a new escalation, complication, or twist. If two adjacent segments \
both lose energy, insert a spike or cut one.
- Escalate: order segments so stakes, emotion, absurdity, or curiosity rise over the \
runtime. Climax late, then land a satisfying payoff or quotable final line that \
rewards the viewer for staying - and invites a rewatch or comment.
- Preserve audio flow: cuts should land on phrase boundaries so dialogue sounds \
natural, and transitions must not leave confusion about who is speaking or what is \
happening.
- Cut mercilessly, but do not rush the story: the viewer needs just enough connective \
context to follow the narrative. Keep connective lines only when they earn watch time \
by adding clarity, comedy, or stakes.

OUTPUT FORMAT (one block, describing the single cohesive video)
**The Story - title: <punchy YouTube-style title for this cut>**
Cold open: [HH:MM:SS-HH:MM:SS] + ... -> <the hook line spoken and the open loop it \
creates>
Sequence: [HH:MM:SS-HH:MM:SS] + [HH:MM:SS-HH:MM:SS] + ... in play order, with a \
<one-line purpose> after each range (hook / escalation / complication / payoff / \
climax / closer)
Arc: <2-3 sentences: how it opens, how tension builds across the middle, how it \
resolves>
Retention: <why the viewer stays the entire runtime: open loops held, payoffs timed, \
where the weak spots are and how the cut avoids them>

If the transcript cannot support one cohesive story, still return the best single \
narrative you can construct rather than a list of unrelated clips.
"""


class PromptType(StrEnum):
    HIGHLIGHTS = "highlights"
    STORY = "story"


PROMPTS: dict[PromptType, str] = {
    PromptType.HIGHLIGHTS: GET_HIGHLIGHTS_PROMPT,
    PromptType.STORY: GET_STORY_PROMPT,
}


def get_prompt(prompt_type: PromptType) -> str:
    """
    Returns the prompt text registered for prompt_type.
    Register newly added prompts in PROMPTS.
    """
    try:
        return PROMPTS[prompt_type]
    except KeyError:
        raise RuntimeError(f"prompt type is unsupported {prompt_type}")
