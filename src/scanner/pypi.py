import re
import time
import requests

_pypi_cache: dict[str, dict] = {}

def fetch_pypi_info(package: str) -> dict:
    """Return {'license': str, 'deps': [str]} for a package from PyPI."""
    if package in _pypi_cache:
        return _pypi_cache[package]

    url = f"https://pypi.org/pypi/{package}/json"
    try:
        r = requests.get(url, timeout=8)
        if r.status_code != 200:
            result = {"license": "Unknown", "deps": []}
        else:
            data = r.json()
            info = data.get("info", {})
            license_str = info.get("license") or ""
            # Sometimes license field is empty but present in classifiers
            if not license_str or license_str.lower() in ("unknown", "none", ""):
                for clf in info.get("classifiers", []):
                    if clf.startswith("License"):
                        # e.g. "License :: OSI Approved :: MIT License"
                        license_str = clf.split("::")[-1].strip()
                        break
            license_str = license_str or "Unknown"

            # Extract dependencies from requires_dist
            requires = info.get("requires_dist") or []
            deps = []
            for req in requires:
                # "requests>=2.0 ; extra == 'dev'" → "requests"
                m = re.match(r"^([A-Za-z0-9_.\-]+)", req)
                if m:
                    dep_name = m.group(1).lower().replace("_", "-")
                    # Skip optional/conditional extras
                    if "extra ==" not in req:
                        deps.append(dep_name)
            result = {"license": license_str, "deps": deps}
    except Exception as e:
        result = {"license": f"Error: {e}", "deps": []}

    _pypi_cache[package] = result
    time.sleep(0.05)  # polite rate-limiting
    return result
