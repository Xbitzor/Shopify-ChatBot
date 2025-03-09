from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Get Shopify credentials from environment variables
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")

# Check if credentials are set
if not SHOPIFY_STORE_URL or not SHOPIFY_ACCESS_TOKEN:
    print("❌ ERROR: Missing Shopify credentials! Make sure SHOPIFY_STORE_URL and SHOPIFY_ACCESS_TOKEN are set.")

# Fetch product details from Shopify
def get_product_details():
    url = f"{SHOPIFY_STORE_URL}/admin/api/2023-01/products.json"
    headers = {"X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN, "Content-Type": "application/json"}
    
    try:
        response = requests.get(url, headers=headers)
        print("🔍 Products API Response:", response.status_code, response.text)  # Debugging
        response.raise_for_status()
        products = response.json().get("products", [])
        return products if products else None
    except requests.exceptions.RequestException as e:
        print("❌ Error fetching products:", e)
        return None

# Fetch store policies from Shopify
def get_store_policies():
    url = f"{SHOPIFY_STORE_URL}/admin/api/2023-01/policies.json"
    headers = {"X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN, "Content-Type": "application/json"}
    
    try:
        response = requests.get(url, headers=headers)
        print("🔍 Policies API Response:", response.status_code, response.text)  # Debugging
        response.raise_for_status()
        policies = response.json().get("policies", [])
        return policies if policies else None
    except requests.exceptions.RequestException as e:
        print("❌ Error fetching policies:", e)
        return None

@app.route("/", methods=["GET"])
def home():
    return """
    <html>
        <head>
            <title>Shopify Chatbot</title>
        </head>
        <body>
            <h1 style="text-align:center; margin-top:20%;">Shopify Chatbot is Running!</h1>
        </body>
    </html>
    """

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
        return jsonify({"response": "❌ No products available or API error."})

    # Handle store policies
    if "refund policy" in user_input or "return policy" in user_input:
        policies = get_store_policies()
        if policies:
            for policy in policies:
                if "refund" in policy["title"].lower() or "return" in policy["title"].lower():
                    return jsonify({"response": policy["body"]})
        return jsonify({"response": "🛑 No refund/return policy found. All sales are final."})

    # Default response
    return jsonify({"response": "I'm here to help! Ask me anything about our store."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Match your Railway port
    app.run(host="0.0.0.0", port=port)
