import pytest
from pathlib import Path
from layouttxt.infra.ansi_text import AnsiFileStore
from layouttxt.domain.layout_parser import parse_layout
from layouttxt.domain.layout import Layout
from layouttxt.domain.field_context import resolve_context, replace_field, overwrite_at

SAMPLE_CSV = """Id;Nome;Inic;Fim;Tam;TP;Fixo;Formato;Tag
x;Tipo;1;1;1;F;1;Tipo;X
x;Nome;2;5;4;A;;Nome;
y;Tipo;1;1;1;F;2;Tipo;X
y;Valor;2;5;4;N2;;Valor;
"""


def test_parse_layout_and_record_counts() -> None:
    layout: Layout = parse_layout(SAMPLE_CSV)
    assert layout.record_ids() == ["x", "y"]
    assert len(layout.fields_of("x")) == 2
    assert len(layout.fields_of("y")) == 2


def test_identify_records() -> None:
    layout: Layout = parse_layout(SAMPLE_CSV)
    assert layout.identify("1JOAO") == "x"
    assert layout.identify("20123") == "y"
    assert layout.identify("9XXXX") is None


def test_field_at_and_metadata() -> None:
    layout: Layout = parse_layout(SAMPLE_CSV)
    field = layout.field_at("x", 3)
    assert field is not None
    assert field.name == "Nome"
    assert field.start == 2
    assert field.end == 5
    assert field.size == 4
    assert field.field_type == "A"
    assert field.is_key is False
    assert field.extract("1MARIA") == "MARI"


def test_all_shipped_layouts_parse_cleanly() -> None:
    store = AnsiFileStore()
    layouts_dir = Path(__file__).resolve().parent.parent / "layouts"
    csv_files = list(layouts_dir.glob("*.csv"))
    assert len(csv_files) >= 10
    for path in csv_files:
        content = store.read(str(path)).content
        layout = parse_layout(content)
        assert len(layout.record_ids()) >= 1
        for record_id in layout.record_ids():
            fields = layout.fields_of(record_id)
            assert len(fields) >= 1
            # Fields should not have empty names
            assert all(f.name.strip() for f in fields)


def test_resolve_context_and_replace_field() -> None:
    layout: Layout = parse_layout(SAMPLE_CSV)
    ctx = resolve_context(layout, "1MARIA", 2, 4)
    assert ctx.record_id == "x"
    assert ctx.field is not None and ctx.field.name == "Nome"
    assert ctx.value == "MARIA"
    assert replace_field("1MARIA", ctx.field, "ANA") == "1ANA  "
    assert overwrite_at("1", 3, "Z") == "1 Z"


def test_brr_layout_and_example_file() -> None:
    from layouttxt.domain.value_description import INVALID_DATE, UNKNOWN_OPTION, describe_value

    store = AnsiFileStore()
    project_dir = Path(__file__).resolve().parent.parent
    layout = parse_layout(store.read(str(project_dir / "layouts" / "BRR.csv")).content)
    expected_ids = ["0", "1", "3A", "3C", "3D", "3I", "3J-52", "3J", "3N2", "3N3", "5", "9"]
    assert layout.record_ids() == expected_ids

    for record_id in expected_ids:
        fields = layout.fields_of(record_id)
        cursor = 1
        for field in fields:
            assert field.start == cursor, f"{record_id}.{field.name}: expected start {cursor}, got {field.start}"
            assert field.end - field.start + 1 == field.size
            cursor = field.end + 1
        assert cursor == 241, f"{record_id}: expected 240 bytes, ended at {cursor - 1}"

    example_lines = store.read(str(project_dir / "exemplos" / "brr.txt")).content.splitlines()
    assert len(example_lines) == 22
    for line in example_lines:
        assert len(line) == 240

    identified = [layout.identify(line) for line in example_lines]
    expected_identified = [
        "0",
        "1", "3A", "3C", "5",
        "1", "3J", "3J-52", "5",
        "1", "3D", "5",
        "1", "3I", "5",
        "1", "3N2", "5",
        "1", "3N3", "5",
        "9",
    ]
    assert identified == expected_identified

    expected_record_labels = {
        "0": "Header de Arquivo",
        "1": "Header de Lote",
        "3": "Detalhe",
        "5": "Trailler de Lote",
        "9": "Trailler de Arquivo",
    }
    for line_no, (line, record_id) in enumerate(zip(example_lines, identified), start=1):
        reg_field = layout.field_at(record_id, 8)
        assert reg_field is not None and reg_field.name == "Tipo de Registro"
        reg_label = describe_value(reg_field.field_type, reg_field.extract(line))
        assert reg_label == expected_record_labels[reg_field.extract(line)], (
            f"line {line_no} ({record_id}) Tipo de Registro label={reg_label!r}"
        )

        for field in layout.fields_of(record_id):
            described = describe_value(field.field_type, field.extract(line))
            assert described not in (UNKNOWN_OPTION, INVALID_DATE), (
                f"line {line_no} ({record_id}) field {field.name!r} "
                f"({field.field_type}) got {described!r} for {field.extract(line)!r}"
            )
