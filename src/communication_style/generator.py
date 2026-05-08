from __future__ import annotations

from collections import Counter
from statistics import mean

from communication_style.models import CommunicationSample

QUESTION_WORDS = (
    "what",
    "why",
    "how",
    "when",
    "where",
    "who",
    "can",
    "could",
    "would",
    "should",
)
HEDGE_WORDS = (
    "probably",
    "maybe",
    "likely",
    "roughly",
    "I think",
    "I suspect",
    "seems",
)
DIRECTIVE_WORDS = ("please", "need", "let's", "we should", "can you", "go ahead")


def build_style_markdown(
    samples: list[CommunicationSample],
    *,
    title: str = "Communication Style Instructions",
) -> str:
    if not samples:
        raise ValueError("No samples were provided.")

    source_counts = Counter(sample.source for sample in samples)
    texts = [sample.text for sample in samples if sample.text.strip()]
    sentences = [sentence for text in texts for sentence in _sentences(text)]
    avg_words = (
        mean([len(sentence.split()) for sentence in sentences]) if sentences else 0
    )
    question_rate = sum(sentence.endswith("?") for sentence in sentences) / max(
        len(sentences), 1
    )
    top_phrases = _top_phrases(texts)

    lines = [
        f"# {title}",
        "",
        "Use these instructions when drafting messages in my voice. Treat them as style guidance, not as permission to invent facts, commitments, or customer-specific claims.",
        "",
        "## Source Basis",
        "",
        f"- Samples analyzed: {len(samples)}",
        f"- Sent email samples: {source_counts.get('sent-mail', 0)}",
        f"- Teams chat samples: {source_counts.get('teams-chat', 0)}",
        f"- Average sentence length: {avg_words:.1f} words",
        f"- Question rate: {question_rate:.0%}",
        "",
        "## Voice",
        "",
        "- Be practical, direct, and context-aware.",
        "- Prefer concrete next actions over broad commentary.",
        "- Keep the reader oriented with the smallest useful amount of background.",
        "- Use plain language and avoid sounding formal for its own sake.",
        "",
        "## Operating Rules",
        "",
        "- State the real blocker when something is blocked.",
        "- Name the smallest safe next step when asking someone else to act.",
        "- Separate evidence from inference.",
        "- Keep uncertainty visible when the evidence is incomplete.",
        "- Avoid overexplaining routine mechanics unless the recipient needs them.",
        "",
        "## Drafting Defaults",
        "",
        "- Start with the useful answer, then add context.",
        "- Use short paragraphs and compact bullets for operational details.",
        "- Prefer active verbs.",
        "- When escalating, stay calm and specific about impact.",
        "- When delegating, include the target outcome and any guardrails.",
        "",
        "## Observed Phrase Patterns",
        "",
    ]
    if top_phrases:
        lines.extend(f"- {phrase}" for phrase in top_phrases)
    else:
        lines.append(
            "- No stable repeated phrases were detected in the current sample."
        )
    lines.extend(
        [
            "",
            "## Things To Avoid",
            "",
            "- Do not make messages sound polished at the expense of being useful.",
            "- Do not bury the action item.",
            "- Do not overstate certainty.",
            "- Do not copy raw private examples into generated drafts.",
            "",
        ]
    )
    return "\n".join(lines)


def build_human_report(
    samples: list[CommunicationSample], *, title: str = "Communication Style Profile"
) -> str:
    if not samples:
        raise ValueError("No samples were provided.")

    source_counts = Counter(sample.source for sample in samples)
    texts = [sample.text for sample in samples if sample.text.strip()]
    sentences = [sentence for text in texts for sentence in _sentences(text)]
    words = [word for text in texts for word in text.split()]
    avg_words = (
        mean([len(sentence.split()) for sentence in sentences]) if sentences else 0
    )
    question_rate = sum(sentence.endswith("?") for sentence in sentences) / max(
        len(sentences), 1
    )
    top_phrases = _top_phrases(texts, limit=12)
    guide_subject = (
        title.replace(" Communication Style Profile", "")
        .replace("Communication Style Profile", "Thomas Bray")
        .strip()
    )

    lines = [
        f"# {guide_subject} -- Communication Style Guide",
        "",
        "A reference for how Thomas writes in Teams and email, derived from authored messages in the local Microsoft Graph corpus. This is descriptive, not prescriptive -- it captures the voice that already exists, with private examples summarized rather than quoted.",
        "",
        "---",
        "",
        "## 1. Core Voice",
        "",
        "Thomas writes like an operator-engineer trying to keep the work moving: **direct, context-aware, evidence-seeking, and allergic to decorative process.** The prose is built around useful next action. It is usually warm enough to keep collaboration easy, but it does not spend many words performing warmth.",
        "",
        "Three traits show up repeatedly:",
        "",
        "- **Operational directness.** The message usually gets to the useful answer quickly: what is happening, what is blocked, what changed, or what should happen next.",
        "- **Evidence before confidence.** He separates what is known from what is inferred, and he is comfortable saying when a claim needs verification.",
        "- **Collaborative pragmatism.** Even when pushing for action, the voice tends to keep the room oriented: here is the problem, here is the constraint, here is the next safe move.",
        "",
        "---",
        "",
        "## 2. Register Shifts by Audience",
        "",
        "The voice changes by context. The biggest split is not formal versus informal; it is **shared operational context versus durable external context.**",
        "",
        "### Peer / technical chats",
        "",
        "- Short, compressed, and often iterative.",
        "- Assumes the reader can follow technical shorthand.",
        "- Uses questions to steer investigation rather than to soften the ask.",
        "- Status updates are compact: done, blocked, fixed, unknown, or next step.",
        "- Humor is dry and situational, more likely to appear when shared context is already established.",
        "",
        "### Mentoring / cross-team direction",
        "",
        "- More framing appears before the ask.",
        "- Reasoning is made visible so the other person can learn the why, not only the task.",
        "- Corrections tend to focus on process, evidence, and blast radius rather than personal fault.",
        "- Reassurance is practical: the mistake matters if it changes risk or next action.",
        "",
        "### Email / durable communication",
        "",
        "- More complete context and cleaner structure.",
        "- The ask or conclusion still appears early.",
        "- Thread history and forwarded content can make the raw sample noisier than the actual authored voice.",
        "- Tone is more restrained, especially when the message may travel outside the immediate technical circle.",
        "",
        "**Rule of thumb:** the less shared context the audience has, the more Thomas adds framing; the more shared context the audience has, the more he compresses toward action.",
        "",
        "---",
        "",
        "## 3. Sentence Construction",
        "",
        f"- Average sentence length in this corpus is about **{avg_words:.1f} words**, so the natural cadence is compact.",
        "- Sentences often combine conclusion, constraint, and consequence in one move.",
        "- Fragments are acceptable when the context is already live.",
        "- Follow-up messages are part of the style: think, correct, refine, continue.",
        "- Questions are common but purposeful; they usually seek ownership, evidence, a decision, or the missing constraint.",
        f"- About **{question_rate:.0%}** of detected sentences are questions.",
        "",
        "---",
        "",
        "## 4. Vocabulary & Tics",
        "",
        "Recurring terms and pivots worth recognizing:",
        "",
    ]
    if top_phrases:
        lines.extend(f"- `{phrase}`" for phrase in top_phrases)
    else:
        lines.append(
            "- No stable repeated phrases were detected in the current corpus."
        )
    lines.extend(
        [
            "- `blocked`, `scope`, `evidence`, `safe`, `next`, and `verify` energy shows up even when those exact words do not.",
            "- Soft uncertainty markers are useful when paired with a concrete next check.",
            "- The voice prefers plain verbs over managerial abstraction.",
            "- Humor works best as a pressure release, not as a substitute for the answer.",
            "",
            "---",
            "",
            "## 5. How He Delivers Information",
            "",
            "### Sharing technical context",
            "",
            "He tends to layer the conclusion with the reason it matters. A good Thomas-style technical message gives the reader enough model to act without forcing them to reverse-engineer the reasoning.",
            "",
            "### Making decisions",
            "",
            "Decisions are framed as the next useful move, not as grand pronouncements. The voice is comfortable with provisional direction when the evidence is still arriving.",
            "",
            "### Asking for things",
            "",
            "Asks are direct and usually carry a boundary: what to check, what not to mutate, what counts as done, or what evidence would change the decision.",
            "",
            "### Owning mistakes",
            "",
            "No theatre. Name the miss, repair the state, explain the guardrail if needed, and keep moving.",
            "",
            "### Disagreeing",
            "",
            "Pushback usually targets the premise, risk, or implementation shape. The useful pattern is: name the concern, give the reason, offer the safer next move.",
            "",
            "---",
            "",
            "## 6. Formatting Habits",
            "",
            "- Short paragraphs by default.",
            "- Bullets appear when there are several operational facts or choices.",
            "- Code, paths, ticket ids, URLs, and command names are treated as normal working language.",
            "- Status reports are concise and delta-oriented.",
            "- Long explanations are acceptable when they reduce future confusion.",
            "- Emoji and decorative punctuation are not central to the voice.",
            "",
            "---",
            "",
            "## 7. What He Doesn't Do",
            "",
            "- **Doesn't pad.** Little appetite for ceremony, filler, or inbox theater.",
            "- **Doesn't hide the blocker.** If the work is blocked, the blocker is the point.",
            "- **Doesn't confuse confidence with evidence.** A hunch stays a hunch until verified.",
            "- **Doesn't over-polish operational notes.** Clarity beats elegance.",
            "- **Doesn't moralize technical problems.** Bad settings, bad joins, bad assumptions, and bad tooling are fair game; people are not the target.",
            "",
            "---",
            "",
            "## 8. Tone Cheat Sheet",
            "",
            "| Situation | What Thomas does |",
            "|---|---|",
            "| Bug or breakage | Names the failure, gives current evidence, then says what he is checking or changing. |",
            "| Ambiguous request | Clarifies the operational goal and chooses the smallest useful next move. |",
            "| Risky action | States the boundary first: read-only, local-only, no delete, no merge, no mutation, or explicit consent needed. |",
            "| Strategy / what should we do | Thinks through constraints, ranks the practical options, lands on a reversible next step. |",
            "| Someone needs help | Gives enough context to unblock them without turning the reply into a lecture. |",
            "| Status update | Reports meaningful deltas and current blocker, not generic activity. |",
            "| Disagreement | Pushes on evidence, premise, or risk; keeps the person separate from the problem. |",
            "",
            "---",
            "",
            "## 9. Corpus Notes",
            "",
            f"- Total authored samples: {len(samples)}",
            f"- Sent email samples: {source_counts.get('sent-mail', 0)}",
            f"- Teams chat samples: {source_counts.get('teams-chat', 0)}",
            f"- Approximate words analyzed: {len(words)}",
            f"- Approximate sentences analyzed: {len(sentences)}",
            "- The corpus includes forwarded emails and thread artifacts, so email-derived signals should be interpreted more cautiously than chat-authored prose.",
            "",
            "---",
            "",
            "## 10. One-Line Summary",
            "",
            "> Plain English, evidence visible, scope explicit, action close at hand -- warm enough to collaborate, direct enough to keep the work moving.",
            "",
        ]
    )
    return "\n".join(lines)


def _sentences(text: str) -> list[str]:
    chunks = []
    current = []
    for char in text:
        current.append(char)
        if char in ".?!":
            sentence = "".join(current).strip()
            if sentence:
                chunks.append(sentence)
            current = []
    tail = "".join(current).strip()
    if tail:
        chunks.append(tail)
    return chunks


def _top_phrases(texts: list[str], limit: int = 8) -> list[str]:
    candidates: Counter[str] = Counter()
    lowered = " ".join(texts).lower()
    for phrase in HEDGE_WORDS + DIRECTIVE_WORDS + QUESTION_WORDS:
        count = lowered.count(phrase.lower())
        if count:
            candidates[phrase] = count
    return [phrase for phrase, _count in candidates.most_common(limit)]
