RESULT_FIELDS = ["legId", "route", "stopovers"]
TOTAL_FARE_FIELD = "totalFare"


def handle_query_4_new(flights):
    sum = flights.pop("sum")
    count = flights.pop("count")
    flights["avg"] = float(sum / count)
    return flights


def handle_query_4_register(register, dic):
    route = register.get("route")
    price = register.get(TOTAL_FARE_FIELD)
    route_flights = dic.get(route, {})
    if route_flights == {}:
        dic[route] = {
            "sum": float(price),
            "count": 1,
            "max": price,
            "route": route
        }
    else:
        max_price = route_flights.get("max")
        if price > max_price:
            route_flights["max"] = price
        route_flights["sum"] += float(price)
        route_flights["count"] += 1
    return dic
