"""
PoC json_poc.py 의 파일 I/O 함수를 그대로 유지하는 저장소 레이어.
"""

import json
from pathlib import Path


# ──────────────────────────────────────────────
# PoC 원본 함수 (변경 없음)
# ──────────────────────────────────────────────

def parse_json_string(raw: str) -> dict | list:
    """JSON 문자열을 Python 객체로 변환."""
    return json.loads(raw)


def load_json_file(path: str | Path) -> dict | list:
    """JSON 파일을 읽어 Python 객체로 반환."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json_file(data: dict | list, path: str | Path, indent: int = 2) -> None:
    """Python 객체를 JSON 파일로 저장."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def to_json_string(data: dict | list, indent: int | None = None) -> str:
    """Python 객체를 JSON 문자열로 직렬화."""
    return json.dumps(data, ensure_ascii=False, indent=indent)


# ──────────────────────────────────────────────
# 저장소 초기화 (파일 없으면 빈 리스트 생성)
# ──────────────────────────────────────────────

def init_store(path: str | Path) -> None:
    """DB 파일이 없으면 빈 배열로 초기화."""
    p = Path(path)
    if not p.exists():
        save_json_file([], p)


def load_records(path: str | Path) -> list[dict]:
    """저장된 레코드 전체를 반환."""
    return load_json_file(path)


def persist_records(records: list[dict], path: str | Path) -> None:
    """레코드 전체를 파일에 덮어 씀."""
    save_json_file(records, path)
