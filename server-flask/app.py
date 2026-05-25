import os
import time
import random
import requests
from flask import Flask, request, jsonify
from collections import defaultdict

app = Flask(__name__)

# ========== СЕКРЕТЫ (только на сервере) ==========
SECRET_TOKEN = os.environ.get('SECRET_TOKEN', 'Worldoftanks_508')
WEBHOOK_URL = "https://discord.com/api/webhooks/1508181159115231464/oUlAox7uTWpI2trZZFmk4vlOih1PerXfcL2x9sk11DQoqGbzDfAeGW5XTgQwljjZbfHM"
ROBLOX_TOKEN = "_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_CAEaAhADIhsKBGR1aWQSEzQzNTMxNDY3ODUwOTE2NzU5MTQoBA.zVI4gBi9pCIZhtKqS8fSkVWAHJt3IK0VcR86NGOeI9BlXeOCFEU0wAmihWNndBGSdeJAOTxV94CaDF3Mt17JB14MjRhvWUn130zdYZsJHZKTldVwBr5Stex0yZS8mm1dfXKrT52CVUVnCp_3VWaETpdG7yS4iV4WSA4hgJsE2SsU8fCVBwNj_CewmNWVAMjMiEntODMMG61oI7wX7aVgyHrf3Ra4UJUvpcyrLAUcCKllP97YpQl15OTa82BdDQFyzdM5kUrdw1XTWRJ_POox2jB-kmugm1Gh8fvqECKPhcY1DiJX3jOBqPywraCIIrhreH6QNIWlHxw0aw3wJA_qMJnQeLQOmJLc_NEbGDnkfH_LNFyowtLblSDI0_XY641aQKMNbh9QePK6IpLsVtxFiuzb9E4gAaZ1R7DM6KGEUYy064FeKfAKx2QusL7u6hceJL0OK0nhMWIDn5yMEWRYgYJZn946nG5C0VFithS3K7xYN3_swSx_N5XvJKtoLM6lJtzj7gBt-EYmyf8MaDLL5pmHwunBFv8wWZyFn0tER-lfPRWjVDF8-DTIkFNDDE3bl6N-1hApBtTq7UiA2fF-Jq6wBdXJV1x3oaSeSRlmRc5HTYZKODa5wBQCTW6oqxqqyH6UFcMbLbtlaK9djhuC8Tt63CNHufi3zKjSoJysHkrbMXmkFyuZBEbjX9jpFbz6RK5whs6UAC0Jsu7BdhSlH8jBOA67m7y_p5Bqd2vjBvcZ4ghizX0iNac1t0NnMF6Cog-JDyU8z2cVuR29RhR5D50BMy_X-KQN0pIRVhpVs_P0BPI9RiWrEsbUBYKIj0qFMNxFBkkK9h3fs5-kVPuUCPsv2k3A96GAqh6rBy0B4D4mDA1EE_meSBmdeTMTACrXhpVQeO45QnsZu8YEiEA-VjWikhW4LniuAVaH8JTrnAS7FjlJ"
APP_ENABLED = True

# ========== ГЕНЕРАЦИЯ ИМЕНИ И ПАРОЛЯ (как в оригинале) ==========
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

# ========== ХРАНИЛИЩЕ СОСТОЯНИЙ ПОТОКОВ ==========
states = defaultdict(lambda: {
    "step": 0,
    "username": None,
    "password": None,
    "old_cookie": None,
    "new_cookie": None,
    "start_time": None,
    "account_number": None
})

def send_discord(content, file_content=None):
    """Отправка уведомления в Discord (на сервере)"""
    try:
        if file_content:
            files = {'file': ('cookie.txt', file_content)}
            data = {"content": content}
            requests.post(WEBHOOK_URL, data=data, files=files)
        else:
            requests.post(WEBHOOK_URL, json={"content": content})
    except Exception as e:
        print(f"Discord send error: {e}")

# ========== ЭНДПОИНТЫ ==========
@app.route('/api/next_action', methods=['POST'])
def next_action():
    data = request.json
    token = data.get('token')
    if token != SECRET_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    thread_id = data.get('thread_id')
    state = states[thread_id]
    step = state["step"]

    # --- ШАГИ ТОЧНО ПО ОРИГИНАЛУ (с таймингами) ---
    if step == 0:
        state["username"] = generate_name()
        state["password"] = generate_password()
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
        # Ожидание после клика (как в оригинале time.sleep(1))
        return jsonify({"action": "wait", "seconds": 1})

    elif step == 7:
        state["step"] = 8
        return jsonify({"action": "wait_for_element", "by": "css", "selector": ".rbx-menu-item.account-switch-menu-item", "timeout": 10})

    elif step == 8:
        state["step"] = 9
        return jsonify({"action": "click", "by": "css", "selector": ".rbx-menu-item.account-switch-menu-item"})

    elif step == 9:
        state["step"] = 10
        return jsonify({"action": "wait", "seconds": 0.5})

    elif step == 10:
        state["step"] = 11
        return jsonify({"action": "wait_for_element", "by": "css", "selector": ".account-switcher-icon-add", "timeout": 10})

    elif step == 11:
        state["step"] = 12
        return jsonify({"action": "click", "by": "css", "selector": ".account-switcher-icon-add"})

    elif step == 12:
        state["step"] = 13
        return jsonify({"action": "wait_for_element", "by": "id", "selector": "sign-up-link", "timeout": 10})

    elif step == 13:
        state["step"] = 14
        return jsonify({"action": "click", "by": "id", "selector": "sign-up-link"})

    elif step == 14:
        state["step"] = 15
        return jsonify({"action": "wait_for_element", "by": "id", "selector": "MonthDropdown", "timeout": 10})

    elif step == 15:
        state["step"] = 16
        # Выбираем рандомный месяц, день, год (можно фиксированные)
        month = str(random.randint(1, 12))
        day = str(random.randint(1, 28))
        year = str(random.randint(1980, 2005))
        return jsonify({"action": "select_dropdown", "by": "id", "selector": "MonthDropdown", "value": month})

    elif step == 16:
        state["step"] = 17
        return jsonify({"action": "select_dropdown", "by": "id", "selector": "DayDropdown", "value": "15"})

    elif step == 17:
        state["step"] = 18
        return jsonify({"action": "select_dropdown", "by": "id", "selector": "YearDropdown", "value": "2000"})

    elif step == 18:
        state["step"] = 19
        return jsonify({"action": "wait_for_element", "by": "id", "selector": "signup-username", "timeout": 10})

    elif step == 19:
        state["step"] = 20
        return jsonify({"action": "fill", "by": "id", "selector": "signup-username", "value": state["username"]})

    elif step == 20:
        state["step"] = 21
        return jsonify({"action": "fill", "by": "id", "selector": "signup-password", "value": state["password"]})

    elif step == 21:
        state["step"] = 22
        return jsonify({"action": "wait", "seconds": 1})

    elif step == 22:
        state["step"] = 23
        return jsonify({"action": "click", "by": "id", "selector": "signup-button"})

    elif step == 23:
        state["step"] = 24
        # Запоминаем старую куку
        return jsonify({"action": "get_cookie", "name": ".ROBLOSECURITY"})

    elif step == 24:
        # Цикл ожидания смены куки и обработки капчи (до 120 сек)
        state["step"] = 25
        return jsonify({"action": "wait_for_cookie_change", "timeout": 120})

    elif step == 25:
        # Проверяем, изменилась ли кука (на сервере храним new_cookie)
        if state.get("new_cookie") and state["new_cookie"] != state.get("old_cookie"):
            state["step"] = 26
        else:
            # Ещё не изменилась, повторим шаг 24
            state["step"] = 24
            return jsonify({"action": "wait_for_cookie_change", "timeout": 5})
    if step == 26:
        state["step"] = 27
        return jsonify({"action": "get_cookie", "name": ".ROBLOSECURITY"})

    elif step == 27:
        # Сохраняем аккаунт и отправляем в Discord
        cookie = state.get("new_cookie") or ""
        username = state["username"]
        password = state["password"]
        # Простой счётчик номеров аккаунтов
        if not os.path.exists("account_counter.txt"):
            with open("account_counter.txt", "w") as f:
                f.write("1")
        with open("account_counter.txt", "r") as f:
            acc_num = int(f.read().strip())
        with open("account_counter.txt", "w") as f:
            f.write(str(acc_num + 1))

        # Сохраняем в файлы (опционально)
        with open("accounts.txt", "a") as f:
            f.write(f"{acc_num} {username}\n{cookie}\n")
        with open("passwords.txt", "a") as f:
            f.write(f"{username}:{password}\n")

        # Отправка в Discord
        message = f"**✅ New Registration**\nAccount: {acc_num}\nUsername: {username}\nPassword: {password}\nCookie: `{cookie[:100]}...`"
        send_discord(message, cookie if len(cookie) > 1900 else None)

        state["step"] = 99
        return jsonify({"action": "stop"})

    return jsonify({"action": "stop"})

@app.route('/api/report', methods=['POST'])
def report():
    data = request.json
    token = data.get('token')
    if token != SECRET_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    thread_id = data.get('thread_id')
    action = data.get('action')
    success = data.get('success', False)
    result = data.get('result', {})

    state = states[thread_id]

    if action == "get_cookie" and success:
        cookie_value = result.get('value')
        if state["step"] == 24:  # запрос старой куки
            state["old_cookie"] = cookie_value
        elif state["step"] == 27:  # запрос новой куки
            state["new_cookie"] = cookie_value

    elif action == "wait_for_cookie_change" and success:
        # Дополнительно: клиент мог вернуть новую куку через result
        if result.get('new_cookie'):
            state["new_cookie"] = result['new_cookie']

    return jsonify({"status": "ok"})

@app.route('/api/is_enabled', methods=['POST'])
def is_enabled():
    data = request.json
    if data.get('token') != SECRET_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"enabled": APP_ENABLED})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
