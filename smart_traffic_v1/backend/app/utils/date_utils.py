from datetime import datetime, timezone
from typing import Optional


def format_datetime(dt: Optional[datetime]) -> Optional[str]:
    """
    将 datetime 对象格式化为带时区信息的 ISO 8601 字符串。
    
    如果 datetime 对象没有时区信息，假设它是 UTC 时间。
    返回的字符串格式为：YYYY-MM-DDTHH:MM:SS.ffffff+00:00
    
    Args:
        dt: datetime 对象，可为 None
        
    Returns:
        带时区信息的 ISO 8601 字符串，或 None
    """
    if dt is None:
        return None
    
    if dt.tzinfo is None:
        # 如果没有时区信息，假设是 UTC 时间
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        # 转换为 UTC 时间
        dt = dt.astimezone(timezone.utc)
    
    return dt.isoformat()
