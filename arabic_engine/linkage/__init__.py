"""Linkage layer — الرابطة: dalāla validation.

Public sub-modules
------------------
* :mod:`arabic_engine.linkage.dalala` — Validates the signification link
  between a signifier (lexical closure) and its signified (concept node),
  covering mutābaqa (مطابقة), taḍammun (تضمن), iltizām (التزام), and
  isnād (إسناد) modes.
* :mod:`arabic_engine.linkage.semantic_roles` — derives semantic role
  labels (event, agent, patient, time, place) from syntax output.
"""

__all__ = ["dalala", "semantic_roles"]
