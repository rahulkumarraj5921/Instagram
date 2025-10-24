from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
import yt_dlp
import os

BOT_TOKEN = '8391056693:AAFQ3rm3MPaTc4t8-1fltzrO_akmnSkPs2c'

# Dictionary to track which users have confirmed follow
user_follow_status = {}

INSTAGRAM_PROFILE_URL = "https://www.instagram.com/rahul_kumar_raj_592"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📲 Follow Instagram Profile", url=INSTAGRAM_PROFILE_URL)],
        [InlineKeyboardButton("✅ I have followed", callback_data="followed")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Welcome! Please follow our Instagram profile before using this bot.\n\n"
        f"👉 {INSTAGRAM_PROFILE_URL}\n\n"
        "Once done, press the button below.",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "followed":
        user_id = query.from_user.id
        user_follow_status[user_id] = True
        await query.edit_message_text("✅ Thanks! Now send me an Instagram video link to download it.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if not user_follow_status.get(user_id, False):
        await update.message.reply_text("⚠️ Please follow the Instagram profile first using /start.")
        return

    url = update.message.text.strip()
    if 'instagram.com' not in url:
        await update.message.reply_text("❌ Please send a valid Instagram video URL.")
        return

    await update.message.reply_text("⬇️ Downloading video, please wait...")

    video_path = download_instagram_video(url)

    if video_path and os.path.exists(video_path):
        with open(video_path, 'rb') as video_file:
            await update.message.reply_video(video_file)
        os.remove(video_path)
    else:
        await update.message.reply_text("⚠️ Failed to download video. Please check the URL or try again later.")

def download_instagram_video(url):
    try:
        ydl_opts = {
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'format': 'mp4',
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_path = ydl.prepare_filename(info_dict)
        return video_path
    except Exception as e:
        print("Download error:", e)
        return None

if __name__ == '__main__':
    if not os.path.exists("downloads"):
        os.mkdir("downloads")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()

