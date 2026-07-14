"""
회귀 검증 + 공격적(Aggressive) 테스트 스위트.

구조:
  - Fixtures : 격리된 임시 DB 경로, crud.DB_PATH 패치
  - TestCreate*   : create_user 회귀 + 공격 케이스
  - TestRead*     : read_all / read_by_id / search_by_name
  - TestUpdate*   : update_user
  - TestDelete*   : delete_user
  - TestIdEdge    : ID 연속성 경계 케이스
  - TestJsonStore : json_store 저수준 함수 유닛 테스트
"""

import json
import pytest
from pathlib import Path

import crud
from json_store import (
    init_store,
    load_records,
    persist_records,
    parse_json_string,
    load_json_file,
    save_json_file,
    to_json_string,
)
from crud import (
    create_user,
    read_all,
    read_by_id,
    search_by_name,
    update_user,
    delete_user,
)


# ──────────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────────

@pytest.fixture()
def db_path(tmp_path: Path) -> Path:
    """격리된 임시 DB 파일을 초기화한 뒤 경로를 반환."""
    path = tmp_path / "test_users.json"
    init_store(path)
    return path


@pytest.fixture(autouse=True)
def patch_db(db_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """모든 테스트에서 crud.DB_PATH 를 임시 경로로 교체."""
    monkeypatch.setattr(crud, "DB_PATH", db_path)


# ──────────────────────────────────────────────────────────────────────────────
# 회귀 테스트 — Create
# ──────────────────────────────────────────────────────────────────────────────

class TestCreateRegression:
    def test_first_id_is_one(self):
        u = create_user("홍길동", 30, "서울")
        assert u["id"] == 1

    def test_ids_auto_increment_sequentially(self):
        u1 = create_user("A", 20, "서울")
        u2 = create_user("B", 21, "부산")
        u3 = create_user("C", 22, "인천")
        assert [u1["id"], u2["id"], u3["id"]] == [1, 2, 3]

    def test_returned_dict_contains_all_fields(self):
        u = create_user("홍길동", 30, "서울")
        assert u == {"id": 1, "name": "홍길동", "age": 30, "city": "서울"}

    def test_create_persists_to_file(self, db_path: Path):
        create_user("홍길동", 30, "서울")
        raw = json.loads(db_path.read_text(encoding="utf-8"))
        assert len(raw) == 1
        assert raw[0]["name"] == "홍길동"

    def test_multiple_creates_all_persisted(self, db_path: Path):
        create_user("A", 10, "서울")
        create_user("B", 20, "부산")
        raw = json.loads(db_path.read_text(encoding="utf-8"))
        assert len(raw) == 2


# ──────────────────────────────────────────────────────────────────────────────
# 회귀 테스트 — Read
# ──────────────────────────────────────────────────────────────────────────────

class TestReadAllRegression:
    def test_empty_db_returns_empty_list(self):
        assert read_all() == []

    def test_returns_all_records(self):
        create_user("A", 20, "서울")
        create_user("B", 21, "부산")
        assert len(read_all()) == 2

    def test_order_preserved(self):
        create_user("먼저", 20, "서울")
        create_user("나중", 21, "부산")
        names = [u["name"] for u in read_all()]
        assert names == ["먼저", "나중"]


class TestReadByIdRegression:
    def test_finds_existing_user(self):
        create_user("홍길동", 30, "서울")
        u = read_by_id(1)
        assert u is not None
        assert u["name"] == "홍길동"

    def test_returns_none_for_missing_id(self):
        assert read_by_id(999) is None

    def test_returns_correct_user_among_many(self):
        create_user("A", 10, "서울")
        create_user("B", 20, "부산")
        create_user("C", 30, "인천")
        assert read_by_id(2)["name"] == "B"


class TestSearchByNameRegression:
    def test_partial_match_returns_results(self):
        create_user("홍길동", 30, "서울")
        create_user("홍순이", 25, "부산")
        create_user("김철수", 28, "인천")
        results = search_by_name("홍")
        assert len(results) == 2

    def test_exact_match(self):
        create_user("홍길동", 30, "서울")
        results = search_by_name("홍길동")
        assert len(results) == 1 and results[0]["id"] == 1

    def test_no_match_returns_empty_list(self):
        create_user("홍길동", 30, "서울")
        assert search_by_name("없는이름") == []

    def test_does_not_search_city_field(self):
        create_user("홍길동", 30, "서울")
        assert search_by_name("서울") == []

    def test_does_not_search_age_field(self):
        create_user("홍길동", 30, "서울")
        assert search_by_name("30") == []


# ──────────────────────────────────────────────────────────────────────────────
# 회귀 테스트 — Update
# ──────────────────────────────────────────────────────────────────────────────

class TestUpdateRegression:
    def test_update_single_field(self):
        create_user("홍길동", 30, "서울")
        updated = update_user(1, age=31)
        assert updated["age"] == 31

    def test_update_multiple_fields_at_once(self):
        create_user("홍길동", 30, "서울")
        updated = update_user(1, age=31, city="인천")
        assert updated["age"] == 31
        assert updated["city"] == "인천"

    def test_update_name_field(self):
        create_user("홍길동", 30, "서울")
        updated = update_user(1, name="김철수")
        assert updated["name"] == "김철수"

    def test_update_returns_none_for_missing_id(self):
        assert update_user(999, age=30) is None

    def test_invalid_field_raises_value_error(self):
        create_user("홍길동", 30, "서울")
        with pytest.raises(ValueError, match="수정 불가 필드"):
            update_user(1, invalid="x")

    def test_update_persists_to_file(self):
        create_user("홍길동", 30, "서울")
        update_user(1, city="인천")
        assert read_by_id(1)["city"] == "인천"

    def test_update_does_not_affect_unmodified_fields(self):
        create_user("홍길동", 30, "서울")
        update_user(1, age=31)
        u = read_by_id(1)
        assert u["name"] == "홍길동"
        assert u["city"] == "서울"

    def test_update_does_not_affect_other_records(self):
        create_user("홍길동", 30, "서울")
        create_user("김철수", 25, "부산")
        update_user(1, city="인천")
        assert read_by_id(2)["city"] == "부산"


# ──────────────────────────────────────────────────────────────────────────────
# 회귀 테스트 — Delete
# ──────────────────────────────────────────────────────────────────────────────

class TestDeleteRegression:
    def test_delete_existing_returns_true(self):
        create_user("홍길동", 30, "서울")
        assert delete_user(1) is True

    def test_delete_missing_returns_false(self):
        assert delete_user(999) is False

    def test_delete_removes_record(self):
        create_user("홍길동", 30, "서울")
        delete_user(1)
        assert read_by_id(1) is None

    def test_delete_reduces_count(self):
        create_user("A", 20, "서울")
        create_user("B", 21, "부산")
        delete_user(1)
        assert len(read_all()) == 1

    def test_delete_leaves_other_records_intact(self):
        create_user("A", 20, "서울")
        create_user("B", 21, "부산")
        delete_user(1)
        remaining = read_all()
        assert remaining[0]["name"] == "B"

    def test_deleted_record_not_findable(self):
        create_user("홍길동", 30, "서울")
        delete_user(1)
        assert read_by_id(1) is None
        assert search_by_name("홍길동") == []


# ──────────────────────────────────────────────────────────────────────────────
# 공격적 테스트 — ID 연속성 경계 케이스
# ──────────────────────────────────────────────────────────────────────────────

class TestIdEdge:
    def test_id_based_on_max_existing_not_global_counter(self):
        """ID는 전역 카운터가 아닌 max(현재 존재 ID) + 1.

        최고 ID 레코드를 삭제하면 그 ID가 재사용된다 — 잠재적 버그.
        (예: A=1, B=2 → delete B → C = max([1])+1 = 2, not 3)
        """
        create_user("A", 20, "서울")   # id=1
        create_user("B", 21, "부산")   # id=2
        delete_user(2)                  # 남은 records: [id=1]
        u3 = create_user("C", 22, "인천")
        assert u3["id"] == 2  # max([1]) + 1 = 2 → ID 재사용 발생

    def test_id_restarts_when_db_is_fully_emptied(self):
        """전체 삭제 후 ID 는 1 부터 재시작 (max() default=0 + 1)."""
        u1 = create_user("A", 20, "서울")
        delete_user(u1["id"])
        u2 = create_user("B", 21, "부산")
        assert u2["id"] == 1

    def test_ids_unique_across_large_batch(self):
        users = [create_user(f"U{i}", i, "서울") for i in range(100)]
        ids = [u["id"] for u in users]
        assert ids == list(range(1, 101))
        assert len(set(ids)) == 100


# ──────────────────────────────────────────────────────────────────────────────
# 공격적 테스트 — 경계값 및 비정상 입력
# ──────────────────────────────────────────────────────────────────────────────

class TestEdgeCases:
    # --- 유니코드 / 특수 문자 ---
    def test_unicode_multilingual_name(self):
        u = create_user("나카무라 타로 Müller", 30, "도쿄")
        assert read_by_id(u["id"])["name"] == "나카무라 타로 Müller"

    def test_emoji_in_name_survives_roundtrip(self):
        u = create_user("홍길동😊🎉", 30, "서울")
        assert read_by_id(u["id"])["name"] == "홍길동😊🎉"

    def test_special_chars_in_name(self):
        u = create_user("O'Brien & <Co>", 40, "더블린")
        assert read_by_id(u["id"])["name"] == "O'Brien & <Co>"

    def test_newline_in_name_stored_correctly(self):
        u = create_user("이름\n두줄", 30, "서울")
        assert read_by_id(u["id"])["name"] == "이름\n두줄"

    def test_very_long_name(self):
        long_name = "가" * 5000
        u = create_user(long_name, 30, "서울")
        assert read_by_id(u["id"])["name"] == long_name

    # --- 나이 경계값 ---
    def test_age_zero(self):
        u = create_user("아기", 0, "서울")
        assert read_by_id(u["id"])["age"] == 0

    def test_age_negative_stored_as_is(self):
        """crud 레이어는 음수 나이를 검증하지 않으므로 그대로 저장됨."""
        u = create_user("테스트", -1, "서울")
        assert read_by_id(u["id"])["age"] == -1

    def test_age_very_large(self):
        u = create_user("므두셀라", 969, "고대")
        assert read_by_id(u["id"])["age"] == 969

    # --- 빈 문자열 ---
    def test_empty_name_stored_without_validation(self):
        """crud 레이어 자체는 빈 이름을 허용 (유효성은 main.py 담당)."""
        u = create_user("", 30, "서울")
        assert read_by_id(u["id"])["name"] == ""

    def test_empty_city_stored_without_validation(self):
        u = create_user("홍길동", 30, "")
        assert read_by_id(u["id"])["city"] == ""

    # --- search_by_name 공격 케이스 ---
    def test_search_empty_string_matches_all(self):
        """빈 문자열은 모든 이름에 포함되므로 전체 반환."""
        create_user("홍길동", 30, "서울")
        create_user("김철수", 25, "부산")
        assert len(search_by_name("")) == 2

    def test_search_case_sensitive_for_latin(self):
        create_user("Alice", 30, "서울")
        assert search_by_name("alice") == []
        assert len(search_by_name("Alice")) == 1

    def test_search_returns_multiple_matches(self):
        for i in range(5):
            create_user(f"홍{i}동", 20 + i, "서울")
        create_user("김철수", 30, "부산")
        results = search_by_name("홍")
        assert len(results) == 5

    # --- update_user 공격 케이스 ---
    def test_update_no_kwargs_returns_unchanged_record(self):
        create_user("홍길동", 30, "서울")
        updated = update_user(1)
        assert updated == {"id": 1, "name": "홍길동", "age": 30, "city": "서울"}

    def test_update_valid_and_invalid_field_raises(self):
        create_user("홍길동", 30, "서울")
        with pytest.raises(ValueError):
            update_user(1, name="새이름", bad_field="x")

    def test_update_does_not_change_id(self):
        create_user("홍길동", 30, "서울")
        # id 는 UPDATABLE_FIELDS 에 없으므로 ValueError 발생해야 함
        with pytest.raises(ValueError):
            update_user(1, id=999)

    # --- delete_user 공격 케이스 ---
    def test_delete_twice_same_id(self):
        create_user("홍길동", 30, "서울")
        assert delete_user(1) is True
        assert delete_user(1) is False

    def test_delete_all_then_recreate(self):
        create_user("A", 20, "서울")
        delete_user(1)
        u = create_user("B", 21, "부산")
        assert read_all() == [u]

    # --- 대량 레코드 ---
    def test_large_dataset_crud_consistency(self):
        N = 300
        for i in range(1, N + 1):
            create_user(f"사용자{i}", i % 100, "서울")

        assert len(read_all()) == N
        assert read_by_id(N)["name"] == f"사용자{N}"

        update_user(1, name="수정된사용자1")
        assert read_by_id(1)["name"] == "수정된사용자1"

        delete_user(1)
        assert len(read_all()) == N - 1
        assert read_by_id(1) is None


# ──────────────────────────────────────────────────────────────────────────────
# json_store 저수준 함수 유닛 테스트
# ──────────────────────────────────────────────────────────────────────────────

class TestJsonStoreParsing:
    def test_parse_valid_object(self):
        assert parse_json_string('{"k": "v"}') == {"k": "v"}

    def test_parse_valid_array(self):
        assert parse_json_string("[1, 2, 3]") == [1, 2, 3]

    def test_parse_unicode_value(self):
        result = parse_json_string('{"이름": "홍길동"}')
        assert result == {"이름": "홍길동"}

    def test_parse_nested_structure(self):
        raw = '{"a": {"b": [1, 2]}}'
        assert parse_json_string(raw) == {"a": {"b": [1, 2]}}

    def test_parse_invalid_json_raises(self):
        with pytest.raises(json.JSONDecodeError):
            parse_json_string("{bad json}")

    def test_parse_empty_string_raises(self):
        with pytest.raises(json.JSONDecodeError):
            parse_json_string("")

    def test_parse_partial_json_raises(self):
        with pytest.raises(json.JSONDecodeError):
            parse_json_string('{"key": ')


class TestJsonStoreFileOps:
    def test_load_nonexistent_file_raises(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            load_json_file(tmp_path / "ghost.json")

    def test_load_invalid_json_file_raises(self, tmp_path: Path):
        bad = tmp_path / "bad.json"
        bad.write_text("{not valid}", encoding="utf-8")
        with pytest.raises(json.JSONDecodeError):
            load_json_file(bad)

    def test_load_empty_file_raises(self, tmp_path: Path):
        empty = tmp_path / "empty.json"
        empty.write_text("", encoding="utf-8")
        with pytest.raises(json.JSONDecodeError):
            load_json_file(empty)

    def test_save_creates_parent_dirs_automatically(self, tmp_path: Path):
        path = tmp_path / "a" / "b" / "c" / "data.json"
        save_json_file({"ok": True}, path)
        assert path.exists()

    def test_save_and_load_roundtrip(self, tmp_path: Path):
        data = [{"id": 1, "name": "홍길동"}]
        path = tmp_path / "rt.json"
        save_json_file(data, path)
        assert load_json_file(path) == data

    def test_save_non_ascii_no_unicode_escape(self, tmp_path: Path):
        path = tmp_path / "kor.json"
        save_json_file({"이름": "홍길동"}, path)
        raw = path.read_text(encoding="utf-8")
        # ensure_ascii=False → \uXXXX 이스케이프 없이 한글 그대로 저장
        assert "홍길동" in raw
        assert r"\u" not in raw

    def test_save_overwrites_existing_file(self, tmp_path: Path):
        path = tmp_path / "file.json"
        save_json_file([1, 2, 3], path)
        save_json_file([9, 9, 9], path)
        assert load_json_file(path) == [9, 9, 9]

    def test_save_uses_indent_default(self, tmp_path: Path):
        path = tmp_path / "indented.json"
        save_json_file({"a": 1}, path)
        raw = path.read_text(encoding="utf-8")
        assert "\n" in raw  # indent=2 이므로 개행 존재

    def test_save_accepts_string_path(self, tmp_path: Path):
        path = str(tmp_path / "str_path.json")
        save_json_file({"test": True}, path)
        assert Path(path).exists()


class TestToJsonString:
    def test_non_ascii_no_escape(self):
        result = to_json_string({"이름": "홍길동"})
        assert "홍길동" in result

    def test_with_indent_contains_newlines(self):
        assert "\n" in to_json_string([1, 2], indent=2)

    def test_without_indent_compact(self):
        assert to_json_string([1, 2]) == "[1, 2]"

    def test_none_indent_compact(self):
        result = to_json_string({"a": 1}, indent=None)
        assert "\n" not in result


class TestInitStore:
    def test_creates_file_if_missing(self, tmp_path: Path):
        path = tmp_path / "new.json"
        assert not path.exists()
        init_store(path)
        assert path.exists()

    def test_created_file_contains_empty_array(self, tmp_path: Path):
        path = tmp_path / "new.json"
        init_store(path)
        assert json.loads(path.read_text(encoding="utf-8")) == []

    def test_does_not_overwrite_existing_data(self, tmp_path: Path):
        path = tmp_path / "existing.json"
        save_json_file([{"id": 99, "name": "보존"}], path)
        init_store(path)
        assert load_records(path)[0]["id"] == 99

    def test_idempotent_on_empty_file(self, tmp_path: Path):
        path = tmp_path / "store.json"
        init_store(path)
        init_store(path)
        assert load_records(path) == []


class TestPersistAndLoadRecords:
    def test_roundtrip(self, tmp_path: Path):
        path = tmp_path / "rec.json"
        records = [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]
        persist_records(records, path)
        assert load_records(path) == records

    def test_persist_empty_list(self, tmp_path: Path):
        path = tmp_path / "rec.json"
        persist_records([], path)
        assert load_records(path) == []

    def test_persist_overwrites(self, tmp_path: Path):
        path = tmp_path / "rec.json"
        persist_records([{"id": 1}], path)
        persist_records([{"id": 2}], path)
        assert load_records(path) == [{"id": 2}]
