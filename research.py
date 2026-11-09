def web_search(query, max_results=8):
    """Uses DuckDuckGo's public HTML results. It is free-access, but not a guaranteed API."""
    try:
        from ddgs import DDGS
        rows = DDGS().text(query, max_results=max_results)
        results = []
        for row in rows:
            results.append({
                "title": row.get("title") or "Untitled result",
                "url": row.get("href") or row.get("url") or "",
                "snippet": row.get("body") or ""
            })
        return [x for x in results if x["url"]]
    except Exception as e:
        raise RuntimeError(f"Public search unavailable: {e}")
