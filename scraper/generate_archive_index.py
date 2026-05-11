"""
GitHub Pages doesn't serve auto-generated directory listings, so we write an
index.html at each level under data/archive/ so the 'history' link in the UI
becomes a browseable archive.

Levels:
  data/archive/index.html              — lists YY.MM.DD/ days
  data/archive/<YY.MM.DD>/index.html   — lists <HH>/ hours
  data/archive/<YY.MM.DD>/<HH>/index.html — lists *.json files
"""
from __future__ import annotations

from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = ROOT / "data" / "archive"


STYLE = """:root{--bg:#0b0d10;--panel:#14181d;--line:#232a32;--fg:#e7ecf1;--muted:#8a95a3;--accent:#1ee84d}
*{box-sizing:border-box}
body{margin:0;padding:24px;background:var(--bg);color:var(--fg);font:14px/1.5 -apple-system,system-ui,"PingFang SC","Hiragino Sans",sans-serif}
.wrap{max-width:900px;margin:0 auto}
h1{margin:0 0 4px;font-size:22px;letter-spacing:-0.01em}
.crumb{color:var(--muted);font-size:12px;margin-bottom:18px}
.crumb a{color:var(--accent);text-decoration:none}
.crumb a:hover{text-decoration:underline}
ul{list-style:none;padding:0;margin:0;border:1px solid var(--line);border-radius:8px;overflow:hidden}
li{border-bottom:1px solid var(--line)}
li:last-child{border-bottom:none}
li a{display:flex;justify-content:space-between;padding:11px 14px;color:var(--fg);text-decoration:none;background:var(--panel)}
li a:hover{background:#1c2128;color:var(--accent)}
.size{color:var(--muted);font-size:12px}
.empty{padding:50px 20px;text-align:center;color:var(--muted);border:1px dashed var(--line);border-radius:8px}
footer{margin-top:24px;color:var(--muted);font-size:12px}
footer a{color:var(--accent);text-decoration:none}
footer a:hover{text-decoration:underline}"""


def render(path: Path, heading: str, crumb_html: str, entries: list[tuple[str, str, str]], root_rel: str, empty_hint: str | None) -> None:
    """entries = list of (href, label, right-side text)"""
    rows = "\n".join(
        f'<li><a href="{escape(h)}"><span>{escape(label)}</span><span class="size">{escape(right)}</span></a></li>'
        for h, label, right in entries
    )
    body = f"<ul>{rows}</ul>" if entries else f'<div class="empty">{escape(empty_hint or "Empty.")}</div>'
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(heading)}</title>
<link rel="icon" type="image/png" href="{root_rel}assets/icon.png">
<style>{STYLE}</style>
</head>
<body>
<div class="wrap">
<h1>{escape(heading)}</h1>
<div class="crumb">{crumb_html}</div>
{body}
<footer><a href="{root_rel}">← back to live trending</a></footer>
</div>
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")


def human_size(n: int) -> str:
    for u in ("B", "KB", "MB"):
        if n < 1024:
            return f"{n:.0f} {u}" if u == "B" else f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} GB"


def main() -> None:
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    days = sorted((p.name for p in ARCHIVE.iterdir() if p.is_dir()), reverse=True)

    # Top level
    render(
        ARCHIVE / "index.html",
        heading="Trending · Archive",
        crumb_html='<a href="../../">← live trending</a>',
        entries=[(f"{d}/", d, "") for d in days],
        root_rel="../../",
        empty_hint="No snapshots yet. Archive runs at UTC 00:00 and 12:00 daily — first one lands within 12 hours.",
    )

    for day in days:
        day_dir = ARCHIVE / day
        hours = sorted(p.name for p in day_dir.iterdir() if p.is_dir())
        render(
            day_dir / "index.html",
            heading=f"Archive · {day}",
            crumb_html=f'<a href="../">archive</a> / {escape(day)}',
            entries=[(f"{h}/", f"{h}:00 UTC", "") for h in hours],
            root_rel="../../../",
            empty_hint="This day has no snapshots.",
        )
        for hour in hours:
            hour_dir = day_dir / hour
            files = sorted((p for p in hour_dir.iterdir() if p.is_file() and p.suffix == ".json"), key=lambda p: p.name)
            render(
                hour_dir / "index.html",
                heading=f"Archive · {day} · {hour}:00 UTC",
                crumb_html=f'<a href="../../">archive</a> / <a href="../">{escape(day)}</a> / {escape(hour)}:00',
                entries=[(p.name, p.name, human_size(p.stat().st_size)) for p in files],
                root_rel="../../../../",
                empty_hint="Slot has no files.",
            )

    print(f"archive index: {len(days)} day(s)")


if __name__ == "__main__":
    main()
