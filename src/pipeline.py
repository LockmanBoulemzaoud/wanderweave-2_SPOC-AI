import pandas as pd
from utils import haversine_km, minutes, fmt_time

def load_pois(csv_path, city):
    df = pd.read_csv(csv_path, encoding="utf-8", encoding_errors="replace")
    return df[df['city'].str.lower() == city.lower()].copy()


def _topic_match(row, topics):
    tags = set(str(row['tags']).lower().replace(" ","").split(","))
    topics = set(t.lower() for t in topics)
    return len(tags.intersection(topics))/max(1,len(topics))

def score_pois(df, topics, hidden_weight=0.2):
    df = df.copy()
    df['topic_match'] = df.apply(lambda r: _topic_match(r, topics), axis=1)
    w_topic, w_hidden, w_pop = 0.6, hidden_weight, 0.4-hidden_weight
    df['score'] = w_topic*df['topic_match'] + w_hidden*(1-df['popularity']) + w_pop*df['popularity']
    return df.sort_values('score', ascending=False)


def is_valid_visit(t_arrive_min, t_end_min, opening_hours_str):
    """
    Checks if an entire visit (from arrival to end) is valid within opening hours.
    """
    if not opening_hours_str or pd.isna(opening_hours_str):
        return True  # Assume open if no data

    try:
        for r in opening_hours_str.split('|'):
            start_str, end_str = r.split('-')
            start_min = minutes(start_str)
            end_min = minutes(end_str)

            # Handle "24:00" or "00:00" as end of day
            if end_min == 0 and start_min > 0:
                end_min = 1440  # 24 * 60

            # Handle midnight crossover (e.g., 22:00-05:00)
            if end_min <= start_min:
                end_min += 1440  # Add 24h

            # We need to check if the visit times also need to wrap
            t_arrive_check = t_arrive_min
            t_end_check = t_end_min

            # If arrival is "next day" (e.g., 01:00) for a 22:00-05:00 slot
            if t_arrive_min < start_min:
                t_arrive_check += 1440
                t_end_check += 1440

            # The new, correct check:
            # 1. Arrive AT or AFTER opening
            # 2. Leave AT or BEFORE closing
            if (t_arrive_check >= start_min) and (t_end_check <= end_min):
                return True

    except Exception as e:
        print(f"Error parsing opening hours: {opening_hours_str}, Error: {e}")
        return False  # Fail safe

    return False


def plan_day(df_sorted, start_hhmm="09:30", end_hhmm="20:00", speed_kmh=4.0):
    start = minutes(start_hhmm)
    end = minutes(end_hhmm)

    route = []
    visited_pois = set()  # 跟踪已访问的景点
    tcur = start  # 当前时间
    if df_sorted.empty:
        return pd.DataFrame(route)  # 如果没有景点，直接返回空行程
    avg_lat = df_sorted['lat'].mean()
    avg_lon = df_sorted['lon'].mean()
    cur_lat, cur_lon = (avg_lat, avg_lon)

    while tcur < end:
        found = False
        # 遍历所有排序后的景点
        for poi_id, r in df_sorted.iterrows():
            if poi_id in visited_pois:
                continue  # 跳过已访问

            # 1. 计算旅行时间
            dist = haversine_km(cur_lat, cur_lon, r['lat'], r['lon'])
            t_travel = int((dist / speed_kmh) * 60)
            t_arrive = tcur + t_travel

            # --- 新功能：弹性游玩时间 ---
            base_duration = r['duration_min']
            if pd.isna(base_duration): base_duration = 60  # 默认值

            if base_duration < 30:
                min_visit = int(base_duration)  # 不能压缩
                max_visit = int(base_duration * 1.5)  # 可以延长50%
            else:
                min_visit = int(base_duration * 0.8)  # 最快压缩20%
                max_visit = int(base_duration * 1.2)  # 最多延长20%

            # 2. 检查当天是否还有足够时间（即使是最快的游玩）
            time_remaining_in_day = end - t_arrive
            if time_remaining_in_day < min_visit:
                continue  # 当天时间不够了

            # 3. 检查营业时间 (修复了错误并加入了弹性逻辑)
            opening_hours_str = r['open']
            if pd.isna(opening_hours_str): opening_hours_str = "00:00-24:00"  # 假设全天开放

            is_open = False
            actual_t_end = 0
            actual_duration = 0

            for r_str in opening_hours_str.split('|'):
                try:
                    start_str, end_str = r_str.split('-')
                    start_min = minutes(start_str)
                    end_min = minutes(end_str)
                    if end_min == 0: end_min = 1440  # 24:00

                    # 3a. 计算等待时间 (如果早到了)
                    t_wait = 0
                    if t_arrive < start_min:
                        t_wait = start_min - t_arrive

                    t_arrive_actual = t_arrive + t_wait  # 加上等待时间后的实际进入时间

                    # 3b. 重新检查时间
                    time_til_close = end_min - t_arrive_actual
                    time_remaining_in_day_after_wait = end - t_arrive_actual

                    # 检查是否还有足够时间（在关门前 或 一天结束前）
                    if time_til_close < min_visit or time_remaining_in_day_after_wait < min_visit:
                        continue  # 时间不够了

                    # 3c. 核心逻辑：我们找到了一个可行的时段
                    # 我们能用的时间 = min(到关门的时间, 到一天结束的时间)
                    available_time = min(time_til_close, time_remaining_in_day_after_wait)

                    # 我们的实际游玩时间 = min(我们能用的时间, 我们想玩的最长时间)
                    # (我们使用 int() 来确保是整数分钟)
                    actual_duration = int(min(available_time, max_visit))

                    # 确保实际游玩时间不短于我们的最短时间
                    if actual_duration < min_visit:
                        continue  # 即使有空，但空闲时间太短，不满足最小游玩要求

                    # 成功！
                    is_open = True
                    actual_t_end = t_arrive_actual + actual_duration
                    break  # 找到了一个可行的营业时间段

                except Exception:
                    continue  # 解析时间出错，跳过这个时间段

            # 4. 如果找到了可行的景点，则添加到行程
            if is_open:
                route.append({
                    "time_start": fmt_time(t_arrive_actual),
                    "time_end": fmt_time(actual_t_end),
                    "duration_actual": actual_duration,  # 添加实际游玩时间
                    "name": r['name'],
                    "category": r['category'],
                    "hidden": int(r['hidden']),
                    "popularity": float(r['popularity']),
                    "tags": r['tags'],
                    "price_eur": r['price_eur']
                })
                tcur = actual_t_end  # 更新当前时间
                cur_lat, cur_lon = r['lat'], r['lon']  # 更新当前位置
                visited_pois.add(poi_id)  # 标记为已访问
                found = True
                break  # 停止搜索景点，进入下一个时间循环

        if not found:
            # 如果遍历完所有景点都找不到合适的，则结束
            break

    return pd.DataFrame(route)

def build_itinerary(csv_path, city, topics, mode="solo", hidden_ratio=0.3, start_hhmm="09:30", end_hhmm="20:00"):
    df = load_pois(csv_path, city)
    if mode == "rencontres":
        df['popularity'] = df.apply(lambda r: r['popularity']*1.0 if r['category'] not in ['walk','food_drink','street'] else min(1.0, r['popularity']+0.1), axis=1)
    df_scored = score_pois(df, topics, hidden_weight=hidden_ratio)
    itin = plan_day(df_scored, start_hhmm=start_hhmm, end_hhmm=end_hhmm)
    return itin