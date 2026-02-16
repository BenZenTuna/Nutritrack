import requests

def test_update():
    url = "http://localhost:8000/api/profile"
    payload = {
        "age": 42,
        "sex": "male",
        "height_cm": 180,
        "current_weight_kg": 85.5,
        "activity_level": "light",
        "weight_goal_kg": 80.0,  # Setting a test goal
        "calorie_deficit": 500
    }
    
    try:
        response = requests.put(url, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_update()
