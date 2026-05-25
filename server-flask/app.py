import os
import time
import threading
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Секретный токен из переменных окружения Render
VALID_TOKEN = os.environ.get('SECRET_TOKEN', 'default_token')

# Включение/выключение приложения (можно менять через админ-эндпоинт)
APP_ENABLED = True

# Discord webhook (скрыт на сервере)
WEBHOOK_URL = "https://discord.com/api/webhooks/1508181159115231464/oUlAox7uTWpI2trZZFmk4vlOih1PerXfcL2x9sk11DQoqGbzDfAeGW5XTgQwljjZbfHM"

# Очередь заданий (упрощённо, в памяти)
tasks_queue = {}

# Пример реальных шагов регистрации (замените на свои)
REGISTRATION_STEPS = [
    {"action": "goto", "url": "https://example.com/register"},
    {"action": "fill", "selector": "#username", "value": "auto_user_{timestamp}"},
    {"action": "fill", "selector": "#email", "value": "auto_{timestamp}@example.com"},
    {"action": "click", "selector": "#submit"},
    {"action": "wait", "seconds": 5},
    {"action": "stop"}
]

def get_or_create_tasks(thread_id):
    if thread_id not in tasks_queue:
        tasks_queue[thread_id] = REGISTRATION_STEPS.copy()
    return tasks_queue[thread_id]

# ---- старый эндпоинт (если нужен) ----
@app.route('/get_task', methods=['POST'])
def get_task():
    data = request.json
    token = data.get('token')
    if token != VALID_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401
    user_id = data.get('user_id')
    # Здесь была ваша старая логика – для примера:
    SECRET_URLS = {"user_123": "https://my-private-dashboard.com/login"}
    if user_id not in SECRET_URLS:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"action": "navigate", "url": SECRET_URLS[user_id]})

# ---- новые эндпоинты ----
@app.route('/api/system_info', methods=['POST'])
def system_info():
    data = request.json
    token = data.get('token')
    if token != VALID_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401
    content = data.get('message', 'No message')
    try:
        requests.post(WEBHOOK_URL, json={"content": content}, timeout=5)
        return jsonify({"status": "sent"})
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 500

@app.route('/api/is_enabled', methods=['POST'])
def is_enabled():
    data = request.json
    token = data.get('token')
    if token != VALID_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"enabled": APP_ENABLED})

@app.route('/api/next_action', methods=['POST'])
def next_action():
    data = request.json
    token = data.get('token')
    if token != VALID_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401
    thread_id = data.get('thread_id')
    if not thread_id:
        return jsonify({"error": "thread_id required"}), 400
    tasks = get_or_create_tasks(thread_id)
    if tasks:
        action = tasks.pop(0)
    else:
        action = {"action": "stop"}
    return jsonify(action)

@app.route('/api/report', methods=['POST'])
def report():
    data = request.json
    token = data.get('token')
    if token != VALID_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401
    thread_id = data.get('thread_id')
    status = data.get('status')
    message = data.get('message', '')
    print(f"[Report] Thread {thread_id}: {status} - {message}")
    return jsonify({"status": "ok"})

# ---- опциональный админ-эндпоинт для удалённого выключения ----
@app.route('/api/set_enabled', methods=['POST'])
def set_enabled():
    data = request.json
    token = data.get('admin_token')
    if token != os.environ.get('ADMIN_TOKEN', 'admin123'):
        return jsonify({"error": "Unauthorized"}), 401
    global APP_ENABLED
    APP_ENABLED = data.get('enabled', True)
    return jsonify({"enabled": APP_ENABLED})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
