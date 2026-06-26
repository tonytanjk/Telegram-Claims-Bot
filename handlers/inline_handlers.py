from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ContextTypes
from services.google_services import google_services
from utils.auth import is_allowed
from utils.helpers import get_user_display_name, format_expense_row
import uuid

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query.strip()
    user = update.inline_query.from_user
    username = user.username or ""
    if not is_allowed(username):
        return
    results = []
    user_rows = google_services.find_expenses_by_user(username)
    for i, row in enumerate(user_rows):
        # Simple search: match if query in description/type/date/amount
        if query.lower() in " ".join(row).lower():
            results.append(
                InlineQueryResultArticle(
                    id=str(uuid.uuid4()),
                    title=f"{row[1]} | {row[2]} | ${row[4]}",
                    input_message_content=InputTextMessageContent(format_expense_row(row)),
                    description=row[3],
                )
            )
        if len(results) >= 20:
            break
    await update.inline_query.answer(results, cache_time=1)
