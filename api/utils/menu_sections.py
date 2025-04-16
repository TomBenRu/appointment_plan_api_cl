"""
Module für die Definition von Menü-Abschnitten in der Web-Anwendung.
"""
from enum import Enum
from typing import NamedTuple


class MenuTemplates(NamedTuple):
    """Struktur für Desktop- und Mobile-Menü-Templates"""
    desktop: str
    mobile: str


class MenuDisplaySection(Enum):
    """
    Enum für die verschiedenen Menübereiche der Web-Anwendung.
    Jeder Bereich entspricht einem Tuple aus Desktop- und Mobile-Template-Pfad.
    """
    NONE = MenuTemplates(
        desktop="menus/none.html",
        mobile="menus/none_mobile.html"
    )
    CALENDAR = MenuTemplates(
        desktop="menus/calendar.html",
        mobile="menus/calendar_mobile.html"
    )
    PLANNING = MenuTemplates(
        desktop="menus/planning.html",
        mobile="menus/planning_mobile.html"
    )
    
    # Weitere Bereiche können später hinzugefügt werden
    # REPORTING = MenuTemplates("menus/reporting.html", "menus/reporting_mobile.html")
    # ADMIN = MenuTemplates("menus/admin.html", "menus/admin_mobile.html")
