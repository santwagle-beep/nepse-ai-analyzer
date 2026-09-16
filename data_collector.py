import requests

SOURCE_URL = "https://nepsealpha.com/nepse-data"

def create_database():
    return True

def test_source():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(
            SOURCE_URL,
            headers=headers,
            timeout=20,
            allow_redirects=True
        )

        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "final_url": response.url,
            "content_type": response.headers.get(
                "content-type",
                ""
            ),
            "size": len(response.content),
            "server": response.headers.get(
                "server",
                ""
            )
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }
