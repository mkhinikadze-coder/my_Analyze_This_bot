# -*- coding: utf-8 -*-
"""
თვითანალიზის ტელეგრამ-ბოტი — მთავარი ფაილი.
გაშვება: python bot.py
საჭირო env ცვლადები: TELEGRAM_BOT_TOKEN, GEMINI_API_KEY
"""
import logging
import os
import random
import threading
from datetime import time as dtime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.error import TelegramError
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PersistenceInput,
    PicklePersistence,
    filters,
)

import texts as T
from ai_client import get_ai_analysis

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
DELETE_AFTER_SECONDS = 15 * 60  # 15 წუთი
RANDOM_QUESTION_COUNT = 7  # "🎯 შერჩევითი კითხვები" რეჟიმზე რამდენი აირჩევა 46-დან
REMINDER_HOUR = int(os.environ.get("REMINDER_HOUR", "21"))
REMINDER_MINUTE = int(os.environ.get("REMINDER_MINUTE", "0"))
PERSISTENCE_PATH = os.environ.get("PERSISTENCE_PATH", "bot_persistence.pickle")

# Render-ის (და მისნაირი) "Web Service" (უფასო) ტიპს სჭირდება, რომ პროცესი
# რაღაც პორტს უსმენდეს, თორემ ის ფიქრობს, რომ სერვისი "მკვდარია" და
# თვითონვე შლის. ბოტი კი თავად მუშაობს polling-ით (Telegram-ს თავად ეკითხება
# ახალ შეტყობინებებზე) და პორტი საერთოდ არ სჭირდება — ამიტომ უბრალოდ
# ვუშვებთ პატარა, დამოუკიდებელ "საცნობარო" (health-check) სერვერს იმავე
# პროცესში, ცალკე thread-ში, მხოლოდ იმისთვის, რომ Render დარწმუნდეს, რომ
# პორტი ღიაა.
PORT = int(os.environ.get("PORT", "8080"))


class _HealthCheckHandler(BaseHTTPRequestHandler):
    """მხოლოდ იმისთვის, რომ Render-ის პორტის შემოწმება წარმატებული იყოს."""

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("ბოტი მუშაობს ✅".encode("utf-8"))

    def do_HEAD(self):
        # UptimeRobot-ის HTTP(s) მონიტორი HEAD მოთხოვნებს იყენებს — ამის
        # გარეშე BaseHTTPRequestHandler უბრალოდ 501-ს აბრუნებს და
        # UptimeRobot ფიქრობს, რომ ბოტი "Down"-ია.
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()

    def log_message(self, format, *args):
        pass  # რომ არ დაისვათ ლოგები ამ მოთხოვნებით


def _start_health_server():
    try:
        server = HTTPServer(("0.0.0.0", PORT), _HealthCheckHandler)
        logger.info("საცნობარო სერვერი გაეშვა 0.0.0.0:%s-ზე", PORT)
        server.serve_forever()
    except Exception:
        logger.exception("საცნობარო სერვერის გაშვება ვერ მოხერხდა")


# ---------- დამხმარე ფუნქციები ----------

def get_lang(context: ContextTypes.DEFAULT_TYPE) -> str | None:
    return context.user_data.get("lang")


def lang_keyboard() -> InlineKeyboardMarkup:
    row = [InlineKeyboardButton(T.LANG_NAMES[l], callback_data=f"lang:{l}") for l in T.LANGS]
    return InlineKeyboardMarkup([row])


def welcome_text(lang: str) -> str:
    return (
        f"{T.WELCOME_INTRO[lang]}\n\n"
        f"🙏 {T.PRAYER[lang]}\n\n"
        f"{T.DELETE_NOTICE[lang]}"
    )


def welcome_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(T.BTN_START[lang], callback_data="start_analysis")],
            [InlineKeyboardButton(T.BTN_RANDOM[lang], callback_data="start_random")],
            [InlineKeyboardButton(T.BTN_LANG_CHANGE[lang], callback_data="show_lang")],
        ]
    )


def render_transcript(lang: str, qa_pairs: list[tuple[str, str]]) -> str:
    lines = []
    for i, (q, a) in enumerate(qa_pairs, start=1):
        lines.append(f"*{i}. {q}*\n{a}")
    return "\n\n".join(lines)


def render_transcript_plain(lang: str, qa_pairs: list[tuple[str, str]]) -> str:
    """იგივე, მაგრამ Markdown-ის გარეშე — AI-ს პასუხთან შერევისას Telegram-ის
    Markdown-პარსერი ადვილად იმტვრევა მოულოდნელი სიმბოლოებისგან."""
    lines = []
    for i, (q, a) in enumerate(qa_pairs, start=1):
        lines.append(f"{i}. {q}\n{a}")
    return "\n\n".join(lines)


def question_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton(T.BTN_SKIP[lang], callback_data="skip")]])


def finish_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(T.BTN_FINISH[lang], callback_data="finish"),
          InlineKeyboardButton(T.BTN_AI[lang], callback_data="ai_analysis")]]
    )


def save_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(T.BTN_SAVE[lang], callback_data="save")],
            [InlineKeyboardButton(T.BTN_FINISH[lang], callback_data="close_now")],
        ]
    )


def result_keyboard(lang: str) -> InlineKeyboardMarkup:
    """AI ანალიზის წარმატებული შედეგის შემდეგ ნაჩვენები keyboard — "AI-ს
    ანალიზი" ღილაკი განზრახ რჩება ხელმისაწვდომი, რომ მომხმარებელს
    შეეძლოს ხელახლა გაუშვას ანალიზი იმავე პასუხებზე (მაგ. ტესტირებისას,
    ან უბრალოდ თუ სურს ახალი AI-პასუხის მიღება)."""
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(T.BTN_AI[lang], callback_data="ai_analysis")],
            [InlineKeyboardButton(T.BTN_SAVE[lang], callback_data="save")],
            [InlineKeyboardButton(T.BTN_FINISH[lang], callback_data="close_now")],
        ]
    )


async def send_question_view(update_msg, lang: str, session: dict):
    """ბოტის ერთი შეტყობინების რედაქტირება: ისტორია + შემდეგი კითხვა + Skip."""
    qidx = session["current_q"]
    total = len(session["questions"])
    transcript = render_transcript(lang, session["answers"])
    q_label = T.progress_label(lang, qidx + 1, total)
    question = session["questions"][qidx]
    parts = []
    if transcript:
        parts.append(transcript)
    parts.append(f"*{q_label}*\n{question}")
    text = "\n\n".join(parts)
    await update_msg.edit_text(text, reply_markup=question_keyboard(lang), parse_mode=ParseMode.MARKDOWN)


async def send_final_choice_view(bot_msg, lang: str, session: dict):
    transcript = render_transcript(lang, session["answers"])
    await bot_msg.edit_text(transcript, reply_markup=finish_keyboard(lang), parse_mode=ParseMode.MARKDOWN)


# ---------- job callback-ები ----------

async def delete_job(context: ContextTypes.DEFAULT_TYPE):
    data = context.job.data
    chat_id = data["chat_id"]
    lang = data.get("lang", "ka")
    for mid in data["message_ids"]:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=mid)
        except TelegramError:
            pass
    # წაშლის შემდეგ ცარიელ ჩატს არ ვტოვებთ — ვაგზავნით ახალ, მუდმივ
    # მისალმების შეტყობინებას "დაწყება" ღილაკით, რომ აღარც ტელეგრამის
    # "Start" ღილაკზე ვიყოთ დამოკიდებული და ხელითაც აღარ დასჭირდეს წერა.
    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=welcome_text(lang),
            reply_markup=welcome_keyboard(lang),
            parse_mode=ParseMode.MARKDOWN,
        )
    except TelegramError:
        logger.warning("წაშლის შემდეგ მისალმების გაგზავნა ვერ მოხერხდა chat_id=%s-სთვის", chat_id)


async def reminder_job(context: ContextTypes.DEFAULT_TYPE):
    data = context.job.data
    chat_id = data["chat_id"]
    lang = data.get("lang", "ka")
    try:
        await context.bot.send_message(chat_id=chat_id, text=T.REMINDER_PING[lang])
    except TelegramError:
        logger.warning("შეხსენების გაგზავნა ვერ მოხერხდა chat_id=%s-სთვის", chat_id)


def schedule_delete(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_ids: list[int], lang: str):
    context.job_queue.run_once(
        delete_job,
        when=timedelta(seconds=DELETE_AFTER_SECONDS),
        data={"chat_id": chat_id, "message_ids": message_ids, "lang": lang},
        name=f"delete_{chat_id}_{message_ids[0]}",
    )


def reschedule_delete(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_ids: list[int], lang: str):
    """აუქმებს ძველ, დაგეგმილ წაშლას (თუ არსებობს) და ხელახლა ნიშნავს
    ვადას თავიდან — გამოიყენება, როცა მომხმარებელი ისევ აქტიურად
    მუშაობს გვერდზე (მაგ. AI ანალიზს ხელახლა ითხოვს), რომ გვერდი
    ნაადრევად არ წაიშალოს."""
    job_name = f"delete_{chat_id}_{message_ids[0]}"
    for j in context.job_queue.get_jobs_by_name(job_name):
        j.schedule_removal()
    schedule_delete(context, chat_id, message_ids, lang)


# ---------- ბრძანებები ----------

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("session", None)
    lang = get_lang(context)
    if not lang:
        await update.message.reply_text(T.CHOOSE_LANG["ka"], reply_markup=lang_keyboard())
        return
    msg = await update.message.reply_text(
        welcome_text(lang), reply_markup=welcome_keyboard(lang), parse_mode=ParseMode.MARKDOWN
    )
    context.user_data["welcome_msg_id"] = msg.message_id


async def cmd_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(T.CHOOSE_LANG["ka"], reply_markup=lang_keyboard())


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context) or "ka"
    await update.message.reply_text(T.HELP_MSG[lang])


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context) or "ka"
    user_id = update.effective_user.id
    stats = context.bot_data.setdefault("stats", {})
    count = stats.get(user_id, 0)
    await update.message.reply_text(T.STATS_MSG[lang].format(count=count))


async def cmd_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context) or "ka"
    is_on = context.user_data.get("reminder_on", False)
    label = T.BTN_REMINDER_OFF[lang] if is_on else T.BTN_REMINDER_ON[lang]
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(label, callback_data="toggle_reminder")]])
    await update.message.reply_text(T.REMINDER_PROMPT[lang], reply_markup=kb)


# ---------- callback query-ები ----------

async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    if data.startswith("lang:"):
        lang = data.split(":", 1)[1]
        context.user_data["lang"] = lang
        await query.message.edit_text(
            welcome_text(lang), reply_markup=welcome_keyboard(lang), parse_mode=ParseMode.MARKDOWN
        )
        return

    if data == "show_lang":
        await query.message.edit_text(T.CHOOSE_LANG["ka"], reply_markup=lang_keyboard())
        return

    lang = get_lang(context) or "ka"

    if data == "start_analysis":
        context.user_data["session"] = {
            "answers": [],
            "current_q": 0,
            "bot_msg_id": query.message.message_id,
            "user_msg_ids": [],
            "chat_id": query.message.chat_id,
            "ai_text": None,
            "questions": list(T.QUESTIONS[lang]),
        }
        context.user_data["awaiting_answer"] = True
        await send_question_view(query.message, lang, context.user_data["session"])
        return

    if data == "start_random":
        context.user_data["session"] = {
            "answers": [],
            "current_q": 0,
            "bot_msg_id": query.message.message_id,
            "user_msg_ids": [],
            "chat_id": query.message.chat_id,
            "ai_text": None,
            "questions": random.sample(T.RANDOM_POOL[lang], RANDOM_QUESTION_COUNT),
        }
        context.user_data["awaiting_answer"] = True
        await send_question_view(query.message, lang, context.user_data["session"])
        return

    if data == "skip":
        await _record_answer(update, context, T.SKIPPED_LABEL[lang], via_callback=True)
        return

    if data == "finish":
        await _finalize(update, context, ai=False)
        return

    if data == "ai_analysis":
        # პირველი დაჭერა: აქტიური session-ია (კითხვები ახლახან დასრულდა) —
        # ჩვეულებრივი დასრულება/ანალიზი. ხელახალი დაჭერა (session უკვე
        # "last_session"-ზეა გადატანილი პირველი დასრულებისას): იმავე
        # პასუხებზე ხელახლა ვითხოვთ AI-ს ანალიზს, session-ს ხელახლა არ
        # ვაფინალებთ და სტატისტიკის თვლას არ ვიმეორებთ.
        if context.user_data.get("session"):
            await _finalize(update, context, ai=True)
        else:
            await _reanalyze(update, context)
        return

    if data == "save":
        session = context.user_data.get("last_session")
        if session:
            transcript = render_transcript_plain(lang, session["answers"])
            body = f"{T.SAVED_HEADER[lang]}\n\n{transcript}"
            if session.get("ai_text"):
                body += f"\n\n🤖 {session['ai_text']}"
            await context.bot.send_message(chat_id=session["chat_id"], text=body)
            await query.answer(T.SAVED_CONFIRM[lang], show_alert=True)
        return

    if data == "close_now":
        session = context.user_data.get("last_session")
        if session:
            chat_id = session["chat_id"]
            msg_ids = [session["bot_msg_id"]] + session["user_msg_ids"]
            # ვაუქმებთ დაგეგმილ (15-წუთიან) ავტომატურ წაშლას, რადგან ახლავე,
            # ხელით ვასრულებთ იმავე მოქმედებას.
            job_name = f"delete_{chat_id}_{msg_ids[0]}"
            for j in context.job_queue.get_jobs_by_name(job_name):
                j.schedule_removal()
            for mid in msg_ids:
                try:
                    await context.bot.delete_message(chat_id=chat_id, message_id=mid)
                except TelegramError:
                    pass
            await context.bot.send_message(
                chat_id=chat_id,
                text=welcome_text(lang),
                reply_markup=welcome_keyboard(lang),
                parse_mode=ParseMode.MARKDOWN,
            )
            context.user_data.pop("last_session", None)
        return

    if data == "toggle_reminder":
        is_on = context.user_data.get("reminder_on", False)
        chat_id = query.message.chat_id
        job_name = f"reminder_{chat_id}"
        existing = context.job_queue.get_jobs_by_name(job_name)
        for j in existing:
            j.schedule_removal()
        if is_on:
            context.user_data["reminder_on"] = False
            await query.message.edit_text(T.REMINDER_OFF_MSG[lang])
        else:
            context.user_data["reminder_on"] = True
            context.job_queue.run_daily(
                reminder_job,
                time=dtime(hour=REMINDER_HOUR, minute=REMINDER_MINUTE),
                data={"chat_id": chat_id, "lang": lang},
                name=job_name,
            )
            await query.message.edit_text(T.REMINDER_ON_MSG[lang])
        return


# ---------- ტექსტური პასუხების დამუშავება ----------

async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_answer"):
        return  # ბოტს არაფერი სჭირდება ამ მომენტში
    await _record_answer(update, context, update.message.text, via_callback=False)


async def _record_answer(update: Update, context: ContextTypes.DEFAULT_TYPE, answer_text: str, via_callback: bool):
    session = context.user_data.get("session")
    if not session:
        return
    lang = get_lang(context) or "ka"
    qidx = session["current_q"]
    question = session["questions"][qidx]
    session["answers"].append((question, answer_text))

    if not via_callback:
        session["user_msg_ids"].append(update.message.message_id)
        try:
            await update.message.delete()  # უფრო სუფთა ვიზუალისთვის: პასუხი გადადის საერთო ტექსტში
        except TelegramError:
            pass

    session["current_q"] += 1
    chat_id = session["chat_id"]
    bot_msg_id = session["bot_msg_id"]

    class _MsgProxy:
        """მცირე დამხმარე, რომ ერთნაირად გამოვიყენოთ edit_text ორივე შემთხვევაში."""
        async def edit_text(self, text, reply_markup=None, parse_mode=None):
            await context.bot.edit_message_text(
                chat_id=chat_id, message_id=bot_msg_id, text=text,
                reply_markup=reply_markup, parse_mode=parse_mode,
            )

    proxy = _MsgProxy()

    if session["current_q"] < len(session["questions"]):
        await send_question_view(proxy, lang, session)
    else:
        context.user_data["awaiting_answer"] = False
        await send_final_choice_view(proxy, lang, session)


# ---------- დასრულება / AI ანალიზი ----------

async def _finalize(update: Update, context: ContextTypes.DEFAULT_TYPE, ai: bool):
    query = update.callback_query
    session = context.user_data.get("session")
    if not session:
        return
    lang = get_lang(context) or "ka"
    user_id = update.effective_user.id
    stats = context.bot_data.setdefault("stats", {})
    stats[user_id] = stats.get(user_id, 0) + 1

    transcript = render_transcript_plain(lang, session["answers"])

    if ai:
        await query.message.edit_text(f"{transcript}\n\n{T.ANALYZING[lang]}")
        prompt = T.build_ai_prompt(lang, session["answers"])
        ai_text = await get_ai_analysis(prompt)
        if ai_text is None:
            await query.message.edit_text(
                f"{transcript}\n\n{T.AI_UNAVAILABLE[lang]}",
                reply_markup=finish_keyboard(lang),
            )
            return
        session["ai_text"] = ai_text
        final_text = f"{transcript}\n\n🤖 {ai_text}{T.WILL_DELETE_SOON[lang]}"
        # წარმატებული ანალიზის შემდეგაც "🤖 AI-ს ანალიზი" ღილაკი რჩება —
        # რომ საჭიროების შემთხვევაში ხელახლა გაუშვათ იმავე პასუხებზე.
        keyboard = result_keyboard(lang)
    else:
        final_text = f"{transcript}\n\n{T.FINISHED_PLAIN[lang]}{T.WILL_DELETE_SOON[lang]}"
        keyboard = save_keyboard(lang)

    await query.message.edit_text(final_text, reply_markup=keyboard)

    context.user_data["last_session"] = session
    all_msg_ids = [session["bot_msg_id"]] + session["user_msg_ids"]
    schedule_delete(context, session["chat_id"], all_msg_ids, lang)

    context.user_data.pop("session", None)
    context.user_data["awaiting_answer"] = False


async def _reanalyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """"🤖 AI-ს ანალიზი" ღილაკზე ხელახალი დაჭერა უკვე დასრულებულ
    სესიაზე — ხელახლა ვითხოვთ AI-ს პასუხს იმავე კითხვა-პასუხებზე
    (stats-ის თვლას აქ არ ვიმეორებთ, რადგან ეს იგივე სესიის გაგრძელებაა,
    არა ახალი დღიური ანალიზი)."""
    query = update.callback_query
    session = context.user_data.get("last_session")
    if not session:
        return
    lang = get_lang(context) or "ka"
    transcript = render_transcript_plain(lang, session["answers"])
    chat_id = session["chat_id"]
    msg_ids = [session["bot_msg_id"]] + session["user_msg_ids"]

    await query.message.edit_text(f"{transcript}\n\n{T.ANALYZING[lang]}")
    prompt = T.build_ai_prompt(lang, session["answers"])
    ai_text = await get_ai_analysis(prompt)

    if ai_text is None:
        await query.message.edit_text(
            f"{transcript}\n\n{T.AI_UNAVAILABLE[lang]}",
            reply_markup=result_keyboard(lang),
        )
        return

    session["ai_text"] = ai_text
    final_text = f"{transcript}\n\n🤖 {ai_text}{T.WILL_DELETE_SOON[lang]}"
    await query.message.edit_text(final_text, reply_markup=result_keyboard(lang))

    # მომხმარებელი ისევ აქტიურად მუშაობს გვერდზე — ვახანგრძლივებთ
    # ავტომატური წაშლის 15-წუთიან ვადას თავიდან.
    reschedule_delete(context, chat_id, msg_ids, lang)


# ---------- გაშვება ----------

def build_application() -> Application:
    if not TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN გარემოს ცვლადი არ არის დაყენებული")

    persistence = PicklePersistence(
        filepath=PERSISTENCE_PATH,
        store_data=PersistenceInput(bot_data=True, user_data=True, chat_data=False, callback_data=False),
    )
    app = ApplicationBuilder().token(TOKEN).persistence(persistence).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("lang", cmd_lang))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("reminder", cmd_reminder))
    app.add_handler(CallbackQueryHandler(on_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    return app


def main():
    app = build_application()
    threading.Thread(target=_start_health_server, daemon=True).start()
    logger.info("ბოტი გაეშვა polling რეჟიმში...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
