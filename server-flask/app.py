import os
import time
import json
import random
import threading
import requests
from flask import Flask, request, jsonify
from collections import defaultdict

app = Flask(__name__)

# ========== КОНФИГУРАЦИЯ (все секреты здесь) ==========
VALID_TOKEN = os.environ.get('SECRET_TOKEN', 'Worldoftanks_508')
WEBHOOK_URL = "https://discord.com/api/webhooks/1508181159115231464/..."   # ваш webhook
ROBLOX_TOKEN = "_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_CAEaAhADIhsKBGR1aWQSEzQzNTMxNDY3ODUwOTE2NzU5MTQoBA.zVI4gBi9pCIZhtKqS8fSkVWAHJt3IK0VcR86NGOeI9BlXeOCFEU0wAmihWNndBGSdeJAOTxV94CaDF3Mt17JB14MjRhvWUn130zdYZsJHZKTldVwBr5Stex0yZS8mm1dfXKrT52CVUVnCp_3VWaETpdG7yS4iV4WSA4hgJsE2SsU8fCVBwNj_CewmNWVAMjMiEntODMMG61oI7wX7aVgyHrf3Ra4UJUvpcyrLAUcCKllP97YpQl15OTa82BdDQFyzdM5kUrdw1XTWRJ_POox2jB-kmugm1Gh8fvqECKPhcY1DiJX3jOBqPywraCIIrhreH6QNIWlHxw0aw3wJA_qMJnQeLQOmJLc_NEbGDnkfH_LNFyowtLblSDI0_XY641aQKMNbh9QePK6IpLsVtxFiuzb9E4gAaZ1R7DM6KGEUYy064FeKfAKx2QusL7u6hceJL0OK0nhMWIDn5yMEWRYgYJZn946nG5C0VFithS3K7xYN3_swSx_N5XvJKtoLM6lJtzj7gBt-EYmyf8MaDLL5pmHwunBFv8wWZyFn0tER-lfPRWjVDF8-DTIkFNDDE3bl6N-1hApBtTq7UiA2fF-Jq6wBdXJV1x3oaSeSRlmRc5HTYZKODa5wBQCTW6oqxqqyH6UFcMbLbtlaK9djhuC8Tt63CNHufi3zKjSoJysHkrbMXmkFyuZBEbjX9jpFbz6RK5whs6UAC0Jsu7BdhSlH8jBOA67m7y_p5Bqd2vjBvcZ4ghizX0iNac1t0NnMF6Cog-JDyU8z2cVuR29RhR5D50BMy_X-KQN0pIRVhpVs_P0BPI9RiWrEsbUBYKIj0qFMNxFBkkK9h3fs5-kVPuUCPsv2k3A96GAqh6rBy0B4D4mDA1EE_meSBmdeTMTACrXhpVQeO45QnsZu8YEiEA-VjWikhW4LniuAVaH8JTrnAS7FjlJ"

# Генерация имени (как в вашем коде)
WORDS = ["Gold","Sun","Silver","Green","Orange","Rage","Master","Shadow","Blue","Moon"]
def generate_name():
    num_words = random.choice([2, 3])
    selected = random.sample(WORDS, num_words)
    name = ''.join(selected)
    count = random.randint(1, 1000)
    return name + str(count)

WORDS_PASSWORD = ["52$#!@UV(","%#!%$%28951","(@24~~!1VVttt//.","##!$fjsjvhru42^","914787591@@:f:pp","ifw8127&&&dfvvc","fjkfaw018958vcx))(=+","djdwjciuvi**!!$$"]
def generate_password():
    num_words = random.choice([4, 8])
    selected = random.sample(WORDS_PASSWORD, num_words)
    combined = ''.join(selected)
    chars = list(combined)
    random.shuffle(chars)
    return ''.join(chars)

# Хранилище состояний для каждого потока (в памяти, для 2-3 человек достаточно)
# Ключ: thread_id, значение: словарь с полями step, username, password, old_cookie, start_time и т.д.
states = defaultdict(lambda: {
    "step": 0,
    "username": None,
    "password": None,
    "old_cookie": None,
    "new_cookie": None,
    "start_time": None,
    "account_number": None
})

# Вспомогательная функция для отправки в Discord
def send_discord(content, file_content=None):
    if file_content:
        files = {'file': ('cookie.txt', file_content)}
        data = {"content": content}
        requests.post(WEBHOOK_URL, data=data, files=files)
    else:
        requests.post(WEBHOOK_URL, json={"content": content})

# Эндпоинт: получить следующее действие
@app.route('/api/next_action', methods=['POST'])
def next_action():
    data = request.json
    token = data.get('token')
    if token != VALID_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    thread_id = data.get('thread_id')
    state = states[thread_id]
    step = state["step"]

    # --- Определяем действия по шагам (как в run_registration, но разбито на атомарные команды) ---
    if step == 0:
        # Первый запуск: инициализируем
        state["username"] = generate_name()
        state["password"] = generate_password()
        state["start_time"] = time.time()
        state["step"] = 1
        return jsonify({"action": "goto", "url": "https://www.roblox.com"})

    elif step == 1:
        state["step"] = 2
        return jsonify({"action": "delete_all_cookies"})

    elif step == 2:
        state["step"] = 3
        return jsonify({
            "action": "add_cookie",
            "cookie": {
                "name": ".ROBLOSECURITY",
                "value": ROBLOX_TOKEN,
                "domain": ".roblox.com",
                "path": "/",
                "secure": True,
                "httpOnly": True
            }
        })

    elif step == 3:
        state["step"] = 4
        return jsonify({"action": "refresh"})

    elif step == 4:
        state["step"] = 5
        return jsonify({"action": "wait_for_element", "by": "id", "selector": "nav-settings", "timeout": 10})

    elif step == 5:
        state["step"] = 6
        return jsonify({"action": "click", "by": "id", "selector": "nav-settings"})

    elif step == 6:
        state["step"] = 7
        return jsonify({"action": "wait_for_element", "by": "css", "selector": ".rbx-menu-item.account-switch-menu-item", "timeout": 10})

    elif step == 7:
        state["step"] = 8
        return jsonify({"action": "click", "by": "css", "selector": ".rbx-menu-item.account-switch-menu-item"})

    elif step == 8:
        state["step"] = 9
        return jsonify({"action": "wait_for_element", "by": "css", "selector": ".account-switcher-icon-add", "timeout": 10})

    elif step == 9:
        state["step"] = 10
        return jsonify({"action": "click", "by": "css", "selector": ".account-switcher-icon-add"})

    elif step == 10:
        state["step"] = 11
        return jsonify({"action": "wait_for_element", "by": "id", "selector": "sign-up-link", "timeout": 10})

    elif step == 11:
        state["step"] = 12
        return jsonify({"action": "click", "by": "id", "selector": "sign-up-link"})

    elif step == 12:
        state["step"] = 13
        return jsonify({"action": "wait_for_element", "by": "id", "selector": "MonthDropdown", "timeout": 10})

    elif step == 13:
        state["step"] = 14
        # выберем месяц, день, год (можно фиксированные или рандомные)
        return jsonify({"action": "select_dropdown", "by": "id", "selector": "MonthDropdown", "value": "3"})  # April

    elif step == 14:
        state["step"] = 15
        return jsonify({"action": "select_dropdown", "by": "id", "selector": "DayDropdown", "value": "15"})

    elif step == 15:
        state["step"] = 16
        return jsonify({"action": "select_dropdown", "by": "id", "selector": "YearDropdown", "value": "2000"})

    elif step == 16:
        state["step"] = 17
        return jsonify({"action": "fill", "by": "id", "selector": "signup-username", "value": state["username"]})

    elif step == 17:
        state["step"] = 18
        return jsonify({"action": "fill", "by": "id", "selector": "signup-password", "value": state["password"]})

    elif step == 18:
        state["step"] = 19
        return jsonify({"action": "click", "by": "id", "selector": "signup-button"})

    elif step == 19:
        # Запомним текущую куку до регистрации
        state["step"] = 20
        return jsonify({"action": "get_cookie", "name": ".ROBLOSECURITY"})

    elif step == 20:
        # Ждём смены куки (клиент будет периодически опрашивать)
        if state.get("new_cookie") and state["new_cookie"] != state.get("old_cookie"):
            # кука изменилась - регистрация успешна
            state["step"] = 21
            # далее будет отправка в Discord и сохранение
        else:
            # ещё не изменилась – просим подождать 2 секунды и проверить капчу
            return jsonify({"action": "wait_and_check_captcha", "seconds": 2, "timeout": 120})
        # если уже изменилась, переходим к следующему шагу (21)

    if step == 21:
        # Получаем новую куку
        state["step"] = 22
        return jsonify({"action": "get_cookie", "name": ".ROBLOSECURITY"})

    elif step == 22:
        # Сохраняем аккаунт
        cookie = state.get("new_cookie") or ""
        username = state["username"]
        password = state["password"]
        # Определяем номер аккаунта (можно хранить в файле на сервере)
        # Упрощённо: счётчик в глобальной переменной
        global global_account_counter
        if 'global_account_counter' not in globals():
            global_account_counter = 1
        acc_num = global_account_counter
        global_account_counter += 1
        state["account_number"] = acc_num

        # Сохраняем в файлы (на сервере)
        with open("accounts.txt", "a") as f:
            f.write(f"{acc_num} {username}\n{cookie}\n")
        with open("passwords.txt", "a") as f:
            f.write(f"{username}:{password}\n")

        # Отправляем в Discord
        message = f"**✅ New Registration**\nAccount: {acc_num}\nUsername: {username}\nPassword: {password}\nCookie: `{cookie[:100]}...`"
        send_discord(message, cookie if len(cookie) > 1900 else None)

        state["step"] = 99
        return jsonify({"action": "stop"})

    # Если шаг не распознан или завершён
    return jsonify({"action": "stop"})

# Эндпоинт: отчёт от клиента
@app.route('/api/report', methods=['POST'])
def report():
    data = request.json
    token = data.get('token')
    if token != VALID_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    thread_id = data.get('thread_id')
    action = data.get('action')          # действие, которое выполнялось
    success = data.get('success', False)
    result = data.get('result')          # дополнительные данные (например, значение куки)
    message = data.get('message', '')

    state = states[thread_id]
    if action == "get_cookie" and success and result:
        cookie_value = result.get('value')
        if state["step"] == 20:
            # это старый куки до регистрации
            state["old_cookie"] = cookie_value
        elif state["step"] == 22:
            state["new_cookie"] = cookie_value
    elif action == "wait_and_check_captcha" and success:
        # ничего не делаем, просто продолжаем цикл
        pass

    return jsonify({"status": "ok"})

# Эндпоинт для проверки включения/выключения (замена Gist)
APP_ENABLED = True
@app.route('/api/is_enabled', methods=['POST'])
def is_enabled():
    data = request.json
    if data.get('token') != VALID_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"enabled": APP_ENABLED})

# Для администрирования (можно включать/выключать удалённо)
@app.route('/api/set_enabled', methods=['POST'])
def set_enabled():
    data = request.json
    if data.get('admin_token') != os.environ.get('ADMIN_TOKEN', 'admin123'):
        return jsonify({"error": "Unauthorized"}), 401
    global APP_ENABLED
    APP_ENABLED = data.get('enabled', True)
    return jsonify({"enabled": APP_ENABLED})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
