from .constants import License

SPDX_MAP: dict[str, License] = {
    "mit": License.MIT,
    "apache-2.0": License.APACHE,
    "apache 2.0": License.APACHE,
    "apache-1.1": License.APACHE,
    "gpl-2.0": License.GPL,
    "gpl-2.0-only": License.GPL,
    "gpl-2.0-or-later": License.GPL,
    "gpl-3.0": License.GPL,
    "gpl-3.0-only": License.GPL,
    "gpl-3.0-or-later": License.GPL,
    "agpl-3.0": License.AGPL,
    "agpl-3.0-only": License.AGPL,
    "agpl-3.0-or-later": License.AGPL,
    "lgpl-2.0": License.LGPL,
    "lgpl-2.0-only": License.LGPL,
    "lgpl-2.1": License.LGPL,
    "lgpl-2.1-only": License.LGPL,
    "lgpl-2.1-or-later": License.LGPL,
    "lgpl-3.0": License.LGPL,
    "lgpl-3.0-only": License.LGPL,
    "lgpl-3.0-or-later": License.LGPL,
    "mpl-2.0": License.MPL,
    "mpl-1.1": License.MPL,
    "bsd-2-clause": License.BSD,
    "bsd-3-clause": License.BSD,
    "bsd-4-clause": License.BSD,
    "isc": License.ISC,
    "unlicense": License.PERMISSIVE_OTHER,
    "cc0-1.0": License.PERMISSIVE_OTHER,
    "cc0": License.PERMISSIVE_OTHER,
    "psf-2.0": License.PERMISSIVE_OTHER,
    "python-2.0": License.PERMISSIVE_OTHER,
    "artistic-2.0": License.PERMISSIVE_OTHER,
    "zlib": License.PERMISSIVE_OTHER,
    "wtfpl": License.PERMISSIVE_OTHER,
    "eupl-1.1": License.COPYLEFT_OTHER,
    "eupl-1.2": License.COPYLEFT_OTHER,
    "osl-3.0": License.COPYLEFT_OTHER,
    "cddl-1.0": License.WEAK_COPYLEFT_OTHER,
    "epl-1.0": License.WEAK_COPYLEFT_OTHER,
    "epl-2.0": License.WEAK_COPYLEFT_OTHER,
}


def classify_license(name: str) -> License:
    n = name.strip().lower()

    # 1. Exact SPDX / known-alias match
    if n in SPDX_MAP:
        return SPDX_MAP[n]

    # 2. Compound licenses (OR / AND) — take the first recognized part
    for sep in (" or ", " and "):
        if sep in n:
            for part in n.split(sep):
                result = classify_license(part.strip())
                if result != License.UNKNOWN:
                    return result

    # 3. Substring fallback — most specific substrings first to avoid mis-matches
    if "agpl" in n:
        return License.AGPL
    if "lgpl" in n:
        return License.LGPL
    if "gpl" in n:
        return License.GPL
    if "mpl" in n:
        return License.MPL
    if "mit" in n:
        return License.MIT
    if "apache" in n:
        return License.APACHE
    if "bsd" in n:
        return License.BSD
    if "isc" in n:
        return License.ISC
    if "unlicense" in n:
        return License.PERMISSIVE_OTHER
    if "cc0" in n:
        return License.PERMISSIVE_OTHER
    if "python" in n:
        return License.PERMISSIVE_OTHER
    if "psf" in n:
        return License.PERMISSIVE_OTHER
    if "eupl" in n:
        return License.COPYLEFT_OTHER
    if "cddl" in n:
        return License.WEAK_COPYLEFT_OTHER
    if "epl" in n:
        return License.WEAK_COPYLEFT_OTHER
    if "propriet" in n or "commercial" in n:
        return License.PROPRIETARY

    return License.UNKNOWN
