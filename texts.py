# -*- coding: utf-8 -*-
"""
ყველა ტექსტი სამივე ენაზე (ka/ru/en).
ყველა ტექსტი და კითხვა ერთ ადგილას ინახება, რომ ადვილად შესწორდეს.
"""

LANGS = ["ka", "ru", "en"]

LANG_NAMES = {
    "ka": "🇬🇪 ქართული",
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English",
}

PRAYER = {
    "ka": "ღმერთო, მაჩვენე რა გავაკეთე დღეს სწორად, სად დავუშვი შეცდომა, "
          "მაჩვენე როგორ ვიცხოვრო და ვემსახურო შენს ნებას ხვალ.",
    "ru": "Господи, покажи мне, что я сделал правильно сегодня, в чём я ошибся, "
          "покажи мне, как жить и служить Твоей воле завтра.",
    "en": "God, show me what I did right today, where I made a mistake, "
          "show me how to live and serve Your will tomorrow.",
}

DELETE_NOTICE = {
    "ka": "ℹ️ ინფორმაცია: ანალიზის დასრულებიდან 15 წუთში ეს გვერდი ავტომატურად წაიშლება "
          "და ბოტი დაუბრუნდება საწყის მდგომარეობას. თუ გინდა შენახვა, გექნება ცალკე ღილაკი.",
    "ru": "ℹ️ Информация: через 15 минут после завершения анализа это сообщение будет "
          "автоматически удалено, и бот вернётся в исходное состояние. Если хочешь сохранить "
          "результат — для этого будет отдельная кнопка.",
    "en": "ℹ️ Note: 15 minutes after you finish, this analysis will be automatically deleted "
          "and the bot will return to its starting state. There's a separate button if you want "
          "to save it.",
}

BTN_START = {"ka": "🔍 დაწყება", "ru": "🔍 Начать", "en": "🔍 Start"}
BTN_SKIP = {"ka": "⏭ გამოტოვება", "ru": "⏭ Пропустить", "en": "⏭ Skip"}
BTN_FINISH = {"ka": "✅ დასრულება", "ru": "✅ Завершить", "en": "✅ Finish"}
BTN_AI = {"ka": "🤖 AI-ს ანალიზი", "ru": "🤖 Анализ от AI", "en": "🤖 AI Analysis"}
BTN_SAVE = {"ka": "💾 შენახვა ჩემთვის", "ru": "💾 Сохранить для себя", "en": "💾 Save for myself"}
BTN_LANG_CHANGE = {"ka": "🌐 ენის შეცვლა", "ru": "🌐 Сменить язык", "en": "🌐 Change language"}
BTN_REMINDER_ON = {"ka": "🔔 შეხსენების ჩართვა", "ru": "🔔 Включить напоминание", "en": "🔔 Turn reminder on"}
BTN_REMINDER_OFF = {"ka": "🔕 შეხსენების გამორთვა", "ru": "🔕 Выключить напоминание", "en": "🔕 Turn reminder off"}

CHOOSE_LANG = {
    "ka": "გამარჯობა! აირჩიე ენა 👇",
    "ru": "Привет! Выбери язык 👇",
    "en": "Hello! Choose your language 👇",
}

WELCOME_INTRO = {
    "ka": "ეს არის შენი პირადი, ყოველდღიური თვითანალიზის სივრცე.",
    "ru": "Это твоё личное пространство для ежедневного самоанализа.",
    "en": "This is your personal space for a daily self-analysis.",
}

QUESTIONS = {
    "ka": [
        "ვიყავი თუ არა გულწრფელი ჩემს მოქმედებებში და მოტივებში?",
        "ვილოცე თუ არა იმისთვის რომ გამეგო ღმერთის ნება ჩემთვის და ვითხოვე თუ არა ძალა ამის ასასრულებლად?",
        "ხომ არ დავაზიანე დღეს სხვა ადამიანი ან საკუთარი თავი, პირდაპირ ან ირიბად?",
        "ხომ არ მმართებს დღეს სხვა ადამიანს ან საკუთარ თავს ავუნაზღაურო ზიანი ჩემი მოქმედებების გამო?",
        "რა შეცდომა დავუშვი დღეს და რა ჯობია გავითვალისწინო მომავალში?",
        "ვიყავი თუ არა დღეს კეთილი საკუთარი თავის მიმართ?",
        "გავუკეთე თუ არა დღეს სხვა ადამიანს რაიმე კარგი, მოლოდინის გარეშე?",
        "დავადასტურე თუ არა დღეს ჩემი ნდობა მოსიყვარულე და მზრუნველი ღმერთის მიმართ?",
        "რისი მადლიერი ვარ დღეს?",
    ],
    "ru": [
        "Был ли я искренним в своих действиях и мотивах сегодня?",
        "Молился ли я о том, чтобы понять волю Божью для себя, и просил ли сил для её исполнения?",
        "Не навредил ли я сегодня другому человеку или себе самому, прямо или косвенно?",
        "Не должен ли я сегодня возместить ущерб другому человеку или себе за свои поступки?",
        "Какую ошибку я совершил сегодня и что мне стоит учесть в будущем?",
        "Был ли я добр к себе сегодня?",
        "Сделал ли я сегодня что-то хорошее для другого человека, не ожидая ничего взамен?",
        "Подтвердил ли я сегодня свою веру в любящего и заботливого Бога?",
        "За что я благодарен сегодня?",
    ],
    "en": [
        "Was I honest in my actions and motives today?",
        "Did I pray to understand God's will for me, and ask for the strength to carry it out?",
        "Did I harm another person or myself today, directly or indirectly?",
        "Do I owe amends to someone else or myself today for something I did?",
        "What mistake did I make today, and what should I keep in mind going forward?",
        "Was I kind to myself today?",
        "Did I do something good for someone today, without expecting anything in return?",
        "Did I affirm my trust in a loving, caring God today?",
        "What am I grateful for today?",
    ],
}

def progress_label(lang, idx_1based, total=9):
    if lang == "ka":
        return f"კითხვა {idx_1based}/{total}"
    if lang == "ru":
        return f"Вопрос {idx_1based}/{total}"
    return f"Question {idx_1based}/{total}"

SKIPPED_LABEL = {"ka": "(გამოტოვებულია)", "ru": "(пропущено)", "en": "(skipped)"}

ANALYZING = {
    "ka": "🤖 გაანალიზდება... ერთი წუთით მოითმინე.",
    "ru": "🤖 Анализирую... подожди немного.",
    "en": "🤖 Analyzing... one moment please.",
}

AI_UNAVAILABLE = {
    "ka": "⚠️ AI ანალიზის სერვისი ამჟამად მიუწვდომელია. სცადე მოგვიანებით, ან დააჭირე „დასრულებას“.",
    "ru": "⚠️ Сервис AI-анализа сейчас недоступен. Попробуй позже или нажми «Завершить».",
    "en": "⚠️ The AI analysis service is unavailable right now. Try again later, or press \"Finish\".",
}

FINISHED_PLAIN = {
    "ka": "✅ დღევანდელი თვითანალიზი დასრულებულია. კარგი საქმეა, რომ დროს უთმობ ამას.",
    "ru": "✅ Сегодняшний самоанализ завершён. Здорово, что ты уделяешь этому время.",
    "en": "✅ Today's self-analysis is complete. It's great that you take the time for this.",
}

SAVED_HEADER = {
    "ka": "📌 შენახული ჩანაწერი",
    "ru": "📌 Сохранённая запись",
    "en": "📌 Saved entry",
}

SAVED_CONFIRM = {
    "ka": "შენახულია ცალკე შეტყობინებაში ⬆️ (ეს არ წაიშლება).",
    "ru": "Сохранено в отдельном сообщении ⬆️ (оно не будет удалено).",
    "en": "Saved in a separate message above ⬆️ (it won't be deleted).",
}

WILL_DELETE_SOON = {
    "ka": "\n\n🕒 ეს გვერდი წაიშლება 15 წუთში.",
    "ru": "\n\n🕒 Это сообщение будет удалено через 15 минут.",
    "en": "\n\n🕒 This message will be deleted in 15 minutes.",
}

REMINDER_PROMPT = {
    "ka": "დღიური შეხსენება იგზავნება ყოველ საღამოს 21:00 საათზე (სერვერის დროით). გინდა ჩართო?",
    "ru": "Ежедневное напоминание приходит каждый вечер в 21:00 (по времени сервера). Включить?",
    "en": "The daily reminder is sent every evening at 21:00 (server time). Turn it on?",
}

REMINDER_ON_MSG = {
    "ka": "🔔 დღიური შეხსენება ჩართულია — ყოველ საღამოს 21:00-ზე შეგახსენებ.",
    "ru": "🔔 Ежедневное напоминание включено — буду напоминать каждый вечер в 21:00.",
    "en": "🔔 Daily reminder turned on — I'll remind you every evening at 21:00.",
}

REMINDER_OFF_MSG = {
    "ka": "🔕 დღიური შეხსენება გამორთულია.",
    "ru": "🔕 Ежедневное напоминание выключено.",
    "en": "🔕 Daily reminder turned off.",
}

REMINDER_PING = {
    "ka": "🕯 დროა დღევანდელი თვითანალიზისთვის. მზად ხარ? /start",
    "ru": "🕯 Время для сегодняшнего самоанализа. Готов? /start",
    "en": "🕯 Time for today's self-analysis. Ready? /start",
}

STATS_MSG = {
    "ka": "📊 შენ დაასრულე თვითანალიზი {count}-ჯერ. პასუხების შინაარსი არსად ინახება.",
    "ru": "📊 Ты завершил(а) самоанализ {count} раз(а). Содержание ответов нигде не сохраняется.",
    "en": "📊 You've completed the self-analysis {count} time(s). The content of your answers is never stored.",
}

HELP_MSG = {
    "ka": "/start — თვითანალიზის დაწყება\n/reminder — დღიური შეხსენების ჩართვა/გამორთვა\n"
          "/stats — რამდენჯერ გაიარე ანალიზი\n/lang — ენის შეცვლა",
    "ru": "/start — начать самоанализ\n/reminder — включить/выключить ежедневное напоминание\n"
          "/stats — сколько раз пройден анализ\n/lang — сменить язык",
    "en": "/start — start the self-analysis\n/reminder — turn the daily reminder on/off\n"
          "/stats — how many times you've done the analysis\n/lang — change language",
}

# AI-სთვის მიმართვის prompt (ინგლისურად ვწერთ, backend-ისთვის, მომხმარებელს არ უჩანს)
def build_ai_prompt(lang, qa_pairs):
    lang_instruction = {
        "ka": "Respond entirely in Georgian (ქართული).",
        "ru": "Respond entirely in Russian (русский).",
        "en": "Respond entirely in English.",
    }[lang]

    qa_text = "\n".join(
        f"{i+1}. {q}\n   Answer: {a}"
        for i, (q, a) in enumerate(qa_pairs)
    )

    return f"""You are giving warm, thoughtful, genuinely perceptive feedback on someone's
daily personal self-reflection (a nightly moral inventory in the style of a 12-step
recovery program's 10th step, covering honesty, harm done, amends, gratitude, and
self-kindness). Do NOT mention the 12-step program, "step 10", recovery programs, or
any framework by name anywhere in your reply — the person should just feel genuinely
seen and gently guided, not analyzed through a labeled lens.

Here are today's questions and their answers:

{qa_text}

Write a reflection (roughly 220-280 words) with two parts:

PART 1 — Reflection (most of the length):
- Engage with what they ACTUALLY wrote, not generic categories. Reference at least two
  of their specific answers directly enough that they'd recognize you actually read
  them — a specific situation, feeling, or phrase they used, not a paraphrase of the
  question itself.
- Notice real patterns or connections across their answers (e.g., a link between what
  they said about harm done and what they said about gratitude, or between honesty and
  self-kindness) — something they might not have noticed themselves.
- If any answers are self-critical or negative, reassure them this is completely
  normal and that change happens gradually — but do this briefly, as one note among
  several, not as the entire reflection. Avoid generic affirmations like "it's great
  that you're reflecting" — assume that's already understood.

PART 2 — One concrete direction for tomorrow (shorter, 2-4 sentences):
- Give ONE specific, small, doable practice or action tied directly to something
  specific they wrote today — not generic advice like "be kinder to yourself." Make it
  concrete enough that they could actually do it tomorrow (a specific moment to pause,
  a specific person to reach out to, a specific question to ask themselves, a specific
  two-minute practice) — grounded in their actual answers, not a stock suggestion.

Tone: warm, direct, perceptive — like someone who read closely and thought about it,
not a form letter. Does not lecture, moralize, or diagnose. Do not use clinical or
therapy-speak. Do not use markdown headers or bullet lists — write it as flowing prose,
with a natural paragraph break between the two parts.

{lang_instruction}
"""
