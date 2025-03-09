from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Get Shopify credentials from environment variables
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")

# Fetch product details from Shopify
def get_product_details():
    url = f"{SHOPIFY_STORE_URL}/admin/api/2023-01/products.json"
    headers = {"X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN, "Content-Type": "application/json"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get("products", [])
    except requests.exceptions.RequestException as e:
        print("Error fetching products:", e)
        return []

# Fetch store policies from Shopify
def get_store_policies():
    url = f"{SHOPIFY_STORE_URL}/admin/api/2023-01/policies.json"
    headers = {"X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN, "Content-Type": "application/json"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get("policies", [])
    except requests.exceptions.RequestException as e:
        print("Error fetching policies:", e)
        return []

@app.route("/", methods=["GET"])
def home():
    return "Shopify Chatbot is Running!"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    if not data or "message" not in data:
        return jsonify({"response": "Invalid request, please send a message."}), 400

    user_input = data.get("message", "").lower()

    # Handle product inquiries
    if "product" in user_input or "price" in user_input:
        products = get_product_details()
        if products:
            response_text = "Here are some of our products:\n"
            for product in products[:5]:  # Limit to 5 products
                price = product["variants"][0]["price"]
                response_text += f"- {product['title']}: ${price}\n"
            return jsonify({"response": response_text})
        return jsonify({"response": "Sorry, I couldn't fetch product details right now."})

    # Handle store policies
    if "refund policy" in user_input or "return policy" in user_input:
        policies = get_store_policies()
        for policy in policies:
            if "refund" in policy["title"].lower() or "return" in policy["title"].lower():
                return jsonify({"response": policy["body"]})
        return jsonify({"response": "All sales are final. We do not accept returns or refunds."})

    # Default response
    return jsonify({"response": "I'm here to help! Ask me anything about our store."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Match your Railway port
    app.run(host="0.0.0.0", port=port)
