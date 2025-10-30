import requests

def get_location_info(lat, lon):
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
    headers = {'User-Agent': 'LocationScript/1.0'}  # Required by Nominatim
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        address = data.get("address", {})

        street = address.get("road", address.get("county", "Unknown street"))
        state = address.get("state", "Unknown state")
        
        return street, state, data
    else:
        print("Error:", response.status_code)
        return None, None

# Example usage:
if __name__ == "__main__":
    lat = "8.9396781"
    lon = "7.3182453"

    street, state, data = get_location_info(lat, lon)
    print(f"Street: {street}")
    print(f"state: {state}")
    print(data)
