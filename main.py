from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/get_server_info')
def get_server_info():
    username = request.args.get('username')
    
    # Проверка на пустой никнейм
    if not username or username.strip() == "":
        return jsonify({"error": "Username is required"}), 400

    try:
        # Получение информации о пользователе по никнейму
        user_info = requests.post(
            "https://users.roblox.com/v1/usernames/users",
            json={"usernames": [username]}
        )
        user_info.raise_for_status()  # Проверяем статус запроса
        user_info = user_info.json()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch user info: {str(e)}"}), 500

    # Если пользователь не найден
    if not user_info.get("data") or len(user_info["data"]) == 0:
        return jsonify({"status": "not_found"})

    # Извлечение user_id
    user_id = user_info["data"][0]["id"]
    
    try:
        # Получение информации о присутствии игрока (в игре или оффлайн)
        presence = requests.post(
            "https://presence.roblox.com/v1/presence/users",
            json={"userIds": [user_id]}
        )
        presence.raise_for_status()  # Проверяем статус запроса
        presence = presence.json()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch presence data: {str(e)}"}), 500

    # Логирование для отладки
    print("Presence Data:", presence)

    # Получаем информацию о присутствии игрока
    user_presence = presence.get("userPresences", [])[0] if presence.get("userPresences") else {}

    # Если игрок не в игре
    if not user_presence or user_presence.get("userPresenceType") != 2:
        return jsonify({"status": "offline"})

    # Проверка на наличие 'gameSessionId'
    game_session_id = user_presence.get("gameSessionId", None)
    if not game_session_id:
        return jsonify({"status": "not_found", "error": "No game session available for the user"})

    # Возвращаем информацию о месте и jobId
    return jsonify({
        "status": "success",
        "placeId": user_presence["placeId"],
        "jobId": game_session_id
    })

if __name__ == '__main__':
    # Запуск приложения Flask
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
