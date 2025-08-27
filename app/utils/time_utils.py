"""
Utilitários de tempo para o sistema SDR IA
"""
from datetime import datetime, time, timedelta
import pytz
from app.config import settings


def get_period_of_day(timezone: str = "America/Sao_Paulo") -> str:
    """
    Retorna o período do dia (Manhã, Tarde, Noite).
    """
    try:
        tz = pytz.timezone(timezone)
        current_hour = datetime.now(tz).hour
        if 5 <= current_hour < 12:
            return "Manhã"
        elif 12 <= current_hour < 18:
            return "Tarde"
        else:
            return "Noite"
    except Exception:
        current_hour = datetime.now().hour
        if 5 <= current_hour < 12:
            return "Manhã"
        elif 12 <= current_hour < 18:
            return "Tarde"
        else:
            return "Noite"


def adjust_datetime_to_business_hours(dt: datetime) -> datetime:
    """
    Ajusta um datetime para estar dentro do horário comercial (08:00-20:00)
    e em dias úteis (seg-sex).
    """
    try:
        tz = pytz.timezone(settings.timezone)
    except (pytz.UnknownTimeZoneError, AttributeError):
        tz = pytz.timezone("America/Sao_Paulo")
    dt = tz.localize(dt) if dt.tzinfo is None else dt.astimezone(tz)
    business_start = time(8, 0)
    business_end = time(20, 0)
    if dt.weekday() >= 5:
        days_to_monday = 7 - dt.weekday()
        return (dt + timedelta(days=days_to_monday)).replace(
            hour=business_start.hour, minute=business_start.minute,
            second=0, microsecond=0
        )
    if dt.time() < business_start:
        return dt.replace(
            hour=business_start.hour, minute=business_start.minute,
            second=0, microsecond=0
        )
    if dt.time() > business_end:
        next_day = dt + timedelta(days=1)
        if next_day.weekday() >= 5:
            days_to_monday = 7 - next_day.weekday()
            next_day += timedelta(days=days_to_monday)
        return next_day.replace(
            hour=business_start.hour, minute=business_start.minute,
            second=0, microsecond=0
        )
    return dt


def get_business_aware_datetime(
    minutes_from_now: int = 0, hours_from_now: int = 0
) -> datetime:
    """
    Retorna um datetime ajustado para horário comercial.
    """
    try:
        tz = pytz.timezone(settings.timezone)
    except (pytz.UnknownTimeZoneError, AttributeError):
        tz = pytz.timezone("America/Sao_Paulo")
    now_with_tz = datetime.now(tz)
    target_time = now_with_tz + timedelta(
        minutes=minutes_from_now, hours=hours_from_now
    )
    return adjust_datetime_to_business_hours(target_time)
