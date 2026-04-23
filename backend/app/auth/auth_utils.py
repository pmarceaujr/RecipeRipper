from flask import request, jsonify
import jwt
from functools import wraps
from flask import current_app
import logging

# Configure logging
logging.basicConfig(
# filename="C:\\Users\\marceaup\\OneDrive - Illumination Works, llc\\Documents\\Projects\\zCalendarSync\\CalendarSync\\logs\\J1OutlookToGoogleSync.log",
level=logging.INFO,
FORMATS = {
    logging.DEBUG: "%(asctime)s - %(levelname)s - %(message)s",
    logging.INFO: "%(asctime)s - %(levelname)s - %(message)s",
    logging.WARNING: "%(asctime)s - %(levelname)s - %(message)s",
    logging.ERROR: "%(asctime)s - %(levelname)s - %(funcName)s - %(lineno)d - %(message)s",
    logging.CRITICAL: "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
}
)
# Use your Flask secret and algorithm
JWT_SECRET = current_app.config.get("JWT_SECRET_KEY", "super-secret")
JWT_ALGORITHM = current_app.config.get("JWT_ALGORITHM", "HS256")

def debug_jwt_required(f):
    """Decorator to log and verify incoming JWT for debugging."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", None)
        if not auth_header:
            logging.info("No Authorization header received")
            return jsonify({"error": "Authorization header missing"}), 401

        try:
            # Expect header like: "Bearer <token>"
            token = auth_header.split()[1]
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            logging.info(f"In Debug Function: JWT is valid: {payload}")
        except IndexError:
            logging.error(f"Malformed Authorization header: {auth_header}")
            return jsonify({"error": "Malformed Authorization header"}), 401
        except jwt.ExpiredSignatureError:
            logging.error("Token expired")
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError as e:
            logging.error(f"Invalid token: {e}")
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)
    return decorated

# Example usage on a route
@app.route("/api/debug", methods=["GET"])
@debug_jwt_required
def debug_route():
    return jsonify({"message": "JWT verified successfully!"})
