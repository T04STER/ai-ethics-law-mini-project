import os
import sys

from google import genai

from .classifier import classify_license
from .constants import LICENSE_TO_CATEGORY, LicenseCategory

SYSTEM_INSTRUCTION = (
    "You are a legal and ethical AI advisor for software projects. "
    "The user runs a dependency license scanner. Given a list of flagged "
    "packages with their licenses, explain in Polish:\n"
    "1. Why this warning was raised (what makes the license risky).\n"
    "2. What it means for the project (obligations, risks, AI Act / RODO implications).\n"
    "Keep answers concise and actionable."
)


def _get_client() -> genai.Client:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print(
            "ERROR: GOOGLE_API_KEY is not set. "
            "Export it before using --ai-explain:\n"
            "  export GOOGLE_API_KEY='your-key'",
            file=sys.stderr,
        )
        sys.exit(1)
    return genai.Client(api_key=api_key)


def _collect_warnings(
    licenses: dict[str, str],
    root_label: str = "project",
) -> list[str]:
    """Collect human-readable warning lines from scanned licenses."""
    warnings: list[str] = []

    for package, license_str in sorted(licenses.items()):
        if package == root_label:
            continue
        lic_enum = classify_license(license_str)
        cat = LICENSE_TO_CATEGORY.get(lic_enum, LicenseCategory.UNKNOWN)

        if cat == LicenseCategory.COPYLEFT:
            warnings.append(
                f"[COPYLEFT] {package} — {license_str}: "
                "copyleft license detected, distribution requires "
                "releasing source code under the same license."
            )
        elif cat == LicenseCategory.WEAK_COPYLEFT:
            warnings.append(
                f"[WEAK COPYLEFT] {package} — {license_str}: "
                "weak copyleft license, modifications to this library "
                "must be shared under the same license."
            )
        elif cat == LicenseCategory.PROPRIETARY:
            warnings.append(
                f"[PROPRIETARY] {package} — {license_str}: "
                "proprietary license, usage may be restricted."
            )
        elif cat == LicenseCategory.UNKNOWN:
            warnings.append(
                f"[UNKNOWN] {package} — {license_str}: "
                "license could not be classified."
            )

    return warnings


def explain_warnings(
    licenses: dict[str, str],
    root_label: str = "project",
) -> str | None:
    """Send collected warnings to Gemini and return the explanation."""
    warnings = _collect_warnings(licenses, root_label)
    if not warnings:
        return None

    client = _get_client()
    prompt = (
        "The following license warnings were raised by the scanner:\n\n"
        + "\n".join(warnings)
        + "\n\nExplain each warning and its implications for the project."
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.3,
            max_output_tokens=2048,
        ),
    )
    return response.text
