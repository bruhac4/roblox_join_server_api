from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/get_server_info')
def get_server_info():
    username = request.args.get('username')
    if not username:
        return jsonify({"error": "Username is required"}), 400

    user_info = requests.post(
        "https://users.roblox.com/v1/usernames/users",
        json={"usernames": [username]}
    ).json()

    if not user_info.get("data") or len(user_info["data"]) == 0:
        return jsonify({"status": "not_found"})

    user_id = user_info["data"][0]["id"]

    presence = requests.post(
        "https://presence.roblox.com/v1/presence/users",
        json={"userIds": [user_id]}
    ).json()

    user_presence = presence["userPresences"][0]

    if user_presence["userPresenceType"] != 2:
        return jsonify({"status": "offline"})

    return jsonify({
        "status": "in_game",
        "placeId": user_presence["placeId"],
        "jobId": user_presence["gameSessionId"]
    })

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
