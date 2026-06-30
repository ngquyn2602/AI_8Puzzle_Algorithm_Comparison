from __future__ import annotations

import base64
import csv
import io
import os
import zipfile
from typing import Any, Literal

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from eight_puzzle_detective_core import (
    CASES,
    GOAL_STATE,
    ALGORITHM_GROUPS_VI,
    ALGORITHM_GROUP_ORDER,
    ALGORITHM_INFO,
    SOLVER_KEYS,
    algorithm_groups,
    algorithms_by_group,
    benchmark,
    display_name,
    get_case,
    group_of,
    heuristic_evidence,
    normalize_state,
    peas_model,
    solve,
)

app = FastAPI(title="8-Puzzle Detective Lab API", version="0.1.0")
origins = [item.strip() for item in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


class RunRequest(BaseModel):
    start: list[int] | None = None
    goal: list[int] = Field(default_factory=lambda: list(GOAL_STATE))
    algorithm: str = "astar"
    heuristic: Literal["manhattan", "misplaced"] = "manhattan"
    case_id: str | None = None
    max_expansions: int = Field(default=500, ge=1, le=5000)


class PredictionRequest(BaseModel):
    case_id: str
    algorithm: str | None = None
    selected_state: list[int]


class ExportRequest(RunRequest):
    formats: list[Literal["markdown", "csv", "html", "docx", "pdf"]] = Field(default_factory=lambda: ["markdown", "csv", "html", "docx", "pdf"])


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz")
def readyz() -> dict[str, str]:
    return {"status": "ready"}


@app.get("/metrics")
def metrics() -> Response:
    body = "detective_lab_info{service=\"api\"} 1\n"
    return Response(body, media_type="text/plain; version=0.0.4")


@app.get("/api/cases")
def list_cases() -> list[dict[str, Any]]:
    return [case.__dict__ for case in CASES]


@app.get("/api/cases/{case_id}")
def read_case(case_id: str) -> dict[str, Any]:
    try:
        return get_case(case_id).__dict__
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Case not found") from exc


@app.get("/api/algorithm-groups")
def list_algorithm_groups() -> dict[str, Any]:
    return {
        "groups": [
            {"name": group, "name_vi": ALGORITHM_GROUPS_VI.get(group, group)}
            for group in ALGORITHM_GROUP_ORDER
        ],
        "algorithms_by_group": algorithms_by_group(),
    }


@app.get("/api/algorithms")
def list_algorithms() -> list[dict[str, Any]]:
    rows = []
    for name, info in ALGORITHM_INFO.items():
        alias = SOLVER_KEYS.get(name)
        if alias is None:
            continue
        rows.append({
            "name": name,
            "alias": alias,
            "group": info["group"],
            "group_vi": ALGORITHM_GROUPS_VI.get(info["group"], info["group"]),
            "family": info["family"],
            "vi": info["vi"],
            "complete": info["complete"],
            "optimal": info["optimal"],
        })
    return rows


@app.get("/api/peas/{alias}")
def read_peas(alias: str) -> dict[str, Any]:
    return {
        "alias": alias,
        "algorithm": display_name(alias),
        "group": group_of(alias),
        "peas": peas_model(alias),
    }


@app.post("/api/run")
def run_algorithm(request: RunRequest) -> dict[str, Any]:
    start, goal, algorithm = resolve_run_input(request)
    result = solve(algorithm, start, goal, request.heuristic, request.max_expansions)
    algorithm_group = group_of(algorithm)
    return result.__dict__ | {
        "heuristic_evidence": [] if algorithm_group == "Adversarial / Stochastic Search" else heuristic_evidence(start, goal),
        "algorithm_display": display_name(algorithm),
        "algorithm_group": algorithm_group,
        "algorithm_group_vi": ALGORITHM_GROUPS_VI.get(algorithm_group, algorithm_group),
        "peas": peas_model(algorithm),
    }


@app.post("/api/predict")
def check_prediction(request: PredictionRequest) -> dict[str, Any]:
    case = get_case(request.case_id)
    algorithm = request.algorithm or case.algorithm
    result = solve(algorithm, case.start, case.goal, max_expansions=20)
    if len(result.trace_rows) < 2:
        raise HTTPException(status_code=422, detail="Case has no trace row to predict")
    expected_row = result.trace_rows[1]
    expected = tuple(expected_row["node"])
    selected = normalize_state(request.selected_state)
    return {
        "correct": selected == expected,
        "expected_state": expected,
        "selected_state": selected,
        "explanation": expected_row.get("explanation", "Follow the priority rule shown in the trace."),
    }


@app.post("/api/benchmark")
def run_benchmark(request: RunRequest) -> dict[str, Any]:
    start, goal, _ = resolve_run_input(request)
    rows = benchmark(start, goal)
    for row in rows:
        alias = row.get("algorithm", "")
        row["algorithm_display"] = display_name(alias)
        row["algorithm_group"] = group_of(alias)
        row["algorithm_group_vi"] = ALGORITHM_GROUPS_VI.get(group_of(alias), group_of(alias))
    return {"start": start, "goal": goal, "rows": rows}


@app.post("/api/export")
def export_pack(request: ExportRequest) -> dict[str, Any]:
    start, goal, algorithm = resolve_run_input(request)
    result = solve(algorithm, start, goal, request.heuristic, request.max_expansions)
    report = build_report(result.__dict__)
    files: dict[str, str] = {}
    if "markdown" in request.formats:
        files["detective-report.md"] = encode(report)
    if "csv" in request.formats:
        files["trace.csv"] = encode(trace_csv(result.trace_rows))
    if "html" in request.formats:
        files["detective-report.html"] = encode(html_report(report))
    if "docx" in request.formats:
        files["detective-report.docx"] = base64.b64encode(docx_bytes(report)).decode("ascii")
    if "pdf" in request.formats:
        files["detective-report.pdf"] = base64.b64encode(pdf_bytes(report)).decode("ascii")
    return {"files": files, "encoding": "base64", "summary": result.message}


def resolve_run_input(request: RunRequest) -> tuple[tuple[int, ...], tuple[int, ...], str]:
    if request.case_id:
        case = get_case(request.case_id)
        return case.start, case.goal, request.algorithm or case.algorithm
    if request.start is None:
        raise HTTPException(status_code=422, detail="Either case_id or start is required")
    return normalize_state(request.start), normalize_state(request.goal), request.algorithm


def encode(text: str) -> str:
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


def build_report(result: dict[str, Any]) -> str:
    certificate = result.get("certificate", {})
    peas = result.get("peas", [])
    lines = [
        "# 8-Puzzle Detective Lab Report",
        "",
        "## PEAS",
    ]
    if peas:
        for row in peas:
            lines.append(f"- **{row['aspect']}**: {row['definition']}")
    else:
        lines.extend([
            "- Performance: solve correctly, minimize expansions, explain decisions.",
            "- Environment: deterministic 3x3 8-Puzzle board.",
            "- Actuators: move blank tile up, down, left, right.",
            "- Sensors: board state, frontier evidence, heuristic scores.",
        ])
    lines.extend([
        "",
        "## Algorithm Profile",
        f"- Algorithm: {result.get('algorithm_display', result['algorithm'])}",
        f"- Group: {result.get('algorithm_group', '-')}",
        f"- Complete: {result['complete']}",
        f"- Optimal: {result['optimal']}",
        f"- Found: {result['found']}",
        f"- Path cost: {result['path_cost']}",
        f"- Expanded: {result['expanded']}",
        f"- Generated: {result['generated']}",
        f"- Runtime (ms): {result['runtime_ms']}",
        "",
        "## Certificate",
        f"- Solvable: {certificate.get('solvable')}",
        f"- Path valid: {certificate.get('path_valid')}",
        f"- Inversions start/goal: {certificate.get('inversions_start')} / {certificate.get('inversions_goal')}",
        "",
        "## Solution Path",
    ])
    path = result.get("path", [])
    actions = result.get("actions", [])
    if path:
        for idx, state in enumerate(path[:20]):
            action = "Start" if idx == 0 else actions[idx - 1] if idx - 1 < len(actions) else "-"
            lines.append(f"- Step {idx}: action={action}, state={list(state)}")
    lines.extend(["", "## Trace Story (first 12 expansions)"])
    for row in result.get("trace_rows", [])[:12]:
        lines.append(f"- Step {row.get('step')}: {row.get('priority_rule')} -> {row.get('selection_key')}. {row.get('explanation', '')}")
    lines.extend(["", "## Academic Limitations", "Educational complex/CSP/adversarial demos are not claimed as canonical 8-Puzzle solvers."])
    return "\n".join(lines)


def trace_csv(rows: list[dict[str, Any]]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=["step", "algorithm", "algorithm_display", "group", "node", "parent_state", "action", "action_vi", "depth", "g", "h", "f", "priority_rule", "selection_key", "frontier_count", "reached_count", "explanation"])
    writer.writeheader()
    for row in rows:
        writer.writerow({key: row.get(key, "") for key in writer.fieldnames or []})
    return buffer.getvalue()


def html_report(markdown: str) -> str:
    body = "\n".join(f"<p>{line}</p>" if line else "" for line in markdown.splitlines())
    return f"<!doctype html><html><head><meta charset='utf-8'><title>Detective Report</title></head><body>{body}</body></html>"


def docx_bytes(text: str) -> bytes:
    escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    document = "".join(f"<w:p><w:r><w:t>{line}</w:t></w:r></w:p>" for line in escaped.splitlines())
    files = {
        "[Content_Types].xml": "<?xml version='1.0'?><Types xmlns='http://schemas.openxmlformats.org/package/2006/content-types'><Default Extension='rels' ContentType='application/vnd.openxmlformats-package.relationships+xml'/><Default Extension='xml' ContentType='application/xml'/><Override PartName='/word/document.xml' ContentType='application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml'/></Types>",
        "_rels/.rels": "<?xml version='1.0'?><Relationships xmlns='http://schemas.openxmlformats.org/package/2006/relationships'><Relationship Id='rId1' Type='http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument' Target='word/document.xml'/></Relationships>",
        "word/document.xml": f"<?xml version='1.0'?><w:document xmlns:w='http://schemas.openxmlformats.org/wordprocessingml/2006/main'><w:body>{document}</w:body></w:document>",
    }
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for path, content in files.items():
            archive.writestr(path, content)
    return buffer.getvalue()


def pdf_bytes(text: str) -> bytes:
    lines = [line[:95] for line in text.splitlines()[:45]]
    operations = ["BT", "/F1 10 Tf", "50 760 Td", "14 TL"]
    for line in lines:
        safe = line.encode("latin-1", "replace").decode("latin-1")
        safe = safe.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        operations.extend([f"({safe}) Tj", "T*"])
    operations.append("ET")
    stream = "\n".join(operations).encode("latin-1")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    buffer = io.BytesIO()
    buffer.write(b"%PDF-1.4\n")
    offsets = [0]
    for index, content in enumerate(objects, start=1):
        offsets.append(buffer.tell())
        buffer.write(f"{index} 0 obj\n".encode("ascii"))
        buffer.write(content)
        buffer.write(b"\nendobj\n")
    xref_offset = buffer.tell()
    buffer.write(f"xref\n0 {len(offsets)}\n".encode("ascii"))
    buffer.write(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        buffer.write(f"{offset:010d} 00000 n \n".encode("ascii"))
    buffer.write(f"trailer << /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("ascii"))
    return buffer.getvalue()
