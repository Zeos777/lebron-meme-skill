"""Validate repository/package integrity without network or third-party modules.

This checks maintained data relationships, not cultural truth or model quality.
Stale chat evidence (skill edited after the last behavior run) is a warning by
default and an error with --strict-evidence.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlparse

FIELDS = (
    "别名", "类型", "级别", "原话与译法", "时间与背景", "幽默机制",
    "社区及日常语境", "原创改编", "反差与可比性", "原始/事实来源",
    "中文社区来源", "媒体索引", "核验与不确定性",
)
MEDIA_FIELDS = (
    "所属梗", "内容与使用语境", "平台", "原帖/作品/媒体入口", "作者",
    "素材类型", "核验状态", "版权/授权", "是否直接分发",
)
RELIABLE = ("nba.com", "si.com", "espn.com", "espnpressroom.com", "abcnews.com", "awfulannouncing.com", "deseret.com")
COMMUNITY = ("hupu.com", "tieba.baidu.com", "bilibili.com")


def sections(text: str, prefix: str, digits: int) -> list[tuple[str, str]]:
    pattern = rf"^### ({prefix}[0-9]{{{digits}}})[^\n]*\n(.*?)(?=^### |\Z)"
    return re.findall(pattern, text, flags=re.M | re.S)


def fields(body: str) -> dict[str, str]:
    return dict(re.findall(r"^- ([^：\n]+)：([^\n]*)", body, flags=re.M))


def under(host: str, domains: tuple[str, ...]) -> bool:
    return any(host == d or host.endswith("." + d) for d in domains)


def validate(root: Path, strict_evidence: bool = False) -> tuple[list[str], dict]:
    errors: list[str] = []
    skill = root / ".agents/skills/lebron-meme"
    required = [
        root / "README.md", root / "LICENSE", root / "CONTRIBUTING.md",
        skill / "SKILL.md", skill / "LICENSE.txt", skill / "agents/openai.yaml",
        *[skill / "references" / f for f in (
            "meme-catalog.md", "source-notes.md", "image-index.md", "humor-guide.md"
        )],
        root / "tests/test-cases.md", root / "tests/test-results.md",
        root / "tests/chat-cases.md", root / "tests/run_chat_checks.py",
        root / "tests/chat-results.md", root / "tests/chat-output.md", root / "tests/chat-evidence.json",
    ]
    for path in required:
        if not path.is_file():
            errors.append(f"Missing file: {path.relative_to(root)}")
    if errors:
        return errors, {}

    entry = (skill / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", entry, flags=re.S)
    if not match:
        errors.append("Missing frontmatter delimiters")
    else:
        front = match[1]
        if not re.search(r"^name: lebron-meme$", front, flags=re.M):
            errors.append("Skill name must match directory lebron-meme")
        desc = re.search(r"^description: (.+)$", front, flags=re.M)
        if not desc or not 1 <= len(desc[1]) <= 1024:
            errors.append("Description missing or exceeds specification limit")
    version_match = re.search(r'^  version: "([0-9.]+)"$', entry, flags=re.M)
    package_version = version_match[1] if version_match else "unknown"
    if len(entry.splitlines()) >= 500:
        errors.append("Entrypoint exceeds the progressive-disclosure line budget")
    if (root / "LICENSE").read_bytes() != (skill / "LICENSE.txt").read_bytes():
        errors.append("Portable bundle license differs from root license")

    refs = skill / "references"
    catalog = (refs / "meme-catalog.md").read_text(encoding="utf-8")
    source_text = (refs / "source-notes.md").read_text(encoding="utf-8")
    media_text = (refs / "image-index.md").read_text(encoding="utf-8")
    memes = sections(catalog, "LM-", 3)
    source_parts = sections(source_text, "S", 3)
    media = sections(media_text, "V", 2)
    quick_ids = re.findall(r"^\| (LM-[0-9]{3}) \|", catalog, flags=re.M)
    if Counter(quick_ids) != Counter(i for i, _ in memes):
        errors.append("Quick index and catalog records must contain the same unique IDs")
    for label, records in [("meme", memes), ("source", source_parts), ("media", media)]:
        ids = [i for i, _ in records]
        if len(ids) != len(set(ids)):
            errors.append(f"Duplicate {label} IDs")
        if not ids:
            errors.append(f"No {label} records parsed")

    sources = {}
    for sid, body in source_parts:
        f = fields(body)
        urls = re.findall(r"\]\((https?://[^)]+)\)", body)
        if not urls or not all(k in f for k in ("标题", "访问", "证据边界")):
            errors.append(f"{sid}: incomplete provenance")
            continue
        sources[sid] = (urls[0], f["访问"])
    known_urls = {url: (sid, access) for sid, (url, access) in sources.items()}
    grades: Counter = Counter()
    types: Counter = Counter()
    for mid, body in memes:
        f = fields(body)
        for key in FIELDS:
            if not f.get(key, "").strip():
                errors.append(f"{mid}: missing {key}")
        grade = f.get("级别")
        grades[grade] += 1
        types[f.get("类型")] += 1
        if grade not in ("A", "B", "C"):
            errors.append(f"{mid}: invalid evidence grade")
        if grade == "C" and f.get("类型") == "真实言论":
            errors.append(f"{mid}: pending claims must not be typed as verified quotations")
        urls = re.findall(r"\]\((https?://[^)]+)\)", body)
        for url in urls:
            if url not in known_urls:
                errors.append(f"{mid}: source URL missing from provenance index: {url}")
        evidence_field = f.get("原始/事实来源" if grade == "A" else "中文社区来源", "")
        evidence_urls = re.findall(r"\]\((https?://[^)]+)\)", evidence_field)
        domains = RELIABLE if grade == "A" else COMMUNITY
        if grade in ("A", "B") and not any(
            url in known_urls
            and known_urls[url][1] == "正文可读"
            and under(urlparse(url).hostname or "", domains)
            for url in evidence_urls
        ):
            errors.append(f"{mid}: {grade} requires a readable supporting source in its evidence field")

    media_urls = []
    verified_media = 0
    for vid, body in media:
        f = fields(body)
        for key in MEDIA_FIELDS:
            if not f.get(key, "").strip():
                errors.append(f"{vid}: missing {key}")
        if f.get("是否直接分发") != "否（尚无明确授权）":
            errors.append(f"{vid}: redistribution requires a separately reviewed license")
        for mid in re.findall(r"LM-[0-9]{3}", f.get("所属梗", "")):
            if mid not in {i for i, _ in memes}:
                errors.append(f"{vid}: unknown meme {mid}")
        urls = re.findall(r"\]\((https?://[^)]+)\)", f.get("原帖/作品/媒体入口", ""))
        media_urls.extend(urls)
        if not urls or any(u not in known_urls for u in urls):
            errors.append(f"{vid}: missing indexed media source")
        verified_media += bool(re.search("页面信息已核验|社区标签已核验", f.get("核验状态", "")))

    # Check real local destinations and explicit/GitHub-style anchors.
    docs = [p for p in root.rglob("*.md") if ".tmp" not in p.relative_to(root).parts]
    for doc in docs:
        # Immutable model transcripts may contain machine-local links. They are
        # evidence, not repository navigation; current output is hash-checked below.
        if doc.parent == root / "tests" and re.fullmatch(r"chat-v[0-9.]+-output\.md", doc.name):
            continue
        text = doc.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^\s)]+)\)", text):
            if urlparse(target).scheme:
                continue
            path, _, anchor = target.partition("#")
            destination = (doc.parent / path).resolve() if path else doc.resolve()
            if not destination.is_relative_to(root.resolve()) or not destination.is_file():
                errors.append(f"{doc.relative_to(root)}: broken local link {target}")
                continue
            if anchor:
                other = destination.read_text(encoding="utf-8")
                explicit = re.findall(r'id="([^"]+)"', other)
                headings = [
                    re.sub(r"[^\w\- ]", "", h.lower()).replace(" ", "-")
                    for h in re.findall(r"^#+ (.+)$", other, flags=re.M)
                ]
                if anchor not in explicit + headings:
                    errors.append(f"{doc.relative_to(root)}: unknown anchor {target}")

    test_text = (root / "tests/test-cases.md").read_text(encoding="utf-8")
    tests = re.findall(r"^### (T[0-9]{2}) ", test_text, flags=re.M)
    if len(tests) < 12 or len(tests) != len(set(tests)):
        errors.append("Need at least 12 unique behavioral test scenarios")
    current_evidence = root / f"tests/chat-v{package_version}-evidence.json"
    evidence_path = current_evidence if current_evidence.is_file() else root / "tests/chat-evidence.json"
    stale: list[str] = []
    try:
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        case_path = (root / evidence.get("case_file", "tests/chat-cases.md")).resolve()
        if not case_path.is_relative_to((root / "tests").resolve()) or case_path.suffix != ".md":
            raise ValueError("Scenario path outside tests")
        chat_text = case_path.read_text(encoding="utf-8")
        if evidence_path == current_evidence and evidence.get("version") != package_version:
            errors.append("Current chat evidence version differs from the Skill version")
        if evidence_path == current_evidence:
            output_file = f"tests/chat-v{package_version}-output.md"
            if evidence.get("published_output_file") != output_file:
                errors.append("Current chat evidence must identify its versioned output file")
            elif evidence.get("published_output_sha256") != hashlib.sha256((root / output_file).read_bytes()).hexdigest():
                errors.append("Published chat output hash differs from the recorded output")
    except (OSError, ValueError, TypeError, AttributeError):
        errors.append("Chat evidence or scenario file is unreadable or malformed")
        evidence = {}
        case_path = root / "tests/chat-cases.md"
        chat_text = case_path.read_text(encoding="utf-8")
    chat_ids = re.findall(r"^### ([CQ][0-9]{2}) ", chat_text, flags=re.M)
    if len(chat_ids) != len(set(chat_ids)):
        errors.append("Duplicate chat scenario IDs")
    chat_turns = sum(i.startswith("C") for i in chat_ids)
    chat_probes = sum(i.startswith("Q") for i in chat_ids)
    if chat_turns < 6 or chat_probes < 4:
        errors.append("Need six real conversation turns and at least four focused probe definitions")
    try:
        runs = evidence.get("runs", [])
        if [r.get("run") for r in runs] != [f"C{i:02d}" for i in range(1, 7)] + ["probes"]:
            errors.append("Chat evidence must include all six turns and the focused probe batch")
        turns = [r for r in runs if r.get("run", "").startswith("C")]
        if [r.get("run") for r in turns] != [f"C{i:02d}" for i in range(1, 7)]:
            errors.append("Recorded conversation must contain C01-C06 in order")
        if any(not r.get("completed") or r.get("exit_code") != 0 or not r.get("observed_thread_id") for r in runs):
            errors.append("Chat evidence includes an incomplete or unobserved CLI session")
        if len({r.get("session_fingerprint") for r in turns}) != 1 or any(not r.get("same_session") for r in turns):
            errors.append("Conversation turns must use one observed session")
        if [r.get("resumed") for r in turns] != [False, True, True, True, True, True]:
            errors.append("Conversation must start fresh and then resume five times")
        if any(r.get("requested_model") != "gpt-6.1-sol" or r.get("requested_reasoning_effort") != "high" for r in runs):
            errors.append("Chat evidence does not match the configured model and effort")
        # Freshness: does the recorded run still describe the current files?
        # Editing the skill makes the evidence stale, which is expected between
        # behavior re-runs; it only fails under --strict-evidence.
        if evidence.get("case_file_sha256") != hashlib.sha256(case_path.read_bytes()).hexdigest():
            stale.append(case_path.relative_to(root).as_posix())
        expected_skill_files = {p.relative_to(root).as_posix() for p in skill.rglob("*") if p.is_file()}
        stale.extend(sorted(expected_skill_files ^ set(evidence.get("skill_hashes", {}))))
        editorial_edits = {e["path"]: e for e in evidence.get("post_test_editorial_edits", [])}
        for path, digest in evidence.get("skill_hashes", {}).items():
            target = (root / path).resolve()
            matches = False
            if target.is_relative_to(skill.resolve()) and target.is_file():
                current = target.read_bytes()
                current_digest = hashlib.sha256(current).hexdigest()
                matches = current_digest == digest
                edit = editorial_edits.get(path)
                if not matches and edit and edit.get("kind") == "editorial-navigation-correction":
                    before, after = edit["before"].encode(), edit["after"].encode()
                    matches = bool(after) and current.count(after) == 1 and edit.get("sampled_sha256") == digest and edit.get("current_sha256") == current_digest and hashlib.sha256(current.replace(after, before, 1)).hexdigest() == digest
            if not matches:
                stale.append(path)
    except (OSError, ValueError, TypeError, KeyError):
        errors.append("Chat evidence is unreadable or malformed")
    binaries = [
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file() and ".tmp" not in p.relative_to(root).parts
        and p.suffix.lower() in (".jpg", ".jpeg", ".png", ".gif", ".webp", ".mp4", ".webm")
    ]
    if binaries:
        errors.append("Unexpected media binaries without a license review: " + ", ".join(binaries))

    # README states hand-written counts; keep them in step with the data.
    readme = (root / "README.md").read_text(encoding="utf-8")
    claims = [
        (r"共(\d+)条候选", len(memes)),
        (r"默认可用(\d+)条", grades["A"] + grades["B"]),
        (r"^\| A \| (\d+) \|", grades["A"]),
        (r"^\| B \| (\d+) \|", grades["B"]),
        (r"^\| C \| (\d+) \|", grades["C"]),
        (r"索引(\d+)个来源页面", len(sources)),
        (r"整理(\d+)条线索", len(media)),
        (r"(\d+)个不同入口", len(set(media_urls))),
        (r"(\d+)条的页面信息/社区标签可读", verified_media),
        (r"(\d+)条仍待核验", len(media) - verified_media),
    ]
    for pattern, actual in claims:
        found = re.search(pattern, readme, flags=re.M)
        if not found:
            errors.append(f"README count statement not found: {pattern}")
        elif int(found[1]) != actual:
            errors.append(f"README says {found[0]!r} but data has {actual}")

    summary = dict(
        memes=len(memes), grades=dict(grades), types=dict(types),
        usable=grades["A"] + grades["B"], sources=len(sources),
        media=len(media), unique_media_urls=len(set(media_urls)),
        media_page_or_label_verified=verified_media,
        media_pending=len(media) - verified_media, test_scenarios=len(tests),
        entry_lines=len(entry.splitlines()), media_binaries=len(binaries),
        chat_turns=chat_turns, chat_probes=chat_probes,
        chat_case_file=case_path.relative_to(root).as_posix(),
        chat_evidence_file=evidence_path.relative_to(root).as_posix(),
        stale_evidence=stale,
    )
    if strict_evidence:
        errors.extend(f"Chat evidence is stale for: {p}" for p in stale)
    return errors, summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--strict-evidence", action="store_true",
        help="fail when the current version's chat evidence no longer matches the Skill files (use before a release)",
    )
    args = parser.parse_args()
    problems, summary = validate(args.root.resolve(), strict_evidence=args.strict_evidence)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    for problem in problems:
        print("ERROR:", problem)
    if summary.get("stale_evidence") and not args.strict_evidence:
        print("WARNING: chat evidence predates edits to: " + ", ".join(summary["stale_evidence"]))
        print("         Behavior results describe the older files; re-run tests/run_chat_checks.py before a release.")
    print(f"Static validation: {'FAIL' if problems else 'PASS'} ({len(problems)} errors)")
    raise SystemExit(bool(problems))
