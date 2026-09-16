import requests

URL = "https://raw.githubusercontent.com/binayabaral/nepal-market-data/main/data/nepse/HATHY.csv"

def test_history():

    response = requests.get(
        URL,
        timeout=30
    )

    return {
        "status_code": response.status_code,
        "success": response.status_code == 200,
        "size": len(response.content),
        "preview": response.text[:500]
    }


if __name__ == "__main__":
    print(test_history())
