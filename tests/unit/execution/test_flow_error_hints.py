from src.shared.execution.checking.flow_error_hints import enrich_flow_pattern_errors


def test_enrich_flow_pattern_errors__does_not_leak_expected_sequence() -> None:
    errors = [{"type": "FLOW_SEQUENCE_MISMATCH", "text": "Проверьте порядок."}]
    debug = {
        "expected_sequence": "Начало → Цикл → Вывод → Конец",
        "detected_sequence": "Начало → Вывод → Цикл → Конец",
    }

    enriched = enrich_flow_pattern_errors(errors, debug)

    assert len(enriched) == 1
    assert "Ожидаемый порядок" not in enriched[0]["text"]
    assert "Цикл" not in enriched[0].get("text", "")


def test_enrich_flow_pattern_errors__does_not_leak_text_check_patterns() -> None:
    errors = [{"type": "FLOW_TEXT_MISMATCH", "text": "Проверьте текст блоков."}]
    debug = {
        "text_check_failures": [
            {"block_type": "loop", "patterns": ["range(3)", "for"]},
        ],
    }

    enriched = enrich_flow_pattern_errors(errors, debug)

    assert "range(3)" not in enriched[0]["text"]


def test_enrich_flow_pattern_errors__adds_loop_back_hint() -> None:
    errors = [{"type": "FLOW_LOOP_BACK_EDGE", "text": "Нужна обратная связь."}]
    enriched = enrich_flow_pattern_errors(errors, {})

    assert "обратно" in enriched[0]["text"].lower()


def test_enrich_flow_pattern_errors__adds_source_alignment_hint() -> None:
    errors = [{"type": "FLOW_SOURCE_MISMATCH", "text": "Текст не совпадает."}]
    debug = {
        "source_alignment_failures": [
            {"hint": "В блоке «Цикл» укажите условие range(3), как в программе."},
        ],
    }

    enriched = enrich_flow_pattern_errors(errors, debug)

    assert "range(3)" in enriched[0]["text"]


def test_enrich_flow_pattern_errors__adds_construction_missing_hint() -> None:
    errors = [{"type": "FLOW_CONSTRUCTION_MISSING", "text": "Не хватает конструкции."}]
    debug = {
        "construction_missing": [{"missing": "цикл (блок «Цикл»)"}],
    }

    enriched = enrich_flow_pattern_errors(errors, debug)

    assert "Цикл" in enriched[0]["text"]


def test_enrich_flow_pattern_errors__returns_unchanged_without_debug() -> None:
    errors = [{"type": "FLOW_EMPTY", "text": "Пусто."}]
    assert enrich_flow_pattern_errors(errors, None) == errors
