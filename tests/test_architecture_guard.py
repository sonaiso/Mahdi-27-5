"""Architectural protection tests — prevent regression of the core surface.

These tests ensure:
1. Every enum in ``enums.py`` that is imported by ``types.py`` actually exists.
2. Every name in ``core/__init__.py``'s ``__all__`` is importable.
3. ``runtime_pipeline.py`` stages produce valid trace entries.
4. No enum name floats between ``enums.py`` and ``types.py`` without sync.
"""

from __future__ import annotations

import inspect
import re
from enum import Enum

# ── Enum sync tests ─────────────────────────────────────────────────


class TestEnumSync:
    """Every enum imported by types.py must exist in enums.py."""

    def _enum_names_from_enums_module(self):
        from arabic_engine.core import enums

        return {
            name
            for name, obj in inspect.getmembers(enums)
            if inspect.isclass(obj) and issubclass(obj, Enum) and obj is not Enum
        }

    def _enum_names_imported_by_types(self):
        import pathlib

        types_path = (
            pathlib.Path(__file__).resolve().parent.parent
            / "arabic_engine" / "core" / "types.py"
        )
        content = types_path.read_text()
        # Extract all names from the `from .enums import (...)` block
        match = re.search(r"from \.enums import \((.*?)\)", content, re.DOTALL)
        assert match, "types.py should have a `from .enums import (...)` block"
        block = match.group(1)
        return set(re.findall(r"([A-Z]\w+)", block))

    def test_no_missing_enums(self):
        """types.py must not import any enum name absent from enums.py."""
        defined = self._enum_names_from_enums_module()
        imported = self._enum_names_imported_by_types()
        missing = imported - defined
        assert not missing, f"types.py imports enums missing from enums.py: {sorted(missing)}"

    def test_no_f821_in_types(self):
        """types.py must have zero F821 (undefined name) errors."""
        import subprocess

        result = subprocess.run(
            ["python", "-m", "ruff", "check", "arabic_engine/core/types.py", "--select", "F821"],
            capture_output=True,
            text=True,
        )
        assert "F821" not in result.stdout, f"types.py has F821 errors:\n{result.stdout}"


# ── Export surface tests ────────────────────────────────────────────


class TestExportSurface:
    """core/__init__.py must re-export every name in __all__."""

    def test_all_names_importable(self):
        """Every name in __all__ must be an actual attribute of core."""
        import arabic_engine.core as core

        missing = [name for name in core.__all__ if not hasattr(core, name)]
        assert not missing, f"__all__ contains non-existent names: {missing}"

    def test_star_import_succeeds(self):
        """``from arabic_engine.core import *`` must not raise."""
        import importlib

        core = importlib.import_module("arabic_engine.core")
        # Verify all names in __all__ are actually accessible
        for name in core.__all__:
            assert hasattr(core, name), f"__all__ name '{name}' not accessible"

    def test_no_duplicates_in_all(self):
        """__all__ must not contain duplicate entries."""
        import arabic_engine.core as core

        seen = set()
        dupes = []
        for name in core.__all__:
            if name in seen:
                dupes.append(name)
            seen.add(name)
        assert not dupes, f"Duplicate entries in __all__: {dupes}"


# ── Runtime pipeline tests ──────────────────────────────────────────


class TestRuntimePipeline:
    """runtime_pipeline.py must produce valid trace through all 8 stages."""

    def test_pipeline_produces_all_stages(self):
        from arabic_engine.runtime_pipeline import PipelineStage, run_pipeline

        result = run_pipeline("ذهب الطالبُ إلى المدرسة")
        stages_seen = {entry.stage for entry in result.trace}
        expected = set(PipelineStage)
        assert expected == stages_seen, f"Missing stages: {expected - stages_seen}"

    def test_pipeline_judgement_not_none(self):
        from arabic_engine.runtime_pipeline import run_pipeline

        result = run_pipeline("كتب المعلمُ الدرسَ")
        assert result.judgement is not None

    def test_pipeline_case_resolutions_have_justification(self):
        from arabic_engine.runtime_pipeline import run_pipeline

        result = run_pipeline("ذهب الطالبُ")
        for cr in result.case_resolutions:
            assert cr.role, f"CaseResolution for '{cr.token}' missing role"
            assert cr.factor, f"CaseResolution for '{cr.token}' missing factor"
            assert cr.case_state, f"CaseResolution for '{cr.token}' missing case_state"
            assert cr.justification, f"CaseResolution for '{cr.token}' missing justification"

    def test_pipeline_trace_entries_have_summaries(self):
        from arabic_engine.runtime_pipeline import run_pipeline

        result = run_pipeline("قرأ")
        for entry in result.trace:
            assert entry.input_summary, f"Trace entry for {entry.stage} missing input_summary"
            assert entry.output_summary, f"Trace entry for {entry.stage} missing output_summary"

    def test_pipeline_empty_input(self):
        from arabic_engine.runtime_pipeline import run_pipeline

        result = run_pipeline("")
        assert result.judgement is not None
        assert result.trace  # trace should exist even for empty input

    def test_pipeline_stage_count(self):
        from arabic_engine.runtime_pipeline import _STAGES, PipelineStage

        assert len(_STAGES) == len(PipelineStage), "Pipeline must have one function per stage"

    def test_runtime_state_fields(self):
        from arabic_engine.runtime_pipeline import RuntimeState

        state = RuntimeState()
        assert hasattr(state, "utterance_units")
        assert hasattr(state, "concepts")
        assert hasattr(state, "axes")
        assert hasattr(state, "relations")
        assert hasattr(state, "roles")
        assert hasattr(state, "factors")
        assert hasattr(state, "case_resolutions")
        assert hasattr(state, "judgement")
        assert hasattr(state, "trace")
