from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext

async def get_chat_id(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type
    await update.message.reply_text(f"Este es el Chat ID: {chat_id}\nTipo de chat: {chat_type}")
    print(f"Chat ID: {chat_id}, Tipo: {chat_type}")

def main():
    TOKEN = '7960598167:AAHebdzdX9DY2yYvcaGSDP0U6csATq87nyk'

    # Configurar la aplicación del bot
    application = Application.builder().token(TOKEN).build()

    # Agregar manejador para capturar cualquier mensaje
    application.add_handler(MessageHandler(filters.ALL, get_chat_id))

    # Ejecutar el bot
    application.run_polling()

if __name__ == "__main__":
    main()
