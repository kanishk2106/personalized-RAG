import random
from typing import NamedTuple


class PromptItem(NamedTuple):
    messages: list[dict]
    prefix_tier: str  # "system_only" | "system_plus_context" | "unique"


SYSTEM_PROMPT = (
    "You are a precise assistant. Answer the user's question using ONLY the "
    "provided context. If the answer is not in the context, say you don't know. "
    "Keep answers under 3 sentences."
)


def load_hotpotqa_prompts(
    n: int,
    seed: int,
    cache_dir: str | None = None,
) -> list[PromptItem]:
    try:
        from datasets import load_dataset
    except ImportError as e:
        raise SystemExit("Missing dependency. Run: pip install datasets") from e

    ds = load_dataset(
        "hotpot_qa",
        "distractor",
        split="validation",
        cache_dir=cache_dir,
        trust_remote_code=True,
    )
    rng = random.Random(seed)
    indices = rng.sample(range(len(ds)), k=min(n, len(ds)))

    prompts: list[PromptItem] = []
    for idx in indices:
        ex = ds[idx]
        question: str = ex["question"]
        ctx = ex["context"]
        paragraphs = []
        for title, sentences in zip(ctx["title"], ctx["sentences"]):
            body = " ".join(s.strip() for s in sentences).strip()
            paragraphs.append(f"[{title}]\n{body}")
        context_block = "\n\n".join(paragraphs)
        user_msg = f"Context:\n{context_block}\n\nQuestion: {question}"
        prompts.append(PromptItem(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            prefix_tier="system_only",
        ))
    return prompts