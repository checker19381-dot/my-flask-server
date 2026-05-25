# =============== ДОБАВИТЬ НОВЫЕ ЭНДПОИНТЫ ===============
import os
from flask import Flask, request, jsonify
import requests
import time
import threading

# Тот же секретный токен, что вы задали на Render
VALID_TOKEN = os.environ.get('SECRET_TOKEN', 'default_token')

# Здесь будет храниться статус enabled/disabled (можно менять через админку)
APP_ENABLED = True   # По умолчанию включено

# Discord webhook – теперь только на сервере
WEBHOOK_URL = "https://discord.com/api/webhooks/1508181159115231464/oUlAox7uTWpI2trZZFmk4vlOih1PerXfcL2x9sk11DQoqGbzDfAeGW5XTgQwljjZbfHM"

# Очередь заданий для каждого потока (упрощённо, в реальном проекте – БД)
# Ключ: thread_id (можно генерировать), значение: список команд
tasks_queue = {}

# Пример последовательности регистрации (то, что раньше было в Testing_App)
REGISTRATION_STEPS = [
    {"action": "goto", "url": "https://example.com/register"},
    {"action": "fill", "selector": "#username", "value": "auto_user_{timestamp}"},
    {"action": "fill", "selector": "#email", "value": "auto_{timestamp}@example.com"},
    {"action": "click", "selector": "#submit"},
    {"action": "wait", "seconds": 5},
    {"action": "stop"}
]

# ---- Вспомогательная функция для генерации уникального ID потока ----
def get_or_create_tasks(thread_id):
    if thread_id not in tasks_queue:
        # Копируем шаги для нового потока (чтобы каждый поток выполнял свою копию)
        tasks_queue[thread_id] = REGISTRATION_STEPS.copy()
    return tasks_queue[thread_id]

# ---- Эндпоинт: получение информации о системе (заменяет прямой webhook) ----
@app.route('/api/system_info', methods=['POST'])
def system_info():
    data = request.json
    token = data.get('token')
    if token != VALID_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401
    
    # Отправляем данные в Discord от имени сервера
    content = data.get('message', 'No message')
    try:
        requests.post(WEBHOOK_URL, json={"content": content}, timeout=5)
        return jsonify({"status": "sent"})
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 500

# ---- Эндпоинт: проверка, включено ли приложение (заменяет Gist) ----
@app.route('/api/is_enabled', methods=['POST'])
def is_enabled():
    data = request.json
    token = data.get('token')
    if token != VALID_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"enabled": APP_ENABLED})

# ---- Эндпоинт: получить следующее действие для потока ----
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

# ---- Эндпоинт: отчёт о выполнении действия (логирование) ----
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
    # Здесь можно сохранять в лог-файл или БД
    return jsonify({"status": "ok"})

# ---- Опционально: эндпоинт для включения/выключения (админка) ----
# Чтобы менять APP_ENABLED удалённо (без передеплоя), можно добавить:
@app.route('/api/set_enabled', methods=['POST'])
def set_enabled():
    data = request.json
    token = data.get('admin_token')
    # admin_token задайте отдельной переменной окружения на Render
    if token != os.environ.get('ADMIN_TOKEN', 'admin123'):
        return jsonify({"error": "Unauthorized"}), 401
    global APP_ENABLED
    APP_ENABLED = data.get('enabled', True)
    return jsonify({"enabled": APP_ENABLED})
