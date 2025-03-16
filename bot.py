import discord
import os
from discord.ext import commands
import asyncio
from flask import Flask
import threading
import time  # Thêm thư viện time để chống spam

# Lấy token từ biến môi trường
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Cấu hình quyền hạn (intents)
intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True  # Cần để bot vào voice
intents.message_content = True  # Cần để bot đọc lệnh

# Tạo bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Biến lưu thời gian cảnh báo gần nhất của !leave
last_warning_time = 0  

@bot.event
async def on_ready():
    """Khi bot khởi động thành công"""
    print(f"✅ Bot đã sẵn sàng! Đăng nhập với tên: {bot.user}")

@bot.command()
async def join(ctx, channel_id: int):
    """Lệnh tham gia kênh thoại bằng Channel ID"""
    try:
        channel = bot.get_channel(channel_id)  # Lấy kênh từ ID

        if not channel:
            await ctx.send("⚠️ Không tìm thấy kênh thoại. Hãy kiểm tra lại ID.")
            return

        if isinstance(channel, discord.VoiceChannel):
            if ctx.voice_client:  # Nếu bot đang ở trong một kênh voice khác
                await ctx.voice_client.disconnect()  # Rời khỏi kênh cũ trước
            voice_client = await channel.connect()  # Kết nối đến kênh thoại
            
            # 🔊 Phát âm thanh trống mà không cần file silence.mp3
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
    global last_warning_time  # Dùng biến toàn cục để kiểm soát cảnh báo

    voice_client = ctx.voice_client  # Lấy voice client hiện tại của bot

    if voice_client and voice_client.is_connected():  # Kiểm tra bot có đang ở voice không
        await voice_client.disconnect()
        await ctx.send("✅ Bot đã rời khỏi kênh thoại.")
    else:
        current_time = time.time()
        if current_time - last_warning_time > 5:  # Chỉ gửi cảnh báo mỗi 5 giây
            await ctx.send("⚠️ Bot không ở trong kênh voice nào.")
            last_warning_time = current_time  # Cập nhật thời gian cảnh báo gần nhất

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
