import re
from pathlib import Path


def load_guidance(path: Path) -> dict[str, dict[str, str]]:
    markdown = path.read_text(encoding="utf-8")
    entries = {}
    for chunk in re.split(r"(?m)^### ", markdown)[1:]:
        lines = chunk.splitlines()
        guidance_id = lines[0].strip()
        item = {"id": guidance_id}
        for line in lines[1:]:
            match = re.match(
                r"^- (Signals|Guidance|Verified excerpt|Link):\s*(.*)$",
                line,
            )
            if match:
                item[match.group(1)] = match.group(2).strip().strip("“”")
        entries[guidance_id] = item
    return entries
