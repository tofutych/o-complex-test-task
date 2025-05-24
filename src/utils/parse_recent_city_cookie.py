def parse_recent_city_cookie(cookie: str | None):
    if cookie:
        parts = cookie.split(",")
        if len(parts) >= 2:
            return {"name": parts[0], "country": parts[1]}
    return None
