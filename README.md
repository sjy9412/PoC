# JSON CRUD 콘솔 애플리케이션

JSON 파일을 데이터베이스로 사용하는 콘솔 기반 CRUD 애플리케이션입니다.  
Python 표준 라이브러리(`json`, `pathlib`)만 사용하며 외부 의존성이 없습니다.

---

## 프로젝트 구조

```
PoC/
├── json_poc.py       # PoC 원본 — JSON 파싱/저장 핵심 함수 4개
├── json_store.py     # I/O 레이어 — PoC 함수 + 저장소 초기화/로드/저장
├── crud.py           # CRUD 비즈니스 로직
├── main.py           # 콘솔 UI 진입점
├── test_crud.py      # 자동 검증 스크립트 (16개 케이스)
└── data/
    └── users.json    # JSON DB 파일 (자동 생성)
```

### 레이어 의존 방향

```
main.py  →  crud.py  →  json_store.py  →  json_poc.py (원본 함수)
  UI           비즈니스 로직      파일 I/O         JSON 파싱/직렬화
```

---

## 요구사항

- Python 3.10 이상 (union type `X | Y` 문법 사용)
- 외부 패키지 없음

---

## 실행 방법

### 1. 가상환경 생성 (선택)

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 2. 애플리케이션 실행

```bash
# Windows (한글 깨짐 방지)
python -X utf8 main.py

# macOS / Linux
python main.py
```

### 3. 테스트 실행

```bash
python -X utf8 test_crud.py
```

---

## 사용법

실행하면 아래 메뉴가 표시됩니다.

```
========================================
   JSON CRUD 콘솔 애플리케이션
   DB: data\users.json
========================================

────────────────────────────────────────
  1) 추가 (Create)
  2) 조회 (Read)
  3) 수정 (Update)
  4) 삭제 (Delete)
  0) 종료
```

### 1) 추가 (Create)

이름, 나이, 도시를 입력하면 자동으로 ID가 부여되어 저장됩니다.

```
[ 사용자 추가 ]
  이름: 홍길동
  나이: 30
  도시: 서울
  ✔ 저장 완료 →   ID   1 │ 홍길동 │ 30세 │ 서울
```

### 2) 조회 (Read)

세 가지 방식으로 조회할 수 있습니다.

| 선택 | 설명 |
|------|------|
| `1` | 전체 목록 출력 |
| `2` | ID로 단일 검색 |
| `3` | 이름 키워드 검색 |

### 3) 수정 (Update)

수정할 ID를 입력한 뒤 필드명(`name` / `age` / `city`)과 새 값을 입력합니다.

```
[ 수정 ]
  수정할 ID: 1
  현재 데이터:   ID   1 │ 홍길동 │ 30세 │ 서울
  수정 가능 필드: age, city, name
  수정할 필드: city
  새 값 (city): 부산
  ✔ 수정 완료 →   ID   1 │ 홍길동 │ 30세 │ 부산
```

### 4) 삭제 (Delete)

삭제할 ID를 입력하면 확인 프롬프트 후 삭제됩니다.

```
[ 삭제 ]
  삭제할 ID: 1
  삭제 대상:   ID   1 │ 홍길동 │ 30세 │ 부산
  정말 삭제하시겠습니까? (y/N): y
  ✔ ID 1 삭제 완료.
```

---

## 데이터 구조

`data/users.json` 파일에 아래 형식으로 저장됩니다.

```json
[
  {
    "id": 1,
    "name": "홍길동",
    "age": 30,
    "city": "서울"
  },
  {
    "id": 2,
    "name": "김철수",
    "age": 25,
    "city": "부산"
  }
]
```

---

## API 레퍼런스

### json_store.py

| 함수 | 설명 |
|------|------|
| `parse_json_string(raw)` | JSON 문자열 → Python 객체 |
| `load_json_file(path)` | JSON 파일 → Python 객체 |
| `save_json_file(data, path)` | Python 객체 → JSON 파일 저장 |
| `to_json_string(data)` | Python 객체 → JSON 문자열 |
| `init_store(path)` | DB 파일 없으면 빈 배열로 초기화 |
| `load_records(path)` | 전체 레코드 리스트 반환 |
| `persist_records(records, path)` | 레코드 전체 파일에 저장 |

### crud.py

| 함수 | 설명 |
|------|------|
| `create_user(name, age, city)` | 사용자 생성 및 저장 |
| `read_all()` | 전체 목록 반환 |
| `read_by_id(user_id)` | ID로 단일 조회 (`None` 반환 가능) |
| `search_by_name(keyword)` | 이름 키워드 검색 |
| `update_user(user_id, **fields)` | 필드 수정 (허용: `name`, `age`, `city`) |
| `delete_user(user_id)` | 삭제 (`True`/`False` 반환) |

---

## 확장 방법

### 필드 추가

1. `crud.py`의 `create_user()` 시그니처에 파라미터 추가
2. `UPDATABLE_FIELDS`에 새 필드명 추가
3. `main.py`의 `handle_create()` / `handle_update()` 에 입력 UI 추가

### 다른 모델 적용

`crud.py`의 `DB_PATH`를 변경하고 함수들을 복사해 새 모듈을 만들면 됩니다.  
`json_store.py`의 I/O 함수는 그대로 재사용할 수 있습니다.
