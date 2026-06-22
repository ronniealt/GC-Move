from __future__ import annotations
from typing import Optional

from app.models.family import Family, FamilyMember, FamilyPreference


def build_system_prompt(
    family: Family,
    members: list[FamilyMember],
    preferences: list[FamilyPreference],
    property_context: Optional[str] = None,
) -> str:
    member_lines: list[str] = []
    for m in members:
        if m.role == "pet":
            member_lines.append(f"  - {m.first_name} (pet)")
        else:
            age_str = f", age {m.age}" if m.age else ""
            role_label = m.role.replace("_", " ").title()
            member_lines.append(f"  - {m.first_name} ({role_label}{age_str})")
    members_text = "\n".join(member_lines) or "  (no members recorded)"

    budget_parts: list[str] = []
    if family.budget_min_aud and family.budget_max_aud:
        budget_parts.append(f"Budget: ${family.budget_min_aud:,} – ${family.budget_max_aud:,}")
    elif family.budget_max_aud:
        budget_parts.append(f"Budget: up to ${family.budget_max_aud:,}")
    if family.target_move_date:
        budget_parts.append(f"Target move: {family.target_move_date.strftime('%B %Y')}")
    budget_text = " | ".join(budget_parts) or "Budget not yet set."

    pref_lines: list[str] = []
    for p in preferences[:6]:
        pref_lines.append(f"  - {p.attribute} (weight {float(p.current_weight):.1f}/5, {p.status})")
    pref_text = "\n".join(pref_lines) or "  (no preferences recorded yet)"

    prompt = f"""You are the Gold Coast Move OS AI Advisor — a calm, knowledgeable, and honest family relocation consultant.

FAMILY: {family.display_name}
MEMBERS:
{members_text}

SCORING WEIGHTS (reflects what this family values):
  Community {float(family.weight_community):.0%} | Lifestyle {float(family.weight_lifestyle):.0%} | Schools {float(family.weight_school):.0%} | Property {float(family.weight_property):.0%} | Financial {float(family.weight_financial):.0%}

{budget_text}

TOP PREFERENCES:
{pref_text}
"""

    if property_context:
        prompt += f"\n{property_context}\n"

    prompt += """
GUIDANCE:
- Reference family members by name when relevant. Be personal, not generic.
- Be honest about trade-offs. This family values trusted advice over enthusiasm.
- Keep responses focused and practical — concise paragraphs, not bullet walls.
- Never invent property data. If you don't have specifics, say so.
- The core question you help answer: "Will this family have a better life here in five years?"
"""
    return prompt.strip()
