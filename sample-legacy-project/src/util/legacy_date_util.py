"""Legacy date formatting utility."""
import datetime

def format_fiscal_month_end(dt: datetime.date) -> str:
    """Old fiscal calendar helper with no direct static call sites."""
    return dt.strftime("%Y-Q%m-EOM")

def parse_julian_batch_date(julian_str: str) -> datetime.date:
    """Parse legacy YYYYDDD format."""
    year = int(julian_str[:4])
    days = int(julian_str[4:])
    return datetime.date(year, 1, 1) + datetime.timedelta(days=days - 1)

