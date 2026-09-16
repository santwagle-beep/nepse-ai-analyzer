import requests

YONEPSE_URL = "https://shubhamnpk.github.io/yonepse/data/nepse_data.json"

def create_database():
    return True

def test_source():
    try:
        response = requests.get(
            YONEPSE_URL,
            timeout=20
        )

        data = response.json()

        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "stocks": len(data),
            "sample": data[:2]
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }
``w
