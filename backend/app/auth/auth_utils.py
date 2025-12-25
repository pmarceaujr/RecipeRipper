from flask import request, jsonify
import jwt
from functools import wraps
from flask import current_app

# Use your Flask secret and algorithm
JWT_SECRET = current_app.config.get("JWT_SECRET_KEY", "super-secret")
JWT_ALGORITHM = current_app.config.get("JWT_ALGORITHM", "HS256")

def debug_jwt_required(f):
    """Decorator to log and verify incoming JWT for debugging."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", None)
        if not auth_header:
            print("No Authorization header received")
            return jsonify({"error": "Authorization header missing"}), 401

        try:
            # Expect header like: "Bearer <token>"
            token = auth_header.split()[1]
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            print("✅ JWT is valid:", payload)
        except IndexError:
            print("Malformed Authorization header:", auth_header)
            return jsonify({"error": "Malformed Authorization header"}), 401
        except jwt.ExpiredSignatureError:
            print("❌ Token expired")
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError as e:
            print("❌ Invalid token:", e)
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)
    return decorated

# Example usage on a route
@app.route("/api/debug", methods=["GET"])
@debug_jwt_required
def debug_route():
    return jsonify({"message": "JWT verified successfully!"})
