"""Run a real sequential chat plus a bounded probe batch using Codex CLI.

All model requests are fixed to gpt-6.1-sol / high. No API key is handled here.
Raw CLI logs live in .tmp; pass a new output directory to retain reruns.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
MODEL = "gpt-6.1-sol"
EFFORT = "high"


def cases(path):
    doc = path.read_text(encoding="utf-8")
    return re.findall(r"^### ([CQ][0-9]{2}) [^\n]+\n\n```text\n(.*?)\n```", doc, re.M | re.S)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=("conversation", "probes", "all"), default="all")
    parser.add_argument("--output-dir", type=Path, default=ROOT / ".tmp/chat-v02")
    parser.add_argument("--case-file", type=Path, default=ROOT / "tests/chat-cases.md")
    args = parser.parse_args()
    case_file = args.case_file.resolve()
    if not case_file.is_relative_to((ROOT / "tests").resolve()) or case_file.suffix != ".md":
        raise SystemExit("Scenario file must be a Markdown file inside this project's tests")
    version = re.search(r'^  version: "([0-9.]+)"$', (ROOT / ".agents/skills/lebron-meme/SKILL.md").read_text(encoding="utf-8"), re.M).group(1)
    out = args.output_dir.resolve()
    if not out.is_relative_to((ROOT / ".tmp").resolve()):
        raise SystemExit("Output directory must remain inside this project's .tmp")
    out.mkdir(parents=True, exist_ok=True)
    cli = shutil.which("codex")
    if not cli:
        raise SystemExit("Codex CLI is not on PATH")
    evidence_path = out / "evidence.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8")) if evidence_path.exists() else {
        "version": version, "requested_model": MODEL,
        "requested_reasoning_effort": EFFORT, "runs": [],
        "case_file": case_file.relative_to(ROOT).as_posix(),
        "case_file_sha256": hashlib.sha256(case_file.read_bytes()).hexdigest(),
        "skill_hashes": {
            p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (ROOT / ".agents/skills/lebron-meme").rglob("*") if p.is_file()
        },
    }
    if evidence.get("case_file_sha256") != hashlib.sha256(case_file.read_bytes()).hexdigest():
        raise SystemExit("Scenario definitions changed; use a new output directory")
    if evidence.get("version") != version or evidence.get("skill_hashes") != {
        p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (ROOT / ".agents/skills/lebron-meme").rglob("*") if p.is_file()
    }:
        raise SystemExit("Skill changed; use a new output directory")

    def save():
        evidence_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def call(stem, prompt, session_id=None, persistent=False):
        output = out / (stem + "-output.md")
        log = out / (stem + "-events.jsonl")
        err = out / (stem + "-stderr.txt")
        if output.exists() or log.exists():
            raise RuntimeError("Refusing to overwrite a retained run: " + stem)
        command = [cli, "exec", "--sandbox", "read-only", "--color", "never",
                   "--model", MODEL, "-c", 'model_reasoning_effort="high"']
        if session_id:
            command += ["resume", "--skip-git-repo-check", "--json",
                        "--output-last-message", str(output), session_id, "-"]
        else:
            command += ["--skip-git-repo-check", "--json", "--output-last-message", str(output)]
            if not persistent:
                command += ["--ephemeral"]
            command += ["-"]
        (out / (stem + "-input.txt")).write_text(prompt, encoding="utf-8")
        started = time.perf_counter()
        with log.open("wb") as stdout, err.open("wb") as stderr:
            try:
                process = subprocess.run(command, input=prompt.encode("utf-8"),
                    cwd=ROOT, stdout=stdout, stderr=stderr, timeout=240)
                exit_code = process.returncode
            except subprocess.TimeoutExpired:
                evidence["runs"].append(dict(run=stem, exit_code=None, timed_out=True,
                                             elapsed_seconds=round(time.perf_counter() - started, 2)))
                save()
                raise RuntimeError("CLI timed out: " + stem)
        events = []
        for line in log.read_text(encoding="utf-8-sig").splitlines():
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        ids = [e["thread_id"] for e in events if e.get("type") == "thread.started"]
        completions = [e for e in events if e.get("type") == "turn.completed"]
        commands = [e["item"].get("command", "") for e in events
            if e.get("type") == "item.completed" and e.get("item", {}).get("type") == "command_execution"]
        tool_failures = [e["item"].get("exit_code") for e in events
            if e.get("type") == "item.completed" and e.get("item", {}).get("type") == "command_execution"
            and e["item"].get("exit_code") not in (0, None)]
        actual_id = ids[0] if ids else None
        info = dict(run=stem, requested_model=MODEL, requested_reasoning_effort=EFFORT,
            exit_code=exit_code, completed=bool(completions),
            elapsed_seconds=round(time.perf_counter() - started, 2),
            resumed=bool(session_id), observed_thread_id=bool(ids),
            same_session=bool(ids) and (not session_id or actual_id == session_id),
            session_fingerprint=hashlib.sha256(actual_id.encode()).hexdigest()[:16] if actual_id else None,
            command_count=len(commands), tool_failures=tool_failures,
            read_skill=any("lebron-meme" in c and "SKILL.md" in c for c in commands),
            read_catalog=any("meme-catalog.md" in c for c in commands),
            read_guide=any("humor-guide.md" in c for c in commands),
            read_sources=any("source-notes.md" in c for c in commands),
            output_sha256=hashlib.sha256(output.read_bytes()).hexdigest() if output.exists() else None,
            usage=completions[-1].get("usage", {}) if completions else {},
        )
        evidence["runs"].append(info)
        save()
        print(stem, "exit", exit_code, "completed", bool(completions),
              "seconds", info["elapsed_seconds"], "reads", len(commands), flush=True)
        if exit_code or not completions or not actual_id or not info["same_session"]:
            raise RuntimeError("Run incomplete or session mismatch: " + stem)
        if persistent:
            (out / "private-session.json").write_text(
                json.dumps({"session_id": actual_id}), encoding="utf-8")
        return actual_id

    inputs = cases(case_file)
    prefix = "这是已批准项目内的只读聊天采样，不是开发任务。不要修改文件、不要联网、不要重新规划，不读取tests里的判据或历史输出。只给正常用户回答，不自评。\n\n"
    if args.phase in ("conversation", "all"):
        session = None
        for stem, prompt in inputs:
            if stem.startswith("C"):
                session = call(stem, (prefix if session is None else "") + prompt,
                               session_id=session, persistent=True)
    if args.phase in ("probes", "all"):
        prompt = prefix + "使用 $lebron-meme。下面每项为独立情境，按Q编号输出正常回答，不自评：\n\n"
        prompt += "\n\n".join(stem + " 用户：" + text for stem, text in inputs if stem.startswith("Q"))
        call("probes", prompt)
    print("Evidence:", evidence_path, flush=True)


if __name__ == "__main__":
    main()
