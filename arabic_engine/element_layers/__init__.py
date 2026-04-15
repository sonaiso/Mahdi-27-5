"""النموذج الطبقي الصارم — Strict 7-Layer Arabic Phonological Analysis.

This package implements a strict layered model (Layer 0 → Layer 6) for
analysing Arabic sounds and letters, from mental primitives through
generative, auditory, structural, transformation and judgment layers
to a final programmatic representation.

Each layer must pass a *transition gate* before the element may
advance to the next layer.  The governing criterion throughout is
**reality-match** (مطابقة واقع العربية).
"""
