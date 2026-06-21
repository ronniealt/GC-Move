QUALITATIVE_SYSTEM_PROMPT = (
    "You are evaluating a property listing to estimate qualitative attributes "
    "not available in structured data. Return ONLY a valid JSON object with the "
    "specified keys. Do not include any explanation or markdown."
)

QUALITATIVE_USER_PROMPT = """LISTING DESCRIPTION:
{description}

FEATURES LIST:
{features}

Estimate the following attributes on a 0–10 scale. Return a JSON object with exactly these keys:
- "modernity": How modern does this property appear? (10 = brand new/fully renovated, 1 = very dated)
- "design_quality": How architecturally distinguished? (10 = custom architect-designed, 1 = standard spec build)
- "indoor_outdoor_flow": How well does the layout connect indoor/outdoor spaces? (10 = seamless flow, 1 = no connection)
- "home_office_suitability": Is there a dedicated or suitable home office space? (10 = dedicated room, 5 = possible, 1 = no)
- "entertaining_space": How suitable for entertaining? (10 = pool + outdoor kitchen + large alfresco, 1 = none)
- "privacy": Estimated privacy from description and block characteristics (10 = very private, 1 = no privacy)

If you cannot estimate a score confidently from the description alone, return null for that key.
Return only JSON — no markdown, no explanation."""
