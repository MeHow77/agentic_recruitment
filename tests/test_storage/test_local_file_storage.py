import json
from pathlib import Path

from pydantic import BaseModel

from src.storage.local_file_storage import LocalFileStorage


class DummyModel(BaseModel):
    name: str
    value: int


def test_save_single_model(tmp_path):
    storage = LocalFileStorage(base_dir=tmp_path)
    model = DummyModel(name="test", value=42)
    result_path = storage.save_model(model, tmp_path / "out.json")

    saved = json.loads(result_path.read_text(encoding="utf-8"))
    assert saved["name"] == "test"
    assert saved["value"] == 42


def test_save_model_list(tmp_path):
    storage = LocalFileStorage(base_dir=tmp_path)
    models = [DummyModel(name="a", value=1), DummyModel(name="b", value=2)]
    result_path = storage.save_model(models, tmp_path / "list.json")

    saved = json.loads(result_path.read_text(encoding="utf-8"))
    assert isinstance(saved, list)
    assert len(saved) == 2
    assert saved[0]["name"] == "a"
    assert saved[1]["name"] == "b"


def test_parent_dir_created(tmp_path):
    storage = LocalFileStorage(base_dir=tmp_path)
    model = DummyModel(name="x", value=0)
    deep_path = tmp_path / "sub" / "dir" / "out.json"
    result_path = storage.save_model(model, deep_path)
    assert result_path.exists()


def test_absolute_path_ignores_base_dir(tmp_path):
    base = tmp_path / "base"
    base.mkdir()
    storage = LocalFileStorage(base_dir=base)
    abs_path = tmp_path / "absolute_out.json"
    model = DummyModel(name="abs", value=99)
    result_path = storage.save_model(model, abs_path)
    assert result_path == abs_path
    assert result_path.exists()


def test_overwrite_existing_file(tmp_path):
    storage = LocalFileStorage(base_dir=tmp_path)
    path = tmp_path / "out.json"
    storage.save_model(DummyModel(name="first", value=1), path)
    storage.save_model(DummyModel(name="second", value=2), path)

    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["name"] == "second"


def test_utf8_encoding(tmp_path):
    storage = LocalFileStorage(base_dir=tmp_path)
    model = DummyModel(name="Ünïcödé", value=0)
    result_path = storage.save_model(model, tmp_path / "utf8.json")

    raw = result_path.read_bytes().decode("utf-8")
    assert "Ünïcödé" in raw


def test_json_indentation(tmp_path):
    storage = LocalFileStorage(base_dir=tmp_path)
    model = DummyModel(name="indent", value=1)
    result_path = storage.save_model(model, tmp_path / "indented.json")

    text = result_path.read_text(encoding="utf-8")
    assert "\n" in text  # indented JSON has newlines


def test_relative_path_uses_base_dir(tmp_path):
    storage = LocalFileStorage(base_dir=tmp_path)
    rel = Path("relative.json")
    model = DummyModel(name="rel", value=7)
    result_path = storage.save_model(model, rel)
    assert result_path == tmp_path / "relative.json"
    assert result_path.exists()


def test_default_base_dir():
    storage = LocalFileStorage()
    assert storage._base_dir == Path("outputs")
