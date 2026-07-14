"""
JSON 데이터 파싱 / JSON 파일 저장 PoC
표준 라이브러리 json 모듈 활용
"""

import json
from pathlib import Path


# ──────────────────────────────────────────────
# 1. JSON 문자열 파싱
# ──────────────────────────────────────────────

def parse_json_string(raw: str) -> dict | list:
    """JSON 문자열을 Python 객체로 변환."""
    return json.loads(raw)


# ──────────────────────────────────────────────
# 2. JSON 파일 읽기
# ──────────────────────────────────────────────

def load_json_file(path: str | Path) -> dict | list:
    """JSON 파일을 읽어 Python 객체로 반환."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ──────────────────────────────────────────────
# 3. JSON 파일 저장
# ──────────────────────────────────────────────

def save_json_file(data: dict | list, path: str | Path, indent: int = 2) -> None:
    """Python 객체를 JSON 파일로 저장."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


# ──────────────────────────────────────────────
# 4. Python 객체 → JSON 문자열 직렬화
# ──────────────────────────────────────────────

def to_json_string(data: dict | list, indent: int | None = None) -> str:
    """Python 객체를 JSON 문자열로 직렬화."""
    return json.dumps(data, ensure_ascii=False, indent=indent)


# ──────────────────────────────────────────────
# 실행 예제
# ──────────────────────────────────────────────

if __name__ == "__main__":
    # --- 파싱 예제 ---
    raw_json = """
    {
        "name": "홍길동",
        "age": 30,
        "skills": ["Python", "JSON", "REST API"],
        "address": {
            "city": "서울",
            "zip": "04524"
        }
    }
    """
    parsed = parse_json_string(raw_json)
    print("== JSON 문자열 파싱 결과 ==")
    print(f"이름: {parsed['name']}")
    print(f"나이: {parsed['age']}")
    print(f"스킬: {', '.join(parsed['skills'])}")
    print(f"도시: {parsed['address']['city']}")

    # --- 파일 저장 예제 ---
    output_path = Path("output/sample.json")
    save_json_file(parsed, output_path)
    print(f"\n== 파일 저장 완료: {output_path} ==")

    # --- 파일 읽기 예제 ---
    loaded = load_json_file(output_path)
    print("\n== 파일 로드 후 직렬화 ==")
    print(to_json_string(loaded, indent=2))

    # --- 리스트 데이터 저장 예제 ---
    users = [
        {"id": 1, "name": "김철수", "active": True},
        {"id": 2, "name": "이영희", "active": False},
        {"id": 3, "name": "박민준", "active": True},
    ]
    save_json_file(users, "output/users.json")
    print("\n== users.json 저장 완료 ==")
    print(to_json_string(users, indent=2))
