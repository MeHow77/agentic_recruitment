import json

import pytest

from src.data.json_file_provider import JsonFileDataProvider


def _write_json(path, data):
    path.write_text(json.dumps(data), encoding="utf-8")


def test_load_merges_personal_and_master(tmp_path, sample_personal_data, sample_master_data):
    personal = tmp_path / "personal.json"
    master = tmp_path / "master.json"
    _write_json(personal, sample_personal_data)
    _write_json(master, sample_master_data)

    provider = JsonFileDataProvider(personal, master)
    merged = provider.load_data()

    assert "personal" in merged
    assert "summary" in merged


def test_personal_overrides_master(tmp_path):
    personal = tmp_path / "personal.json"
    master = tmp_path / "master.json"
    _write_json(personal, {"key": "from_personal"})
    _write_json(master, {"key": "from_master"})

    provider = JsonFileDataProvider(personal, master)
    assert provider.load_data()["key"] == "from_personal"


def test_file_not_found_when_personal_missing(tmp_path, sample_master_data):
    master = tmp_path / "master.json"
    _write_json(master, sample_master_data)
    personal = tmp_path / "no_such_file.json"

    provider = JsonFileDataProvider(personal, master)
    with pytest.raises(FileNotFoundError):
        provider.load_data()


def test_file_not_found_when_master_missing(tmp_path, sample_personal_data):
    personal = tmp_path / "personal.json"
    _write_json(personal, sample_personal_data)
    master = tmp_path / "no_such_file.json"

    provider = JsonFileDataProvider(personal, master)
    with pytest.raises(FileNotFoundError):
        provider.load_data()


def test_empty_json_files(tmp_path):
    personal = tmp_path / "personal.json"
    master = tmp_path / "master.json"
    _write_json(personal, {})
    _write_json(master, {})

    provider = JsonFileDataProvider(personal, master)
    assert provider.load_data() == {}


def test_string_path_coercion(tmp_path, sample_personal_data, sample_master_data):
    personal = tmp_path / "personal.json"
    master = tmp_path / "master.json"
    _write_json(personal, sample_personal_data)
    _write_json(master, sample_master_data)

    provider = JsonFileDataProvider(str(personal), str(master))
    merged = provider.load_data()
    assert "personal" in merged


def test_nested_structure_preserved(tmp_path):
    personal = tmp_path / "personal.json"
    master = tmp_path / "master.json"
    _write_json(personal, {"a": {"nested": {"deep": True}}})
    _write_json(master, {"b": [1, 2, 3]})

    provider = JsonFileDataProvider(personal, master)
    merged = provider.load_data()
    assert merged["a"]["nested"]["deep"] is True
    assert merged["b"] == [1, 2, 3]


def test_master_keys_preserved_when_no_overlap(tmp_path):
    personal = tmp_path / "personal.json"
    master = tmp_path / "master.json"
    _write_json(personal, {"only_personal": 1})
    _write_json(master, {"only_master": 2})

    provider = JsonFileDataProvider(personal, master)
    merged = provider.load_data()
    assert merged["only_personal"] == 1
    assert merged["only_master"] == 2
