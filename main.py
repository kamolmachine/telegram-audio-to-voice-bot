#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import telebot
import tempfile
import subprocess

TOKEN = ''
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start_command_handler(message):
    text = "Just send an audio message and you'll get it as a proper voice message with waveform"
    bot.send_message(message.chat.id, text)

@bot.message_handler(content_types=['audio', 'voice'])
def audio_handler(message):
    file_info = bot.get_file(message.audio.file_id if message.content_type == 'audio' else message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    # temp file for conversion
    with tempfile.NamedTemporaryFile(suffix=".input", delete=False) as input_file, \
         tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as output_file:

        input_file.write(downloaded_file)
        input_file.flush()

        # convert to .ogg Opus for Telegram voice note
        subprocess.run([
            'ffmpeg', '-y', '-i', input_file.name,
            '-c:a', 'libopus', '-b:a', '64k', '-vbr', 'on',
            '-vn', output_file.name
        ], check=True)

        # Send voice note
        with open(output_file.name, 'rb') as f:
            bot.send_voice(message.chat.id, f, caption=message.caption)

bot.infinity_polling()
