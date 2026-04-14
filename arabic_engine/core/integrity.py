"""Repository-level integrity checks for architecture and duplicate files."""

from __future__ import annotations

import hashlib
import importlib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

DEFAULT_REQUIRED_MODULES: tuple[str, ...] = (
    "arabic_engine.pipeline",
    "arabic_engine.closure",
    "arabic_engine.signifier.unicode_norm",
    "arabic_engine.signifier.root_pattern",
    "arabic_engine.signifier.transition",
    "arabic_engine.signifier.functional_transition",
    "arabic_engine.signifier.aeu",
    "arabic_engine.signified.ontology",
    "arabic_engine.signified.ontology_v1",
    "arabic_engine.linkage.dalala",
    "arabic_engine.syntax.syntax",
    "arabic_engine.cognition.evaluation",
    "arabic_engine.cognition.time_space",
    "arabic_engine.cognition.inference_rules",
    "arabic_engine.cognition.world_model",
    "arabic_engine.cognition.knowledge_graph",
    "arabic_engine.cognition.episode_validator",
    "arabic_engine.cognition.epistemic_v1",
    "arabic_engine.cognition.discourse_exchange",
    "arabic_engine.core.fractal_constitution",
    "arabic_engine.representation.fractal_rep_spec",
)

DEFAULT_SCAN_DIRS: tuple[str, ...] = ("arabic_engine", "tests", "docs", "db")


@dataclass(frozen=True)
class DuplicateFileGroup:
    """A set of files that share the same SHA-256 content."""

    sha256: str
    paths: tuple[str, ...]


@dataclass(frozen=True)
class IntegrityReport:
    """Integrity report for repository architecture and duplicate-content checks."""

    imported_modules: tuple[str, ...]
    missing_modules: tuple[str, ...]
    duplicate_groups: tuple[DuplicateFileGroup, ...]
    scanned_files: int

    @property
    def ok(self) -> bool:
        """Return ``True`` when the repository passes all integrity checks."""
        return not self.missing_modules and not self.duplicate_groups


def _iter_scannable_files(project_root: Path, scan_dirs: Sequence[str]) -> Iterable[Path]:
    for relative_dir in scan_dirs:
        root = project_root / relative_dir
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            if "__pycache__" in path.parts:
                continue
            yield path


def _find_duplicate_content_groups(
    project_root: Path, scan_dirs: Sequence[str]
) -> tuple[DuplicateFileGroup, ...]:
    hash_to_paths: dict[str, list[str]] = {}
    for path in _iter_scannable_files(project_root, scan_dirs):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        relative_path = str(path.relative_to(project_root))
        hash_to_paths.setdefault(digest, []).append(relative_path)

    duplicate_groups: list[DuplicateFileGroup] = []
    for digest, paths in hash_to_paths.items():
        if len(paths) <= 1:
            continue
        duplicate_groups.append(DuplicateFileGroup(sha256=digest, paths=tuple(sorted(paths))))

    duplicate_groups.sort(key=lambda group: (len(group.paths), group.paths))
    return tuple(duplicate_groups)


def _check_modules(required_modules: Sequence[str]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    imported: list[str] = []
    missing: list[str] = []

    for module_name in required_modules:
        try:
            importlib.import_module(module_name)
        except ImportError:
            missing.append(module_name)
            continue
        imported.append(module_name)

    return tuple(imported), tuple(missing)


def scan_repository_integrity(
    project_root: Path | str,
    *,
    required_modules: Sequence[str] = DEFAULT_REQUIRED_MODULES,
    scan_dirs: Sequence[str] = DEFAULT_SCAN_DIRS,
) -> IntegrityReport:
    """Run repository-level integrity checks.

    Checks:
    1. Core architecture modules are importable.
    2. No duplicated file contents across selected repository directories.
    """
    root = Path(project_root).resolve()
    imported_modules, missing_modules = _check_modules(required_modules)
    duplicate_groups = _find_duplicate_content_groups(root, scan_dirs)
    scanned_files = sum(1 for _ in _iter_scannable_files(root, scan_dirs))

    return IntegrityReport(
        imported_modules=imported_modules,
        missing_modules=missing_modules,
        duplicate_groups=duplicate_groups,
        scanned_files=scanned_files,
    )


def format_integrity_report(report: IntegrityReport) -> str:
    """Create a human-readable report for CLI/log output."""
    lines: list[str] = [
        "Repository Integrity Report",
        "==========================",
        f"Imported modules: {len(report.imported_modules)}",
        f"Missing modules: {len(report.missing_modules)}",
        f"Scanned files: {report.scanned_files}",
        f"Duplicate groups: {len(report.duplicate_groups)}",
        f"Overall status: {'PASS' if report.ok else 'FAIL'}",
    ]
    if report.missing_modules:
        lines.append("")
        lines.append("Missing modules:")
        lines.extend(f"- {module}" for module in report.missing_modules)
    if report.duplicate_groups:
        lines.append("")
        lines.append("Duplicate file-content groups:")
        for group in report.duplicate_groups:
            lines.append(f"- sha256={group.sha256}")
            lines.extend(f"  - {path}" for path in group.paths)
    return "\n".join(lines)
