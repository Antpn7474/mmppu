import os
import json
import datetime
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

BOT_TOKEN = "7578917097:AAHJa_8tvC91Y9G8Ca9eTP9yLquFsFb4-UI" # Лучше в переменной среды!
ADMIN_IDS = [1618247541]
DATA_FILE = "suggestions.json"

SUGGESTION, PHOTO_UPLOAD = range(2)
LIST_SUGGESTIONS, VIEW_SUGGESTION, COMMENT_INPUT = range(3, 6)
USER_CHAT = 6

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def is_admin(user_id):
    return user_id in ADMIN_IDS

def get_user_menu():
    keyboard = [
        [KeyboardButton("Подать предложение по улучшению")],
        [KeyboardButton("Посмотреть историю предложений")],
        [KeyboardButton("Важная информация")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_admin_menu():
    keyboard = [
        [KeyboardButton("Просмотреть все предложения")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_admin(user_id):
        await update.message.reply_text(
            "Привет, администратор! Выбери действие из меню.",
            reply_markup=get_admin_menu(),
        )
    else:
        await update.message.reply_text(
            'Привет! Данный бот создан для работников ООО "Мечел-Материалы", где каждый работник может написать свое предложение по улучшению процессов и условий работы! За каждое действенное предложение есть возможность получить вознаграждение! Отправьте свою идею, и мы обязательно её рассмотрим.',
            reply_markup=get_user_menu(),
        )

async def handle_important_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💎 Порядок подачи предложений по улучшению\n\n"
        "1. Работник формулирует предложение, направленное на повышение эффективности, снижения затрат или иное улучшение в деятельности. \n"
        "2. Оформляет предложение по форме и отправляет в телеграмм бот (Предложения по улучшениям Мечел-Материалы) или передает своему руководителю в подразделении. (руководитель должен выдать бланк) \n"
        "3. Предложение проходит экспертизу и получает один из статусов: \n"  
        " - «Принято к рассмотрению» - ваше предложение соответствует требованиям и принято к рассмотрению на техническом совете. \n"
        " - «Удовлетворено» - ваша идея внедрена на производстве (или в процессе внедрения). \n"
        " - «Отказано» - ваша идея не соответствует требованиям или возможностям на данный момент. (Требования смотри в конце) \n\n"
        "🏆 Вознаграждение за предложения по улучшению\n\n"
        "1. Вознаграждение автору (авторам) \n"
        "- За каждое принятое предложение, получившее на Техническом совете одобрение — выплата 500 рублей (единовременно). \n"
        "2. Вознаграждение за внедрение \n"
        "- Ответственному за внедрение каждого реализованного предложения — выплата 1000 рублей (единовременно за каждое ПУ).\n\n"
        "Если ваше предложение очень ценное, со всеми чертежами, расчетами и может принести прибыль предприятию, то необходимо оценить экономический эффект.\n\n"
        "💰 Вознаграждение за экономический эффект\n\n"
        "1. За достигнутый экономический эффект: \n"
        "- При годовом экономическом эффекте от 500 тыс. рублей до 1 млн руб. —  20 000 рублей (единовременно). \n"
        "- При годовом экономическом эффекте от 1 млн рублей и выше — 20 000 рублей и дополнительно 1,5% от суммы годового экономического эффекта, превышающего 1 миллион рублей. (Выплата не более 200 000 рублей. \n"
        "- Если экономический эффект невозможно определить количественно — от 5 000 до 20 000 рублей (по решению Технического совета).\n\n"
        "ТРЕБОВАНИЯ\n\n"
        "Предложение должно иметь:\n"
        "1. описание текущего состояния или проблемы; \n"
        "2. указание на изменяемый (улучшаемый) параметр и его величину «до» и «после»; \n"
        "3. описание действий по реализации и расчет затрат на реализацию (допускается указать «требует проработки»); \n"
        "4. указание условий, обязательных для получения эффекта (внешние факторы, сезонность, изменение требований к сырью, логистике и т.д.). \n\n"
        "Предложение должно решать:\n"
        "1. устранение потерь; \n"
        "2. снижение влияния вредных производственных факторов; \n"
        "3. совершенствование технологического процесса; \n"
        "4. увеличение эффективности оборудования или отдельных механизмов; \n"
        "5. увеличение производительности труда работников и улучшение условий труда; \n"
        "6. повышение качества продукции при реализации улучшения; \n"
        "7. снижение рисков преждевременного выхода из строя машин и механизмов; \n"
        "8. снижение уровня рисков получения некачественной продукции, нарушения правил ОТ и ПБ при выполнении технологических и ремонтных операций. \n\n"
        "Предложения, которые НЕ принимаются:\n"
        "1. внедренные ранее; \n"
        "2. уже используемые на предприятии; \n"
        "3. описывающие только основную идею или концепцию, но не предлагающие конкретного механизма реализации или решений проблемы; \n"
        "4. направленные на улучшение бытовых условий; \n"
        "5. созданные инженерно-техническими работниками в порядке выполнения служебного задания или должностных обязанностей. К данной категории не относятся специалисты, в чьи основные обязанности входит внедрение инструментов бережливого производства, а также РиС цехов.\n\n"
        "Примечание:\n"  
        "При наличии нескольких авторов/ответственных, выплата производится в равных долях, если иное не определено решением ТС. \n"
        "Если ранее было выплачено вознаграждение за прогнозный экономический эффект по ПУ, сумма окончательной выплаты уменьшается на ранее выплаченное вознаграждение. \n"
        "Все суммы указаны без учета НДФЛ и без учета районного коэффициента. "
    )

async def handle_view_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = load_data()
    user_suggestions = [s for s in data if s["user_id"] == user.id]

    if not user_suggestions:
        menu = get_admin_menu() if is_admin(user.id) else get_user_menu()
        await update.message.reply_text("У вас нет поданных предложений.", reply_markup=menu)
        return

    for s in user_suggestions:
        msg = (
            f"ID: {s['id']}\n"
            f"Дата: {s['date'][:19]}\n"
            f"Текст: {s['text']}\n"
            f"Статус: {s['status']}\n"
            f"Комментарий: {s['comment'] if s['comment'] else 'нет'}"
        )
        await update.message.reply_text(msg)
        
        if s.get('photos'):
            for photo_id in s['photos']:
                try:
                    await update.message.reply_photo(photo=photo_id)
                except Exception as e:
                    print(f"Ошибка отправки фото: {e}")
    
    menu = get_admin_menu() if is_admin(user.id) else get_user_menu()
    await update.message.reply_text("История предложений показана выше.", reply_markup=menu)

async def start_suggestion_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_admin(user_id):
        await update.message.reply_text(
            "Администраторы не могут подавать предложения. Ваша функция - просмотр и реакция на предложения других пользователей.",
            reply_markup=get_admin_menu()
        )
        return ConversationHandler.END
    
    await update.message.reply_text(
        "Пожалуйста, опишите вашу идею по пунктам:\n\n"
        "1. Отдел/место применения: где это будет действовать\n"
        "2. Подробное описание: что именно, как работает сейчас, что предлагаете изменить\n"
        "3. Выгода/эффект: экономия времени/денег, повышение безопасности, качество, удобство\n"
        "4. Примерный план внедрения: простые шаги, ресурсы\n"
        "5. Вложения: фото, схемы, расчёты\n\n"
        "Чтобы отменить нажмите /cancel.",
        reply_markup=ReplyKeyboardRemove()
    )
    return SUGGESTION

async def handle_new_suggestion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text.strip()

    if not text:
        await update.message.reply_text("Пустое предложение не может быть сохранено. Пожалуйста, введите текст или нажмите /cancel.")
        return SUGGESTION

    context.user_data["suggestion_text"] = text
    context.user_data["suggestion_photos"] = []

    await update.message.reply_text(
        "Теперь вы можете отправить 1 или несколько фото (по одному). "
        "После загрузки всех нужных — напишите /done. "
        "Если фото не нужны, также напишите /done. "
        "Для отмены — /cancel."
    )
    return PHOTO_UPLOAD

async def handle_photo_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        photo = update.message.photo[-1]
        file_id = photo.file_id
        context.user_data.setdefault("suggestion_photos", []).append(file_id)
        await update.message.reply_text("Фото добавлено. Если есть ещё — пришлите ещё. После окончания напишите /done.")
        return PHOTO_UPLOAD
    else:
        await update.message.reply_text("Пожалуйста, отправьте фото или завершите ввод командой /done.")
        return PHOTO_UPLOAD

async def handle_suggestion_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = context.user_data.get("suggestion_text")
    photos = context.user_data.get("suggestion_photos", [])
    data = load_data()
    suggestion_id = max([s["id"] for s in data], default=0) + 1

    new_suggestion = {
        "id": suggestion_id,
        "user_id": user.id,
        "user_name": user.full_name,
        "text": text,
        "date": datetime.datetime.now().isoformat(),
        "status": "Новый",
        "comment": "",
        "photos": photos,
        "chat_messages": []
    }
    data.append(new_suggestion)
    data.sort(key=lambda x: x["date"], reverse=True)
    save_data(data)

    context.user_data.pop("suggestion_text", None)
    context.user_data.pop("suggestion_photos", None)

    menu = get_admin_menu() if is_admin(user.id) else get_user_menu()

    await update.message.reply_text(
        f"Спасибо! Ваше предложение зарегистрировано под №{suggestion_id}. "
        f"Ответ будет в этом боте, а также вы сможете наблюдать статус вашего обращения!",
        reply_markup=menu
    )
    
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"Новое предложение №{suggestion_id} от {user.full_name}:\n\n{text[:200]}{'...' if len(text) > 200 else ''}"
            )
        except Exception as e:
            print(f"Ошибка при уведомлении админа {admin_id}: {e}")
    
    return ConversationHandler.END

async def send_suggestions_list_message(update_or_query_or_message, context):
    data = load_data()
    if not data:
        text = "Пока нет предложений."
        reply_markup = None
    else:
        text = "Выберите предложение для просмотра:"
        keyboard = []
        for s in data:
            btn_text = f"ID {s['id']}: {s['text'][:25]}{'...' if len(s['text']) > 25 else ''}"
            keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"view_{s['id']}")])
        reply_markup = InlineKeyboardMarkup(keyboard)

    if isinstance(update_or_query_or_message, Update):
        await update_or_query_or_message.message.reply_text(text, reply_markup=reply_markup)
    elif hasattr(update_or_query_or_message, 'edit_message_text'):
        await update_or_query_or_message.edit_message_text(text, reply_markup=reply_markup)
    else:
        await context.bot.send_message(chat_id=update_or_query_or_message.effective_chat.id, text=text, reply_markup=reply_markup)

async def send_detailed_suggestion_message(update_or_query, context, suggestion_id):
    data = load_data()
    suggestion = next((s for s in data if s["id"] == suggestion_id), None)

    if not suggestion:
        text = "Предложение не найдено."
        reply_markup = None
        if hasattr(update_or_query, 'edit_message_text'):
            await update_or_query.edit_message_text(text)
        elif hasattr(update_or_query, 'reply_text'):
            await update_or_query.reply_text(text)
        else:
            await update_or_query.message.reply_text(text)
        return

    text = (
        f"ID: {suggestion['id']}\n"
        f"Пользователь: {suggestion['user_name']} (id: {suggestion['user_id']})\n"
        f"Дата: {suggestion['date'][:19]}\n"
        f"Текст: {suggestion['text']}\n"
        f"Статус: {suggestion['status']}\n"
        f"Комментарий: {suggestion['comment'] if suggestion['comment'] else 'нет'}\n"
        f"Фото: {len(suggestion.get('photos', []))} шт.\n\n"
        "Выберите действие:"
    )
    keyboard = [
        [
            InlineKeyboardButton("Принято к рассмотрению", callback_data=f"status_{suggestion_id}_Принято к рассмотрению"),
        ],
        [
            InlineKeyboardButton("Удовлетворено", callback_data=f"status_{suggestion_id}_Удовлетворено"),
            InlineKeyboardButton("Отказано", callback_data=f"status_{suggestion_id}_Отказано"),
        ],
        [InlineKeyboardButton("Добавить комментарий", callback_data=f"comment_{suggestion_id}")],
        [InlineKeyboardButton("Чат с пользователем", callback_data=f"chat_{suggestion_id}")],
    ]
    
    if suggestion.get('photos'):
        keyboard.append([InlineKeyboardButton("Показать фото", callback_data=f"showphotos_{suggestion_id}")])
    
    keyboard.append([InlineKeyboardButton("Назад", callback_data="back_to_list")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    if hasattr(update_or_query, 'edit_message_text'):
        await update_or_query.edit_message_text(text, reply_markup=reply_markup)
    elif hasattr(update_or_query, 'reply_text'):
        await update_or_query.reply_text(text, reply_markup=reply_markup)
    else:
        await update_or_query.message.reply_text(text, reply_markup=reply_markup)

async def start_admin_suggestions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("У вас нет прав для этого действия.")
        return ConversationHandler.END

    await send_suggestions_list_message(update, context)
    return LIST_SUGGESTIONS

async def handle_list_suggestions_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        await query.edit_message_text("У вас нет прав для этого действия.")
        return ConversationHandler.END

    data_payload = query.data
    if data_payload.startswith("view_"):
        suggestion_id = int(data_payload.split("_")[1])
        await send_detailed_suggestion_message(query, context, suggestion_id)
        context.user_data["current_suggestion_id"] = suggestion_id
        return VIEW_SUGGESTION
    
    return LIST_SUGGESTIONS

async def handle_view_suggestion_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        await query.edit_message_text("У вас нет прав для этого действия.")
        return ConversationHandler.END

    data_payload = query.data
    data = load_data()

    if data_payload.startswith("status_"):
        parts = data_payload.split("_", 2)
        suggestion_id = int(parts[1])
        new_status = parts[2]
        
        suggestion = next((s for s in data if s["id"] == suggestion_id), None)
        if suggestion:
            suggestion["status"] = new_status
            save_data(data)
            try:
                await context.bot.send_message(
                    chat_id=suggestion["user_id"],
                    text=f"Статус вашего предложения №{suggestion_id} обновлён на: {new_status}",
                )
            except Exception as e:
                print(f"Ошибка при уведомлении пользователя: {e}")
            
            await send_detailed_suggestion_message(query, context, suggestion_id)
            return VIEW_SUGGESTION
        else:
            await query.edit_message_text("Предложение не найдено.")
            await send_suggestions_list_message(query, context)
            return LIST_SUGGESTIONS

    elif data_payload.startswith("comment_"):
        suggestion_id = int(data_payload.split("_")[1])
        context.user_data["comment_for"] = suggestion_id
        await query.edit_message_text(
            f"Пожалуйста, отправьте комментарий к предложению №{suggestion_id}.\n"
            "Для отмены нажмите /cancel, для завершения ввода комментария нажмите /done."
        )
        return COMMENT_INPUT

    elif data_payload.startswith("chat_"):
        suggestion_id = int(data_payload.split("_")[1])
        suggestion = next((s for s in data if s["id"] == suggestion_id), None)
        if suggestion:
            context.user_data["chat_suggestion_id"] = suggestion_id
            chat_messages = suggestion.get("chat_messages", [])
            
            if chat_messages:
                msg_text = f"История чата по предложению №{suggestion_id}:\n\n"
                for msg in chat_messages[-10:]:
                    msg_text += f"{msg['from']}: {msg['text']}\n{msg['date'][:16]}\n\n"
            else:
                msg_text = f"Чат по предложению №{suggestion_id} пуст.\n\n"
            
            msg_text += "Отправьте сообщение пользователю или /done для выхода."
            
            await query.edit_message_text(msg_text)
            return COMMENT_INPUT
        else:
            await query.edit_message_text("Предложение не найдено.")
            return VIEW_SUGGESTION

    elif data_payload.startswith("showphotos_"):
        suggestion_id = int(data_payload.split("_")[1])
        suggestion = next((s for s in data if s["id"] == suggestion_id), None)
        if suggestion and suggestion.get('photos'):
            await query.answer("Отправляю фото...")
            for photo_id in suggestion['photos']:
                try:
                    await context.bot.send_photo(
                        chat_id=query.message.chat_id,
                        photo=photo_id,
                        caption=f"Фото из предложения №{suggestion_id}"
                    )
                except Exception as e:
                    print(f"Ошибка отправки фото: {e}")
        else:
            await query.answer("Фото не найдены.")
        return VIEW_SUGGESTION

    elif data_payload == "back_to_list":
        await send_suggestions_list_message(query, context)
        context.user_data.pop("current_suggestion_id", None)
        return LIST_SUGGESTIONS
    
    return VIEW_SUGGESTION

async def comment_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("У вас нет прав оставлять комментарии.")
        return ConversationHandler.END

    comment_for = context.user_data.get("comment_for")
    chat_suggestion_id = context.user_data.get("chat_suggestion_id")
    
    if chat_suggestion_id:
        suggestion_id = chat_suggestion_id
        comment_text = update.message.text.strip()

        if comment_text.startswith('/done'):
            await update.message.reply_text("Чат завершён.")
            context.user_data.pop("chat_suggestion_id", None)
            await send_detailed_suggestion_message(update.message, context, suggestion_id)
            return VIEW_SUGGESTION
        elif comment_text.startswith('/cancel'):
            await update.message.reply_text("Чат отменён.")
            context.user_data.pop("chat_suggestion_id", None)
            await send_detailed_suggestion_message(update.message, context, suggestion_id)
            return VIEW_SUGGESTION
        else:
            data = load_data()
            suggestion = next((s for s in data if s["id"] == suggestion_id), None)

            if not suggestion:
                await update.message.reply_text("Предложение не найдено.")
                context.user_data.pop("chat_suggestion_id", None)
                return ConversationHandler.END

            if "chat_messages" not in suggestion:
                suggestion["chat_messages"] = []
            
            suggestion["chat_messages"].append({
                "from": "Администратор",
                "text": comment_text,
                "date": datetime.datetime.now().isoformat()
            })
            save_data(data)

            try:
                await context.bot.send_message(
                    chat_id=suggestion["user_id"],
                    text=f"Сообщение от администратора по предложению №{suggestion_id}:\n\n{comment_text}"
                )
            except Exception as e:
                print(f"Ошибка при уведомлении пользователя: {e}")

            await update.message.reply_text(
                "Сообщение отправлено. Напишите ещё или /done для выхода."
            )
            return COMMENT_INPUT
    
    elif comment_for:
        suggestion_id = comment_for
        comment_text = update.message.text.strip()

        if comment_text.startswith('/done'):
            await update.message.reply_text("Ввод комментария завершён.")
            context.user_data.pop("comment_for", None)
            await send_detailed_suggestion_message(update.message, context, suggestion_id)
            return VIEW_SUGGESTION
        elif comment_text.startswith('/cancel'):
            await update.message.reply_text("Ввод комментария отменён.")
            context.user_data.pop("comment_for", None)
            await send_detailed_suggestion_message(update.message, context, suggestion_id)
            return VIEW_SUGGESTION
        else:
            data = load_data()
            suggestion = next((s for s in data if s["id"] == suggestion_id), None)

            if not suggestion:
                await update.message.reply_text("Предложение не найдено.")
                context.user_data.pop("comment_for", None)
                return ConversationHandler.END

            if suggestion["comment"]:
                suggestion["comment"] += "\n" + comment_text
            else:
                suggestion["comment"] = comment_text
            save_data(data)

            try:
                await context.bot.send_message(
                    chat_id=suggestion["user_id"],
                    text=f"К вашему предложению №{suggestion_id} добавлен комментарий:\n{comment_text}",
                )
            except Exception as e:
                print(f"Ошибка при уведомлении пользователя: {e}")

            await update.message.reply_text(
                "Комментарий добавлен. Если хотите добавить ещё, напишите текст, "
                "или нажмите /done для завершения, /cancel для отмены."
            )
            return COMMENT_INPUT
    else:
        await update.message.reply_text("Ошибка: не найдено предложение для комментария.")
        return ConversationHandler.END

async def handle_user_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    if is_admin(user.id):
        return
    
    message_text = update.message.text
    
    if message_text in ["Подать предложение по улучшению", "Посмотреть историю предложений", "Важная информация"]:
        return
    
    data = load_data()
    user_suggestions = [s for s in data if s["user_id"] == user.id]
    
    if not user_suggestions:
        return
    
    active_suggestions = [s for s in user_suggestions if s.get("chat_messages")]
    if active_suggestions:
        latest_suggestion = active_suggestions[0]
    else:
        latest_suggestion = user_suggestions[0]
    
    suggestion_id = latest_suggestion["id"]
    
    if "chat_messages" not in latest_suggestion:
        latest_suggestion["chat_messages"] = []
    
    latest_suggestion["chat_messages"].append({
        "from": user.full_name,
        "text": message_text,
        "date": datetime.datetime.now().isoformat()
    })
    save_data(data)
    
    await update.message.reply_text(
        f"Ваше сообщение по предложению №{suggestion_id} отправлено администратору."
    )
    
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"Новое сообщение от {user.full_name} по предложению №{suggestion_id}:\n\n{message_text}"
            )
        except Exception as e:
            print(f"Ошибка при уведомлении админа {admin_id}: {e}")

async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    menu = get_admin_menu() if is_admin(user_id) else get_user_menu()
    await update.message.reply_text("Действие отменено.", reply_markup=menu)
    
    context.user_data.pop("comment_for", None)
    context.user_data.pop("current_suggestion_id", None)
    context.user_data.pop("suggestion_text", None)
    context.user_data.pop("suggestion_photos", None)
    context.user_data.pop("chat_suggestion_id", None)

    return ConversationHandler.END

def main():
    if not BOT_TOKEN:
        print("ОШИБКА: BOT_TOKEN не установлен!")
        print("Пожалуйста, установите переменную окружения BOT_TOKEN в Secrets.")
        return
    
    if not ADMIN_IDS:
        print("ВНИМАНИЕ: ADMIN_IDS не установлен!")
        print("Пожалуйста, установите переменную окружения ADMIN_IDS в Secrets.")
        print("Формат: 1234567890,9876543210 (ID администраторов через запятую)")
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^Важная информация$"), handle_important_info))
    app.add_handler(MessageHandler(filters.Regex("^Посмотреть историю предложений$"), handle_view_history))

    suggestion_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Подать предложение по улучшению$"), start_suggestion_flow)],
        states={
            SUGGESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_new_suggestion)],
            PHOTO_UPLOAD: [
                MessageHandler(filters.PHOTO, handle_photo_upload),
                CommandHandler("done", handle_suggestion_done),
                CommandHandler("cancel", cancel_handler),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_handler)],
    )

    app.add_handler(suggestion_conv)

    admin_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^Просмотреть все предложения$"), start_admin_suggestions)
        ],
        states={
            LIST_SUGGESTIONS: [
                CallbackQueryHandler(handle_list_suggestions_callbacks, pattern="^view_\\d+$")
            ],
            VIEW_SUGGESTION: [
                CallbackQueryHandler(handle_view_suggestion_callbacks, pattern="^(status_\\d+_.+|comment_\\d+|chat_\\d+|showphotos_\\d+|back_to_list)$")
            ],
            COMMENT_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, comment_text_handler),
                CommandHandler("cancel", cancel_handler),
                CommandHandler("done", cancel_handler),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_handler),
            CommandHandler("start", cancel_handler)
        ],
        per_message=False,
    )
    app.add_handler(admin_conv)
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_reply))

    print("Бот запущен и готов к работе!")
    app.run_polling()

if __name__ == "__main__":
    main()
