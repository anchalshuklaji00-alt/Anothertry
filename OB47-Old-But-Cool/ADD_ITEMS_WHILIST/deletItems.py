import requests

m_ids = [801048010, 801048536, 801000609, 801000171]
jwt_token = "دير توكن jwt هنا"

# تكرار العملية مرتين
for _ in range(2):
    for item_id in m_ids:
        url = f"https://fox-additems-wishlist-e1zc.vercel.app/add-to-wishlist/{jwt_token}/{item_id}"
        response = requests.get(url)
        print(f"Item ID: {item_id}, Response: {response.text}")