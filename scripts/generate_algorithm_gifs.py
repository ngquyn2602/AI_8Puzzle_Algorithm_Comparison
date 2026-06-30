from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
API_DIR = ROOT / "api"
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

from eight_puzzle_detective_core import SOLVER_KEYS  # noqa: E402


OUTPUT_DIR = ROOT / "docs" / "assets" / "algorithm-gifs"
CAPTURE_SCRIPT = ROOT / "scripts" / "capture_web_algorithm_frames.mjs"
GIF_SIZE = (960, 720)
WEB_CAPTURE_SOURCE = "web-ui-playwright"


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture the real web UI and build one GIF per algorithm.")
    parser.add_argument("--out", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--only", nargs="*", default=None, help="Optional aliases to generate or check.")
    parser.add_argument("--check", action="store_true", help="Verify GIF files and their web-capture manifest.")
    parser.add_argument("--base-url", help="Reuse an already running web instead of starting local servers.")
    args = parser.parse_args()

    aliases = algorithm_aliases()
    if args.only:
        requested = set(args.only)
        unknown = requested.difference(aliases)
        if unknown:
            raise SystemExit(f"Unknown aliases: {', '.join(sorted(unknown))}")
        aliases = [alias for alias in aliases if alias in requested]

    if args.check:
        check_assets(args.out, aliases)
        return

    generate_assets(args.out, aliases, args.base_url)


def algorithm_aliases() -> list[str]:
    return list(dict.fromkeys(SOLVER_KEYS.values()))


def generate_assets(output_dir: Path, aliases: list[str], base_url: str | None) -> None:
    node = shutil.which("node")
    if not node:
        raise SystemExit("Node.js is required to capture GIF frames from the web UI.")

    output_dir.mkdir(parents=True, exist_ok=True)
    temp_root = ROOT / ".tmp" / "algorithm-web-capture"
    temp_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="run-", dir=temp_root) as temp:
        frames_dir = Path(temp)
        command = [node, str(CAPTURE_SCRIPT), "--out", str(frames_dir)]
        if base_url:
            command.extend(["--base-url", base_url])
        command.extend(["--only", *aliases])
        env = os.environ.copy()
        env["PYTHON_EXECUTABLE"] = sys.executable
        subprocess.run(command, cwd=ROOT, env=env, check=True)

        capture_manifest = json.loads((frames_dir / "capture-manifest.json").read_text(encoding="utf-8"))
        captured = {entry["alias"]: entry for entry in capture_manifest}
        manifest: list[dict[str, Any]] = []

        for alias in aliases:
            entry = captured.get(alias)
            if not entry:
                raise SystemExit(f"Web capture did not return frames for {alias}.")
            frame_paths = [frames_dir / relative for relative in entry["frames"]]
            frames = [normalize_frame(Image.open(path).convert("RGB")) for path in frame_paths]
            if not frames:
                raise SystemExit(f"Web capture returned no frames for {alias}.")

            gif_path = output_dir / f"{alias}.gif"
            frames[0].save(
                gif_path,
                save_all=True,
                append_images=frames[1:],
                duration=1100,
                loop=0,
                optimize=True,
            )
            manifest.append(
                {
                    "alias": alias,
                    "algorithm": entry["algorithm"],
                    "display": entry["display"],
                    "group": entry["group"],
                    "file": gif_path.name,
                    "frames": len(frames),
                    "source": WEB_CAPTURE_SOURCE,
                    "capture_target": "live React trace panel",
                    "sha256": hashlib.sha256(gif_path.read_bytes()).hexdigest(),
                }
            )

    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Captured {len(manifest)} web UI GIF assets")


def normalize_frame(image: Image.Image) -> Image.Image:
    image.thumbnail(GIF_SIZE, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", GIF_SIZE, "#141821")
    x = (GIF_SIZE[0] - image.width) // 2
    y = (GIF_SIZE[1] - image.height) // 2
    canvas.paste(image, (x, y))
    return canvas


def check_assets(output_dir: Path, aliases: list[str]) -> None:
    manifest_path = output_dir / "manifest.json"
    if not manifest_path.exists():
        raise SystemExit("Missing GIF manifest.json")
    entries = json.loads(manifest_path.read_text(encoding="utf-8"))
    by_alias = {entry.get("alias"): entry for entry in entries}

    errors: list[str] = []
    for alias in aliases:
        path = output_dir / f"{alias}.gif"
        entry = by_alias.get(alias)
        if not path.exists():
            errors.append(f"missing {alias}.gif")
            continue
        if path.read_bytes()[:6] not in {b"GIF87a", b"GIF89a"}:
            errors.append(f"invalid GIF header: {alias}")
        if not entry:
            errors.append(f"missing manifest entry: {alias}")
            continue
        if entry.get("source") != WEB_CAPTURE_SOURCE:
            errors.append(f"not captured from web UI: {alias}")
        if entry.get("frames", 0) < 1:
            errors.append(f"no captured frames: {alias}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if entry.get("sha256") != digest:
            errors.append(f"checksum mismatch: {alias}")

    if errors:
        raise SystemExit("GIF verification failed: " + "; ".join(errors))
    print(f"OK: {len(aliases)} web-captured GIF assets verified")


if __name__ == "__main__":
    main()
