from flask import Flask, jsonify, request, abort
from flask_cors import CORS
import requests
import os
import time

app = Flask(__name__)
CORS(app)

# Cache storage
cache = {
    'statuses': {},
    'last_updated': {}
}

MAX_LIMIT = 10
CACHE_UPDATE_INTERVAL = int(os.getenv('CACHE_UPDATE_INTERVAL', 3600))  # Default to 1 hour

def fetch_statuses(limit=3):
    """
    Fetches the latest posts from the Mastodon account.

    Parameters:
        limit (int): The number of posts to fetch.

    Returns:
        list: A list of the latest posts, or None if fetching fails.
    """
    mastodon_instance = os.getenv('MASTODON_INSTANCE')
    access_token = os.getenv('ACCESS_TOKEN')
    if not mastodon_instance or not access_token:
        raise ValueError("Mastodon instance or access token not provided")

    url = f"{mastodon_instance}/api/v1/accounts/verify_credentials"
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        user_id = response.json()['id']
        url = f"{mastodon_instance}/api/v1/accounts/{user_id}/statuses?limit={limit}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print("Error fetching statuses:", response.status_code, response.text)
    else:
        print("Error verifying credentials:", response.status_code, response.text)
    return None

def update_cache(limit=3, force_update=False):
    """
    Updates the cache with the latest posts if the cache is stale or forced to update.

    Parameters:
        limit (int): The number of posts to fetch.
        force_update (bool): Whether to force update the cache regardless of the last update time.

    Returns:
        bool: True if cache is updated successfully, False otherwise.
    """
    current_time = time.time()
    last_updated = cache['last_updated'].get(limit, 0)
    
    if force_update or (current_time - last_updated > CACHE_UPDATE_INTERVAL):
        statuses = fetch_statuses(limit)
        if statuses:
            cache['statuses'][limit] = statuses
            cache['last_updated'][limit] = current_time
            return True
        return False
    return True  # Cache is considered updated if within the interval

@app.route('/statuses', methods=['GET'])
def statuses():
    """
    Endpoint to get the latest posts.

    Returns:
        Response: JSON response containing the latest posts.
    """
    limit = request.args.get('limit', default=3, type=int)
    if limit > MAX_LIMIT:
        return jsonify({"error": f"Limit cannot exceed {MAX_LIMIT}"}), 400

    if update_cache(limit):
        return jsonify(cache['statuses'][limit])
    else:
        return jsonify({"error": "Unable to fetch latest posts"}), 500

@app.route('/webhook', methods=['GET'])
def webhook():
    """
    Endpoint to trigger cache update via webhook.

    Returns:
        Response: JSON response indicating success or failure.
    """
    limit = request.args.get('limit', default=3, type=int)
    if limit > MAX_LIMIT:
        return jsonify({"error": f"Limit cannot exceed {MAX_LIMIT}"}), 400

    if update_cache(limit, force_update=True):
        return jsonify({"message": "Cache updated successfully"}), 200
    else:
        return jsonify({"error": "Failed to update cache"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

