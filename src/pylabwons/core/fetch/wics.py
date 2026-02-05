# WISE INDUSTRY CLASSIFICATION SYSTEM
from pylabwons.schema import wics as SCHEMA
import re, requests


class wiseICS:

    def __init__(self):
        return

    @classmethod
    def fetch_date(cls) -> str:
        return re.compile(r"var\s+dt\s*=\s*'(\d{8})'") \
            .search(requests.get(SCHEMA.URL.BASE).text) \
            .group(1)