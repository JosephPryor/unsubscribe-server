from flask import Flask, request
import hmac
import hashlib
import os


app = Flask(__name__)
SECRET_KEY = b'G4`(L4WRZK3Al_y@pVr>-dZC<1x9vO'  # 🔒 change this to something long and random

def generate_token(email):
    return hmac.new(SECRET_KEY, email.encode(), hashlib.sha256).hexdigest()

def is_token_valid(email, token):
    return hmac.compare_digest(generate_token(email), token)

@app.route('/unsubscribe')
def unsubscribe():
    email = request.args.get('email', '').strip().lower()
    token = request.args.get('token', '')

    if not email or not token:
        return "Invalid request.", 400

    if not is_token_valid(email, token):
        return "Invalid or expired token.", 403

    with open("unsubscribed.txt", "a") as f:
        f.write(email + "\n")

    return f"You ({email}) have been successfully unsubscribed. You won’t receive any more emails from us."

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
