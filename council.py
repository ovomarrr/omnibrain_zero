from concurrent.futures import ThreadPoolExecutor, as_completed
from omnibrain.providers import ask, provider_label

def run_council(providers, question, critique=True):
    results = []
    with ThreadPoolExecutor(max_workers=min(4, len(providers))) as pool:
        futures = {pool.submit(ask, p, "Answer independently. Show reasoning summary, assumptions, practical recommendation, and uncertainty. Do not invent sources.\n\nTASK:\n" + question): p for p in providers}
        for future in as_completed(futures):
            p = futures[future]
            try:
                results.append((p, future.result()))
            except Exception as e:
                results.append((p, f"Provider error: {e}"))
    if critique:
        critique_prompt = "Review these independent answers. Identify errors, gaps, disagreements, and unsupported claims. Propose a corrected answer. Do not assume majority agreement means truth.\n\n" + "\n\n".join(f"{provider_label(p)}:\n{r}" for p, r in results)
        critic = providers[0]
        try:
            critique_text = ask(critic, critique_prompt)
            results.append(("critique", critique_text))
        except Exception as e:
            results.append(("critique", f"Critique unavailable: {e}"))
    synthesis_prompt = "Act as an impartial chief analyst. Synthesize the responses into a useful final answer. Explicitly note meaningful disagreements, uncertainty, and claims that need external verification. Never claim that model consensus proves correctness.\n\nQUESTION:\n" + question + "\n\n" + "\n\n".join(f"{provider_label(p) if p != 'critique' else 'Critique'}:\n{r}" for p, r in results)
    synthesizer = providers[0]
    try:
        synthesis = ask(synthesizer, synthesis_prompt)
    except Exception as e:
        synthesis = f"Synthesis unavailable: {e}. Review the individual answers above."
    return results, synthesis
