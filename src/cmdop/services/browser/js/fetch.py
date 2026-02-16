"""Fetch JavaScript builders for browser automation."""

from __future__ import annotations

import json


def build_fetch_js(url: str) -> str:
    """Build JS for single fetch with JSON response."""
    return f"""
    (async function() {{
        try {{
            const resp = await fetch("{url}");
            if (!resp.ok) return JSON.stringify({{__error: resp.status}});
            return JSON.stringify(await resp.json());
        }} catch(e) {{
            return JSON.stringify({{__error: e.message}});
        }}
    }})()
    """


def build_fetch_all_js(
    urls: dict[str, str],
    headers: dict[str, str] | None = None,
    credentials: bool = False,
) -> str:
    """
    Build JS for parallel fetch with optional headers and credentials.

    Args:
        urls: Dict of {id: url} to fetch
        headers: Optional request headers (accept: application/json added by default)
        credentials: Include credentials/cookies (default False, may break CORS)

    Returns:
        JS code that returns {id: {data: ..., error: ...}}
    """
    # Default to JSON accept header since we parse as JSON
    merged_headers = {"accept": "application/json"}
    if headers:
        merged_headers.update(headers)
    headers_json = json.dumps(merged_headers)
    creds = "'include'" if credentials else "'same-origin'"
    urls_json = ", ".join([f'"{k}": "{v}"' for k, v in urls.items()])

    return f"""
    const urls = {{{urls_json}}};
    const headers = {headers_json};
    const results = {{}};

    const fetchOne = async (id, url) => {{
        try {{
            const resp = await fetch(url, {{
                headers: headers,
                credentials: {creds}
            }});

            if (!resp.ok) {{
                results[id] = {{ data: null, error: `HTTP ${{resp.status}}` }};
                return;
            }}

            const data = await resp.json();
            results[id] = {{ data: data, error: null }};
        }} catch (e) {{
            results[id] = {{ data: null, error: e.message }};
        }}
    }};

    await Promise.all(
        Object.entries(urls).map(([id, url]) => fetchOne(id, url))
    );

    return results;
    """
