from flask import Flask, request, jsonify
import requests
import os  # Import for environment variables

app = Flask(__name__)

# Get Shopify credentials from environment variables
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")  # Get store URL from Railway env vars
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")  # Use access token instead of API key & password

# Fetch product details from Shopify
def get_product_details():
    url = f"{SHOPIFY_STORE_URL}/admin/api/2023-01/products.json"
    headers = {"X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN}  # Use access token
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("products", [])
    return []

# Fetch store policies from Shopify
def get_store_policies():
    url = f"{SHOPIFY_STORE_URL}/admin/api/2023-01/policies.json"
    headers = {"X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN}  # Use access token
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("policies", [])
    return []

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("message", "").lower()
    
    # Check if user is asking about products
    if "product" in user_input or "price" in user_input:
        products = get_product_details()
        if products:
            response_text = "Here are some of our products:\n"
            for product in products[:5]:  # Limit to 5 products for brevity
                response_text += f"- {product['title']}: {product['variants'][0]['price']}\n"
            return jsonify({"response": response_text})
        else:
            return jsonify({"response": "Sorry, I couldn't fetch the product details right now."})
    
    # Check if user is asking about store policies
    if "refund policy" in user_input or "return policy" in user_input:
        policies = get_store_policies()
        for policy in policies:
            if "refund" in policy['title'].lower() or "return" in policy['title'].lower():
                return jsonify({"response": policy['body']})
        return jsonify({"response": "All sales are final. We do not accept returns or refunds."})
    
    # Default response
    return jsonify({"response": "I'm here to help! Ask me anything about our store."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Default to 8080 if no PORT is assigned
    app.run(host="0.0.0.0", port=port)
