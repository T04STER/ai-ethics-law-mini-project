import json
import re
from pathlib import Path

def parse_pyproject(path: Path) -> list[str]:
    try:
        import tomllib  # Python 3.11+
    except ImportError:
        import tomli as tomllib # type: ignore
        
    with open(path, "rb") as f:
        data = tomllib.load(f)
    deps_raw = data.get("project", {}).get("dependencies", [])
    packages = []
    for d in deps_raw:
        m = re.match(r"^([A-Za-z0-9_.\-]+)", d)
        if m:
            packages.append(m.group(1).lower().replace("_", "-"))
    return packages

def parse_requirements(path: Path) -> list[str]:
    packages = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        m = re.match(r"^([A-Za-z0-9_.\-]+)", line)
        if m:
            packages.append(m.group(1).lower().replace("_", "-"))
    return packages

def parse_package_json(path: Path) -> list[str]:
    data = json.loads(path.read_text())
    deps: dict = {}
    deps.update(data.get("dependencies", {}))
    deps.update(data.get("devDependencies", {}))
    return list(deps.keys())

def find_dependencies(directory: Path) -> list[str]:
    """Scan directory for dependency files and return a deduplicated package list."""
    packages: list[str] = []

    for filename in ("pyproject.toml", "requirements.txt", "requirements-dev.txt"):
        p = directory / filename
        if p.exists():
            print(f"  [+] Found: {p.name}")
            if filename == "pyproject.toml":
                packages += parse_pyproject(p)
            else:
                packages += parse_requirements(p)

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique = []
    for pkg in packages:
        if pkg not in seen:
            seen.add(pkg)
            unique.append(pkg)
    return unique
