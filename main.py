import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, filters, MessageHandler
import time
import pars  # Импортируем файл с функциями парсинга

# Настройки логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Хранилище для последнего запроса пользователей
last_request_time = {}

# Функция для формирования основного меню
def build_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("Поиск", callback_data='search')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка команды /start"""
    await update.message.reply_text("Привет! Я бот для поиска информации. Выберите действие:", reply_markup=build_menu())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка команды /help"""
    help_text = (
        "Используйте кнопку \"Поиск\", чтобы задать вопрос. Просто нажмите на кнопку и введите ваш вопрос.\n"
        "Бот выполнит поиск информации по вашему запросу.\n\n"
        "Если получите ответ, вы можете выбрать его, и бот предоставит вам ссылку на источник.\n\n"
        "Я не умею обрабатывать медиа-запросы, такие как фото, видео или голосовые сообщения."
    )
    await update.message.reply_text(help_text, reply_markup=build_menu())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка нажатий на кнопки"""
    query = update.callback_query
    await query.answer()

    if query.data == 'search':
        await query.edit_message_text("Пожалуйста, введите ваш вопрос:", reply_markup=build_menu())
        return

    if query.data == 'help':
        await help_command(update, context)
        return

    # Обработка выбора результата
    result_index = int(query.data)
    selected_title = context.user_data['titles'][result_index]

    # Получение URL и контента
    url, additional_info = await pars.fetch_website_content(selected_title)

    await query.edit_message_text(
        f"Вы выбрали результат: {selected_title}\n\nСсылка: {url}\n\nДополнительная информация:\n{additional_info}",
        reply_markup=build_menu()
    )

async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка вопросов пользователей"""
    user_id = update.message.from_user.id
    current_time = time.time()

    if user_id in last_request_time and current_time - last_request_time[user_id] < 20:
        await update.message.reply_text("Пожалуйста, подождите 20 секунд перед следующим запросом.", reply_markup=build_menu())
        return

    last_request_time[user_id] = current_time
    question = update.message.text
    await update.message.reply_text(f"Ищу информацию по вашему запросу: {question}...", reply_markup=build_menu())

    # Вызываем функцию для поиска заголовков
    titles = await pars.get_titles_from_google_custom_search(question)

    context.user_data['titles'] = titles

    if titles:
        keyboard = []
        for i, title in enumerate(set(titles)):
            # Каждая кнопка в отдельной строке
            keyboard.append([InlineKeyboardButton(title, callback_data=str(i))])

        reply_markup = InlineKeyboardMarkup(keyboard)  # Каждая кнопка в отдельной строке
        await update.message.reply_text("Вот несколько заголовков из результатов поиска:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Не удалось найти результаты по вашему запросу.", reply_markup=build_menu())

# Обработка медиа-запросов
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка неподдерживаемых медиа-запросов"""
    await update.message.reply_text(
        "Я не умею обрабатывать медиа-запросы, такие как фото, видео или голосовые сообщения.",
        reply_markup=build_menu()
    )

def main() -> None:
    """Основная функция для запуска бота."""
    application = ApplicationBuilder().token("7704297845:AAFdly3YQu6xhwzVWUsjNEJkUj2w4PtYQIQ").build()

    # Регистрация обработчиков команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question))

    # Обработка медиа-запросов
    application.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.VOICE, handle_media))

    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()
