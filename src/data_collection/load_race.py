import fastf1

fastf1.Cache.enable_cache("cache")

session = fastf1.get_session(
    2024,
    "Monaco",
    "R"
)

session.load()

print(session.results.head())