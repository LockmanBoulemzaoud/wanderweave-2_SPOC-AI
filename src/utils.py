from math import radians, sin, cos, asin, sqrt

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2*asin(sqrt(a))
    return R*c

def parse_hhmm(s):
    h,m = s.split(":")
    return int(h), int(m)

def minutes(hhmm):
    h,m = parse_hhmm(hhmm)
    return h*60 + m

def fmt_time(total_min):
    h = total_min // 60
    m = total_min % 60
    return f"{h:02d}:{m:02d}"