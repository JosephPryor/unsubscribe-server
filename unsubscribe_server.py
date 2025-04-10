from flask import Flask, request
import hmac
import hashlib
import os

app = Flask(__name__)
SECRET_KEY = b'G4`(L4WRZK3Al_y@pVr>-dZC<1x9vO'  # 🔒 keep this secret

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

@app.route('/unsubscribed.txt')
def get_unsubscribed_file():
    try:
        with open("unsubscribed.txt", "r") as f:
            return f.read(), 200, {'Content-Type': 'text/plain'}
    except FileNotFoundError:
        return "", 200, {'Content-Type': 'text/plain'}

@app.route('/admin/remove')
def remove_email():
    target = request.args.get('email', '').strip().lower()
    if not target:
        return "No email provided", 400

    try:
        with open("unsubscribed.txt", "r") as f:
            lines = f.readlines()

        lines = [line for line in lines if line.strip().lower() != target]

        with open("unsubscribed.txt", "w") as f:
            f.writelines(lines)

        return f"{target} has been removed from the unsubscribe list.", 200
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
