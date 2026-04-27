import json
from collections import Counter
from .classifier import classify_license
from .constants import License, LicenseCategory, LICENSE_TO_CATEGORY

def print_table(
    licenses: dict[str, str],
    depths: dict[str, int] | None = None,
    root_label: str = "project",
    file=None,
) -> None:
    def out(line: str = "") -> None:
        print(line, file=file)

    out("\n" + "═" * 78)
    out(f"  {'PACKAGE':<35} {'LICENSE':<25} {'D':>3}  CATEGORY")
    out("═" * 78)

    icon_map = {
        LicenseCategory.PERMISSIVE: "✓",
        LicenseCategory.WEAK_COPYLEFT: "△",
        LicenseCategory.COPYLEFT: "✗",
        LicenseCategory.PROPRIETARY: "⚠",
        LicenseCategory.UNKNOWN: "?"
    }

    for package, license_str in sorted(licenses.items()):
        if package == root_label:
            continue

        lic_enum = classify_license(license_str)
        cat = LICENSE_TO_CATEGORY.get(lic_enum, LicenseCategory.UNKNOWN)
        icon = icon_map.get(cat, "?")

        # Truncate long license names for table readability
        lic_display = (license_str[:22] + "...") if len(license_str) > 25 else license_str
        lic_display = lic_display.replace("\n", " ")

        depth_str = str(depths[package]) if depths and package in depths else "-"
        out(f"  {package:<35} {lic_display:<25} {depth_str:>3}  {icon} {cat.value}")
    out("═" * 78)

    # Summary by Category
    categories = Counter(
        LICENSE_TO_CATEGORY.get(classify_license(v), LicenseCategory.UNKNOWN)
        for k, v in licenses.items() if k != root_label
    )
    out("\n  Summary by Category:")
    for cat, n in sorted(categories.items(), key=lambda x: x[0].value):
        out(f"    {cat.value:<20}: {n}")

    # Legal warnings for copyleft packages
    copyleft_packages = [
        p for p, l in licenses.items()
        if p != root_label and LICENSE_TO_CATEGORY.get(classify_license(l)) == LicenseCategory.COPYLEFT
    ]
    if copyleft_packages:
        out(f"\n  WARNING (copyright / AI Act): Copyleft licenses detected:")
        for p in copyleft_packages:
            out(f"     • {p} — {licenses[p]}")
        out("     → Distribution requires releasing source code under the same license.")
    out()


def write_jsonl(
    licenses: dict[str, str],
    depths: dict[str, int] | None = None,
    root_label: str = "project",
    file=None,
) -> None:
    for package, license_str in sorted(licenses.items()):
        if package == root_label:
            continue
        lic_enum = classify_license(license_str)
        cat = LICENSE_TO_CATEGORY.get(lic_enum, LicenseCategory.UNKNOWN)
        record = {
            "package": package,
            "license": license_str,
            "depth": depths[package] if depths and package in depths else None,
            "category": cat.value,
        }
        print(json.dumps(record, ensure_ascii=False), file=file)
