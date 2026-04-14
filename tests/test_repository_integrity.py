"""Repository integrity tests."""

from __future__ import annotations

from pathlib import Path

from arabic_engine.core.integrity import (
    DEFAULT_REQUIRED_MODULES,
    format_integrity_report,
    scan_repository_integrity,
)


def test_repository_integrity_passes_for_project() -> None:
    project_root = Path(__file__).resolve().parents[1]
    report = scan_repository_integrity(project_root)
    assert report.ok is True
    assert report.missing_modules == ()
    assert report.duplicate_groups == ()
    assert report.scanned_files > 0
    assert len(report.imported_modules) == len(DEFAULT_REQUIRED_MODULES)


def test_repository_integrity_detects_missing_module(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    src = project_root / "src"
    src.mkdir(parents=True)
    (src / "module.py").write_text("VALUE = 1\n", encoding="utf-8")

    report = scan_repository_integrity(
        project_root,
        required_modules=("sys", "non_existing_project_module_xyz"),
        scan_dirs=("src",),
    )
    assert report.ok is False
    assert report.imported_modules == ("sys",)
    assert report.missing_modules == ("non_existing_project_module_xyz",)


def test_repository_integrity_detects_duplicate_content(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    docs = project_root / "docs"
    docs.mkdir(parents=True)
    (docs / "a.md").write_text("# same\ncontent\n", encoding="utf-8")
    (docs / "b.md").write_text("# same\ncontent\n", encoding="utf-8")
    (docs / "c.md").write_text("# different\n", encoding="utf-8")

    report = scan_repository_integrity(
        project_root,
        required_modules=("sys",),
        scan_dirs=("docs",),
    )
    assert report.ok is False
    assert len(report.duplicate_groups) == 1
    duplicate_paths = report.duplicate_groups[0].paths
    assert duplicate_paths == ("docs/a.md", "docs/b.md")

    formatted = format_integrity_report(report)
    assert "Duplicate file-content groups" in formatted
