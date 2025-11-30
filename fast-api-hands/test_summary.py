import requests
import sys

def test_summary(conv_id):
    url = f"http://localhost:8000/get_summary/{conv_id}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Success!")
            print(response.json()['summary'])
        else:
            print(f"Failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Use a known conv_id, e.g., 1 or pass as arg
    conv_id = sys.argv[1] if len(sys.argv) > 1 else 1
    test_summary(conv_id)
