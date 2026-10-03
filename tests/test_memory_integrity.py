from datetime import datetime

import pytest
import yaml

from personal_memory_os.deploy import install
from personal_memory_os.doctor import run_doctor
from personal_memory_os.errors import ValidationError
from personal_memory_os.events import now_for_vault, write_correction, write_memory_event
from personal_memory_os.frontmatter import dumps, load_file
from personal_memory_os.ingest import ingest_turn
from personal_memory_os.models import CorrectionEvent, MemoryEvent
from personal_memory_os.views import rebuild_views


@pytest.fixture
def vault(tmp_path):
    root = tmp_path / "vault"
    install(root)
    return root


def memory(vault, event_id, **kwargs):
    return MemoryEvent(
        id=event_id, type="decision", content=f"content-{event_id}",
        created_at=now_for_vault(vault), source="test", **kwargs,
    )


def test_supersession_chain_keeps_only_current_memory_and_correction(vault):
    originals = {}
    for event_id, supersedes in (("a", []), ("b", ["a"]), ("c", ["b"])):
        path = write_memory_event(vault, memory(vault, event_id, supersedes=supersedes))
        originals[path] = path.read_bytes()
        correction = CorrectionEvent(
            id=event_id, wrong=f"wrong-{event_id}", correct=f"correct-{event_id}",
            created_at=now_for_vault(vault), source="test", supersedes=supersedes,
        )
        path = write_correction(vault, correction)
        originals[path] = path.read_bytes()
    rebuild_views(vault)
    for name in ("MEMORY.md", "NOW.md"):
        text = (vault / name).read_text()
        assert "content-c" in text
        assert "content-a" not in text and "content-b" not in text
    text = (vault / "GUARDRAILS.md").read_text()
    assert "correct-c" in text
    assert "correct-a" not in text and "correct-b" not in text
    assert all(path.read_bytes() == original for path, original in originals.items())


def test_archiving_replacement_does_not_revive_old_memory(vault):
    write_memory_event(vault, memory(vault, "old"))
    write_memory_event(vault, memory(vault, "replacement", supersedes=["old"], status="archived"))
    rebuild_views(vault)
    assert "content-old" not in (vault / "MEMORY.md").read_text()


def test_rejected_inference_does_not_hide_explicit_memory(vault):
    write_memory_event(vault, memory(vault, "explicit"))
    write_memory_event(vault, memory(
        vault, "guess", supersedes=["explicit"], explicitness="inferred", confidence=0.1,
    ))
    rebuild_views(vault)
    for name in ("MEMORY.md", "NOW.md"):
        text = (vault / name).read_text()
        assert "content-explicit" in text and "content-guess" not in text


@pytest.mark.parametrize("threshold", [0.8, 0.99])
def test_both_views_use_configured_confidence_and_label_inferences(vault, threshold):
    path = vault / "_config/settings.yaml"
    settings = yaml.safe_load(path.read_text())
    settings["memory"]["inferred_memory_min_confidence"] = threshold
    path.write_text(yaml.safe_dump(settings))
    for event_id, confidence, explicitness in (
        ("low", 0.1, "inferred"), ("below", threshold - 0.01, "inferred"),
        ("boundary", threshold, "inferred"), ("explicit", 0.1, "explicit"),
    ):
        write_memory_event(vault, memory(vault, event_id, confidence=confidence, explicitness=explicitness))
    rebuild_views(vault)
    for name in ("MEMORY.md", "NOW.md"):
        text = (vault / name).read_text()
        assert "content-low" not in text and "content-below" not in text
        assert "content-boundary" in text and "content-explicit" in text
        assert f"[inferred; confidence={threshold:g}]" in text


@pytest.mark.parametrize("created_at", ["2026-10-02T12:00:00", "not-a-date", 123, 0, ""])
def test_ingest_rejects_bad_timestamp_before_persisting(vault, created_at):
    with pytest.raises(ValidationError, match="created_at"):
        ingest_turn(vault, {"memory_events": [{
            "type": "decision", "content": "must not persist", "created_at": created_at,
        }]})
    assert list((vault / "10_Memory/Events").glob("*.md")) == []
    rebuild_views(vault)


@pytest.mark.parametrize("field,value", [
    ("content", None), ("source", 42), ("confidence", True),
    ("confidence", "0.9"), ("supersedes", "abc"), ("id", None),
])
def test_ingest_does_not_coerce_invalid_fields_into_valid_records(vault, field, value):
    item = {"type": "fact", "content": "valid", field: value}
    with pytest.raises(ValidationError):
        ingest_turn(vault, {"memory_events": [item]})
    assert list((vault / "10_Memory/Events").glob("*.md")) == []


@pytest.mark.parametrize("field,value", [
    ("schema", "pmo.memory-event/v2"), ("id", ""), ("source", None),
    ("created_at", "2026-10-02T12:00:00"), ("type", "unknown"),
    ("explicitness", "certain"), ("status", "invalid"), ("confidence", 2),
    ("importance", True), ("topic", []), ("supersedes", "other"),
    ("supersedes", ["same", "same"]), ("supersedes", ["valid"]),
])
def test_external_bad_records_fail_doctor_and_preserve_existing_views(vault, field, value):
    path = write_memory_event(vault, memory(vault, "valid"))
    meta, body = load_file(path)
    meta[field] = value
    path.write_text(dumps(meta, body))
    before = {name: (vault / name).read_bytes() for name in ("MEMORY.md", "NOW.md", "GUARDRAILS.md", "INDEX.md")}
    with pytest.raises(ValidationError):
        rebuild_views(vault)
    check = next(c for c in run_doctor(vault) if c.name == "memory_parse")
    assert not check.ok and "valid.md" in check.detail
    assert all((vault / name).read_bytes() == data for name, data in before.items())


def test_missing_schema_cannot_be_promoted(vault):
    (vault / "10_Memory/Events/bad.md").write_text("---\ntype: fact\n---\n\nInvalid\n")
    with pytest.raises(ValidationError, match="missing required fields"):
        rebuild_views(vault)


def test_duplicate_external_ids_fail_closed(vault):
    path = write_memory_event(vault, memory(vault, "original"))
    path.with_name("duplicate.md").write_bytes(path.read_bytes())
    with pytest.raises(ValidationError, match="duplicate event ID"):
        rebuild_views(vault)


def test_model_rejects_naive_datetime_and_metadata_overrides(vault):
    event = memory(vault, "naive")
    event.created_at = datetime(2026, 10, 2)  # noqa: DTZ001 - deliberately invalid input
    with pytest.raises(ValidationError, match="timezone"):
        write_memory_event(vault, event)
    with pytest.raises(ValidationError, match="override"):
        write_memory_event(vault, memory(vault, "override", metadata={"status": "active"}))


def test_correction_body_and_schema_are_validated(vault):
    event = CorrectionEvent(id="c", wrong="old", correct="new", created_at=now_for_vault(vault), source="test")
    path = write_correction(vault, event)
    meta, _ = load_file(path)
    path.write_text(dumps(meta, "## Wrong assumption\nold"))
    with pytest.raises(ValidationError, match="Correct understanding"):
        rebuild_views(vault)
    assert not next(c for c in run_doctor(vault) if c.name == "memory_parse").ok


def test_unquoted_yaml_timestamp_is_supported(vault):
    path = write_memory_event(vault, memory(vault, "yaml"))
    meta, body = load_file(path)
    meta["created_at"] = now_for_vault(vault)
    path.write_text(dumps(meta, body))
    rebuild_views(vault)
    assert "content-yaml" in (vault / "NOW.md").read_text()


def test_bom_and_crlf_memory_from_cloud_writer_is_readable(vault):
    path = write_memory_event(vault, memory(vault, "bom-crlf"))
    original_meta, original_body = load_file(path)
    path.write_bytes(b"\xef\xbb\xbf" + path.read_bytes().replace(b"\n", b"\r\n"))

    meta, body = load_file(path)

    assert meta == original_meta
    assert body == original_body
    assert next(c for c in run_doctor(vault) if c.name == "memory_parse").ok
