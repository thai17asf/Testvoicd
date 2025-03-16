import discord
import os
from discord.ext import commands
import asyncio
from flask import Flask
import threading

# Lấy token từ biến môi trường
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Cấu hình quyền hạn (intents)
intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True  # Cần để bot vào voice
intents.message_content = True  # Cần để bot đọc lệnh

# Tạo bot
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    """Khi bot khởi động thành công"""
    print(f"✅ Bot đã sẵn sàng! Đăng nhập với tên: {bot.user}")

@bot.command()
async def join(ctx, channel_id: int):
    """Lệnh tham gia kênh thoại bằng Channel ID và phát âm thanh trống (không cần file)"""
    try:
        channel = bot.get_channel(channel_id)  # Lấy kênh từ ID

        if not channel:
            await ctx.send("⚠️ Không tìm thấy kênh thoại. Hãy kiểm tra lại ID.")
            return

        if isinstance(channel, discord.VoiceChannel):
            if ctx.voice_client:  # Nếu bot đang ở trong một kênh voice khác
                await ctx.voice_client.disconnect()  # Rời khỏi kênh cũ trước
            voice_client = await channel.connect()  # Kết nối đến kênh thoại
            
            # 🔊 Phát âm thanh trống bằng FFmpeg mà không cần file silence.mp3
            ffmpeg_options = {
                'before_options': '-f lavfi -i anullsrc',
                'options': '-vn'
            }
            source = discord.FFmpegPCMAudio("dummy", **ffmpeg_options)
            voice_client.play(source)

            await ctx.send(f"✅ Đã tham gia kênh thoại: {channel.name}")
        else:
            await ctx.send("⚠️ ID không hợp lệ hoặc không phải kênh voice.")

    except Exception as e:
        await ctx.send(f"❌ Lỗi: `{e}`")
        print(f"[ERROR] {e}")

@bot.command()
async def leave(ctx):
    """Lệnh rời khỏi kênh voice"""
    if ctx.voice_client:  # Kiểm tra nếu bot đang ở trong kênh voice
        await ctx.voice_client.disconnect()
        await ctx.send("✅ Bot đã rời khỏi kênh thoại.")
    else:
        await ctx.send("⚠️ Bot không ở trong kênh voice nào.")

# 🌐 Flask giữ bot online
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host="0.0.0.0", port=8080)

# Chạy Flask trên một luồng riêng
t = threading.Thread(target=run)
t.start()

# 🔄 Giữ bot online bằng vòng lặp keep_alive
async def keep_alive():
    while True:
        print("✅ Bot vẫn hoạt động...")
        await asyncio.sleep(600)  # 10 phút

bot.loop.create_task(keep_alive())  # Chạy vòng lặp

# 🟢 Chạy bot
bot.run(TOKEN)
