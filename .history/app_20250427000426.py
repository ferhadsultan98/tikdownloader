import os
import re
import logging
import tempfile
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
)
import yt_dlp
from dotenv import load_dotenv

load_dotenv()

# Bot token
TOKEN = os.environ.get("TOKEN")

# Log settings
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# TikTok URL regex
TIKTOK_URL_PATTERN = re.compile(r'https?://(www\.)?(vm\.)?(tiktok\.com|vt\.tiktok\.com)/.*')

class TiktokDownloaderBot:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            "Salam! TikTok videolarını yükləmək üçün mənə bir TikTok linki göndərin."
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            "TikTok videosunu yükləmək üçün sadəcə mənə bir TikTok linki göndərin."
        )

    async def download_tiktok(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        message_text = update.message.text
        
        if not TIKTOK_URL_PATTERN.match(message_text):
            await update.message.reply_text("Bu bir TikTok linki deyil. Zəhmət olmasa düzgün bir TikTok linki göndərin.")
            return
        
        status_message = await update.message.reply_text("Video yüklənir, zəhmət olmasa gözləyin...")
        
        try:
            video_path = self._download_video(message_text)
            await self._send_video(update, video_path)
            self._cleanup_temp_files([video_path])
            await status_message.delete()
            
        except Exception as e:
            logger.error(f"Video yüklənərkən xəta baş verdi: {e}")
            await status_message.edit_text(f"Video yüklənərkən xəta baş verdi: {str(e)}")
    
    def _download_video(self, url):
        output_path = os.path.join(self.temp_dir, "video.mp4")
        
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'outtmpl': output_path,
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        return output_path
    
    async def _send_video(self, update: Update, video_path):
        with open(video_path, 'rb') as video_file:
            await update.message.reply_video(
                video=video_file,
                caption="TikTok videosu filigransız olaraq yükləndi."
            )
    
    def _cleanup_temp_files(self, file_paths):
        for file_path in file_paths:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    logger.error(f"Fayl silinərkən xəta: {e}")

async def main():
    bot = TiktokDownloaderBot()
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CommandHandler("help", bot.help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.download_tiktok))

    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
