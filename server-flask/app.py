import os
from flask import Flask, request, jsonify

# !!! ВАЖНО: Замените на ваш реальный токен, он будет использоваться для простой аутентификации клиента
VALID_TOKEN = os.environ.get('SECRET_TOKEN', 'your_default_token')

app = Flask(__name__)

# Представьте, что это ваша секретная база данных
SECRET_URLS = {
    "user_123": "https://my-private-dashboard.com/login",
}

@app.route('/get_task', methods=['POST'])
def get_task():
    """
    Клиент обращается сюда, чтобы получить следующую задачу.
    """
    data = request.get_json()
    user_id = data.get('user_id')
    client_token = data.get('token')

    # Проверка токена
    if client_token != VALID_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    if user_id not in SECRET_URLS:
        return jsonify({"error": "User not found"}), 404

    # Здесь может быть ваша сложная логика
    target_url = SECRET_URLS[user_id]

    # Отправляем клиенту "инструкцию"
    return jsonify({
        "action": "navigate",
        "url": target_url,
        "message": "Пожалуйста, перейдите по этой ссылке"
    })

# Эта часть важна, чтобы запускать сервер на нужном порту
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)