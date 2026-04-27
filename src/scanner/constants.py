from enum import Enum

class LicenseCategory(Enum):
    PERMISSIVE = "Permissive"
    COPYLEFT = "Copyleft"
    WEAK_COPYLEFT = "Weak Copyleft"
    PROPRIETARY = "Proprietary"
    UNKNOWN = "Unknown"

class License(Enum):
    MIT = "MIT"
    APACHE = "Apache"
    BSD = "BSD"
    ISC = "ISC"
    GPL = "GPL"
    AGPL = "AGPL"
    LGPL = "LGPL"
    MPL = "MPL"
    PROPRIETARY = "Proprietary"
    PERMISSIVE_OTHER = "Permissive (other)"
    COPYLEFT_OTHER = "Copyleft (other)"
    WEAK_COPYLEFT_OTHER = "Weak Copyleft (other)"
    UNKNOWN = "Unknown"

# Mapping specific licenses to their legal categories
LICENSE_TO_CATEGORY = {
    License.MIT: LicenseCategory.PERMISSIVE,
    License.APACHE: LicenseCategory.PERMISSIVE,
    License.BSD: LicenseCategory.PERMISSIVE,
    License.ISC: LicenseCategory.PERMISSIVE,
    License.PERMISSIVE_OTHER: LicenseCategory.PERMISSIVE,
    License.GPL: LicenseCategory.COPYLEFT,
    License.AGPL: LicenseCategory.COPYLEFT,
    License.COPYLEFT_OTHER: LicenseCategory.COPYLEFT,
    License.LGPL: LicenseCategory.WEAK_COPYLEFT,
    License.MPL: LicenseCategory.WEAK_COPYLEFT,
    License.WEAK_COPYLEFT_OTHER: LicenseCategory.WEAK_COPYLEFT,
    License.PROPRIETARY: LicenseCategory.PROPRIETARY,
    License.UNKNOWN: LicenseCategory.UNKNOWN,
}

# License category colors
LICENSE_COLOR = {
    LicenseCategory.PERMISSIVE:    "#4caf50",   # green
    LicenseCategory.COPYLEFT:      "#f44336",   # red
    LicenseCategory.WEAK_COPYLEFT: "#ff9800",   # orange
    LicenseCategory.PROPRIETARY:   "#9c27b0",   # purple
    LicenseCategory.UNKNOWN:       "#9e9e9e",   # grey
}
