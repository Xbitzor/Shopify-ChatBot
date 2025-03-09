from flask import Flask, request, jsonify, render_template_string
import requests
import os

app = Flask(__name__)

# Get Shopify credentials from environment variables
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")

# Shopify API headers
HEADERS = {
    "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
    "Content-Type": "application/json"
}

# Fetch store details dynamically
def fetch_shopify_data(endpoint):
    url = f"{SHOPIFY_STORE_URL}/admin/api/2023-01/{endpoint}.json"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Error fetching {endpoint}: {str(e)}"}

# Fetch products
def get_product_details():
    data = fetch_shopify_data("products")
    products = data.get("products", [])

    if not products:
        return "No products available."

    product_list = "<ul>"
    for product in products[:5]:  # Limit to 5 products
        title = product.get("title", "Unknown Product")
        price = product.get("variants", [{}])[0].get("price", "N/A")
        product_list += f"<li><b>{title}:</b> ${price}</li>"
    product_list += "</ul>"

    return product_list

# Fetch store policies
def get_store_policies():
    data = fetch_shopify_data("policies")
    policies = data.get("policies", [])

    if not policies:
        return "No policies available."

    policy_text = "<ul>"
    for policy in policies:
        title = policy.get("title", "Unknown Policy")
        body = policy.get("body", "No details available")
        policy_text += f"<li><b>{title}:</b> {body}</li>"
    policy_text += "</ul>"

    return policy_text

# Fetch shipping info
def get_shipping_details():
    return "<b>Shipping Info:</b> We offer worldwide shipping with estimated delivery in 5-10 days."

# Fetch payment details
def get_payment_methods():
    return "<b>Accepted Payment Methods:</b> We accept PayPal, Visa, MasterCard, and Shopify Payments."

# Fetch customer support details
def get_customer_support():
    return "<b>Customer Support:</b> You can reach us at support@example.com."

# Serve HTML Chat Page
@app.route("/", methods=["GET"])
def home():
    html_page = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Shopify Chatbot</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 20px; background-color: #f4f4f4; }
            h1 { color: #333; }
            #chatbox { width: 50%; margin: auto; padding: 10px; border: 1px solid #ddd; background: white; border-radius: 5px; }
            input, button { padding: 10px; margin: 5px; width: 80%; }
            button { width: 20%; }
        </style>
    </head>
    <body>
        <h1>Welcome to the Shopify Chatbot</h1>
        <div id="chatbox">
            <p>Ask me anything about our store:</p>
            <input type="text" id="userInput" placeholder="Type your question...">
            <button onclick="sendMessage()">Send</button>
            <p id="response"></p>
        </div>
        <script>
            function sendMessage() {
                let userMessage = document.getElementById("userInput").value;
                fetch("/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ message: userMessage })
                })
                .then(response => response.json())
                .then(data => { document.getElementById("response").innerHTML = data.response; })
                .catch(error => { document.getElementById("response").innerHTML = "Error: " + error; });
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html_page)

# Chatbot logic
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("message", "").lower()

    # Check user query and respond with correct data
    if "product" in user_input or "price" in user_input:
        return jsonify({"response": get_product_details()})
    if "refund policy" in user_input or "return policy" in user_input:
        return jsonify({"response": get_store_policies()})
    if "shipping" in user_input:
        return jsonify({"response": get_shipping_details()})
    if "payment" in user_input:
        return jsonify({"response": get_payment_methods()})
    if "support" in user_input or "contact" in user_input:
        return jsonify({"response": get_customer_support()})

    # Default response
    return jsonify({"response": "I'm here to help! Ask me anything about our store."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
