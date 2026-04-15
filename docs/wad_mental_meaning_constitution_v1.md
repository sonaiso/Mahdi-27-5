# دستور الوضع والمعنى الذهني عند النبهاني v1

## Wad' and Mental Meaning Constitution v1

### Overview

This constitution governs the language layer (شطر اللغة) in
al-Nabhani's framework. It establishes that:

1. **Wad'** (الوضع) is the designation of a lafz (utterance) for a
   mental meaning — not for external reality directly.
2. **Mental Meaning** (المعنى الذهني) is what is established in the mind
   from the image, aspect, or relation of a thing.
3. **Wad' is a branch of Tasawwur** (الوضع فرع عن التصور) — no
   designation without prior conception.
4. **The highest purpose of Wad'** is to convey ratios/relations
   (إفادة النسب), not merely individual meanings.

### Governing Chain (Art. 37)

```
واقع/خبر → إدراك → معلومات سابقة → ربط → تمييز → تصور
→ وضع/لغة/نسب → ضبط دلالي → تحرير موضوع → جهة حكم → حكم
```

Language occupies the position **وضع/لغة/نسب** — after tasawwur
(conception), before semantic grounding and judgement.

### Mathematical Representation (Art. 43)

```
T → W → M → R → E
```

Where:
- **T** = Tasawwur (التصور) — Conception
- **W** = Wad' (الوضع) — Designation
- **M** = Mental Meaning (المعنى الذهني)
- **R** = Ratios/Relations (النسب)
- **E** = Expression (التعبير)

### Anti-Jump Rules (Art. 40–42)

Five prohibited jumps:

1. Lafz → complete meaning without tasawwur
2. Lafz → external reality without mental meaning
3. Language → judgement without method of reason
4. Wad' → external reality directly without mental mediation
5. Individual words → complete expression without ratios

### Module

Implemented in `arabic_engine/linkage/wad_constitution.py`.

### Public API

- `build_wad_record()` — Build a Wad' designation record
- `build_mental_meaning()` — Build a mental meaning record
- `build_nisba()` — Build a ratio/relation record
- `check_wad_jump()` — Check a single anti-jump condition
- `check_all_wad_jumps()` — Check all prohibited jumps
- `validate_wad_chain()` — Validate T → W → M → R → E chain
- `validate_wad_constitution()` — Full constitution validation

### Types

- `WadRecord` — Wad' designation record (frozen dataclass)
- `MentalMeaningRecord` — Mental meaning record (frozen dataclass)
- `NisbaRecord` — Ratio/relation record (frozen dataclass)
- `WadJumpCheckResult` — Anti-jump check result (frozen dataclass)
- `WadConstitutionResult` — Full validation result (frozen dataclass)

### Enums

- `WadElement` — Constitutive elements of Wad' (lafz, meaning,
  takhsis, comprehensibility)
- `MentalMeaningSource` — How a mental meaning arises
- `ExpressionMode` — Mode of expression (lafz, ishara, mithal)
- `NisbaType` — Types of ratios/relations
- `WadJumpViolation` — Prohibited jump types
