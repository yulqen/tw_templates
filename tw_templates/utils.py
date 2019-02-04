from datetime import datetime

import parsedatetime as pdt


def date_parser(d: str):
    cal = pdt.Calendar()
    time_struct, parse_status = cal.parse(d)
    return datetime(*time_struct[:3]).isoformat() + "Z"
