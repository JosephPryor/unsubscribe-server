from flask import Flask, request, jsonify
import hmac
import hashlib
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

app = Flask(__name__)
SECRET_KEY = b'G4`(L4WRZK3Al_y@pVr>-dZC<1x9vO'  # 🔒 keep this secret

# Get database URL from environment variable
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

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

    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO unsubscribed (email, unsubscribed_at) VALUES (%s, %s) ON CONFLICT (email) DO NOTHING",
                    (email, datetime.utcnow())
                )
        return f"You ({email}) have been successfully unsubscribed. You won’t receive any more emails from us."
    except Exception as e:
        return f"Database error: {e}", 500
    finally:
        if conn:
            conn.close()

@app.route('/unsubscribed')
def get_unsubscribed_file():
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT email FROM unsubscribed")
                emails = [row['email'] for row in cur.fetchall()]
        return jsonify(emails), 200
    except Exception as e:
        return f"Error retrieving unsubscribed emails: {e}", 500
    finally:
        if conn:
            conn.close()

@app.route('/admin/remove')
def remove_email():
    target = request.args.get('email', '').strip().lower()
    if not target:
        return "No email provided", 400

    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM unsubscribed WHERE email = %s", (target,))
        return f"{target} has been removed from the unsubscribe list.", 200
    except Exception as e:
        return f"Error: {str(e)}", 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
