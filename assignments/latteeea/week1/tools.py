from langchain_core.tools import tool
from typing import Optional
from mock_data import TROUBLESHOOTING_NOTES

NOTE_BY_ID = {note["id"]: note for note in TROUBLESHOOTING_NOTES}

@tool
def search_notes(
  query: str,
  category: Optional[str] = None,
  min_blog_value: Optional[int] = None,
) -> list[dict]:
  query_lower = query.lower()
  results = []

  for note in TROUBLESHOOTING_NOTES:
    if category and note["category"] != category:
      continue

    if min_blog_value and note["blog_value"] < min_blog_value:
      continue

    searchable_fields = {
      "title": note.get("title", ""),
      "category": note.get("category", ""),
      "tech_stack": " ".join(note.get("tech_stack", [])),
      "symptom": note.get("symptom", ""),
      "root_cause": note.get("root_cause", ""),
      "content_angle": note.get("content_angle", ""),
      "structural_insight": note.get("structural_insight", ""),
    }

    matched_fields = [
      field for field, value in searchable_fields.items()
      if query_lower in value.lower()
    ]

    if matched_fields:
      results.append({
          "id": note["id"],
          "title": note["title"],
          "category": note["category"],
          "matched_fields": matched_fields,
          "summary": note["structural_insight"],
          "blog_value": note["blog_value"],
      })

  return results

@tool
def get_note_detail(note_id: str) -> dict:
  note = NOTE_BY_ID.get(note_id)

  if not note:
    return {
      "error": f"Note not found: {note_id}",
      "available_ids": list(NOTE_BY_ID.keys()),
    }
  
  return {
    "id": note["id"],
    "title": note["title"],
    "timeline": note["timeline"],
    "investigation_steps": note["investigation_steps"],
    "root_cause": note["root_cause"],
    "solution": note["solution"],
    "structural_insight": note["structural_insight"],
    "evidence": note["evidence"],
    "content_angle": note["content_angle"],
    "blog_value": note["blog_value"],
  }

@tool
def generate_narrative_outline(
  note_id: str,
  target_reader: str = "junior_backend_engineer"
) -> dict:
  note = NOTE_BY_ID.get(note_id)

  if not note:
    return {
      "error": f"Note not found: {note_id}",
      "available_ids": list(NOTE_BY_ID.keys()),
    }
  
  wrong_or_partial_hypothesis = [
    step["hypothesis"]
    for step in note["investigation_steps"]
    if step["result"] in ["rejected", "'partial"]
  ]

  confirmed_finidings = [
    step["observation"]
    for step in note["investigation_steps"]
    if step["result"] == "confirmed"
  ]

  return {
    "note_id": note["id"],
    "target_reader": target_reader,
    "title": note["title"],
    "hook": note["symptom"],
    "problem_context": note["impact"],
    "debugging_flow": {
      "timeline": note["timeline"],
      "wrong_or_partial_hypothesis": wrong_or_partial_hypothesis,
      "confirmed_findings": confirmed_finidings,
    },
    "root_cause_section": note["root_cause"],
    "solution_section": note["solution"],
    "lessons": note["structural_insight"],
    "closing": note["content_angle"],
    "evidence": note["evidence"],
  }

TOOLS = [search_notes, get_note_detail, generate_narrative_outline]