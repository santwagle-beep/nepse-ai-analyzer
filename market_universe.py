import requests

GITHUB_API = (
    "https://api.github.com/repos/"
    "binayabaral/nepal-market-data/contents/data/nepse"
)


def get_symbols():

    response = requests.get(
        GITHUB_API,
        timeout=30
    )

    response.raise_for_status()

    files = response.json()

    symbols = []

    for item in files:

        name = item.get("name", "")

        if not name.lower().endswith(".csv"):
            continue

        symbol = name[:-4].upper()

        if symbol:
            symbols.append(symbol)

    return sorted(set(symbols))


if __name__ == "__main__":

    symbols = get_symbols()

    print({
        "success": True,
        "symbols": len(symbols),
        "sample": symbols[:30]
    })
