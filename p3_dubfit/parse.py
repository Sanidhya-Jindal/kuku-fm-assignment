"""Turn a screenplay .txt into a list of timed blocks. Plain code, no AI."""
import re
from pathlib import Path

TAG = re.compile(r"^\*\*(.+?):\*\*\s*$")
TIME = re.compile(r"Start:\s*\((\d+):(\d+(?:\.\d+)?)\)\s*\|\s*End:\s*\((\d+):(\d+(?:\.\d+)?)\)")
HEAD = re.compile(r"^(EPISODE NUMBER|EPISODE LOGLINE|CONTINUITY NOTES):\s*(.*)")


def _secs(m, s):
    return int(m) * 60 + float(s)


def parse_episode(text, ep_num=None):
    """Returns {'episode', 'logline', 'continuity', 'duration', 'blocks': [...]}.
    Each block: id, kind (dialogue/action/camera/sfx), speaker, emotion, start, end, text, scene."""
    meta, blocks, scene, cur = {}, [], None, None
    for raw in text.splitlines():
        line = raw.strip()
        if m := HEAD.match(line):
            meta[m.group(1)] = m.group(2)
            continue
        if line.startswith("Scene heading:"):
            scene = line.split(":", 1)[1].strip()
            continue
        if re.match(r"^(SCENE \d+|Scene (start|end):|Actions and dialogue:|--- SCRIPT)", line):
            cur = None  # structural line, not part of any block
            continue
        if m := TAG.match(line):
            tag = m.group(1).strip()
            name, emo = (tag.split(" (", 1) + [""])[:2]
            emo = emo.replace("(", "").replace(")", "").strip()
            up = name.upper()
            kind = {"CAMERA": "camera", "ACTION": "action", "SOUND FX": "sfx"}.get(up, "dialogue")
            cur = {"kind": kind, "speaker": name if kind == "dialogue" else "", "emotion": emo,
                   "start": None, "end": None, "text": "", "scene": scene}
            blocks.append(cur)
            continue
        if cur is None:
            continue
        if cur["start"] is None and (m := TIME.search(line)):
            cur["start"], cur["end"] = _secs(m[1], m[2]), _secs(m[3], m[4])
            continue
        if line and not line.startswith("---"):
            cur["text"] = (cur["text"] + " " + line).strip().strip('"') if cur["text"] else line.strip('"')
    blocks = [b for b in blocks if b["start"] is not None]
    blocks.sort(key=lambda b: (b["start"], b["end"]))
    if ep_num is None:
        ep_num = int(re.search(r"\d+", meta.get("EPISODE NUMBER", "0")).group())
    for i, b in enumerate(blocks):
        b["id"] = f"E{ep_num:03d}-{i:03d}"
        b["episode"] = ep_num
    return {"episode": ep_num, "logline": meta.get("EPISODE LOGLINE", ""),
            "continuity": meta.get("CONTINUITY NOTES", ""),
            "duration": max((b["end"] for b in blocks), default=0.0), "blocks": blocks}


def load_show(folder):
    """Reads every .txt in a folder (recursively), sorted by episode number."""
    eps = [parse_episode(p.read_text(encoding="utf-8", errors="ignore")) for p in Path(folder).rglob("*.txt")]
    return sorted(eps, key=lambda e: e["episode"])


def fmt(t):
    return f"{int(t // 60):02d}:{t % 60:05.2f}"
