import os
import re 
import sys
import typing
import asyncio 
import logging 
from database import db 
from config import Config, temp
from pyrogram import Client, filters
from pyrogram.raw.all import layer
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message 
from pyrogram.errors.exceptions.bad_request_400 import AccessTokenExpired, AccessTokenInvalid
from pyrogram.errors import FloodWait, PhoneNumberInvalid, PhoneCodeInvalid, PhoneCodeExpired, SessionPasswordNeeded, PasswordHashInvalid
from config import Config
from translation import Translation

from typing import Union, Optional, AsyncGenerator

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BTN_URL_REGEX = re.compile(r"(\[([^\[]+?)]\[buttonurl:/{0,2}(.+?)(:same)?])")
BOT_TOKEN_TEXT = "<b>1) create a bot using @BotFather\n2) Then you will get a message with bot token\n3) Forward that message to me</b>"
SESSION_STRING_SIZE = 351

async def start_clone_bot(FwdBot, data=None):
   await FwdBot.start()
   # futures add by @Mr_Jisshu
   async def iter_messages(
      self, 
      chat_id: Union[int, str], 
      limit: int, 
      offset: int = 0,
      search: str = None,
      filter: "types.TypeMessagesFilter" = None,
      ) -> Optional[AsyncGenerator["types.Message", None]]:
        """Iterate through a chat sequentially.
        This convenience method does the same as repeatedly calling :meth:`~pyrogram.Client.get_messages` in a loop, thus saving
        you from the hassle of setting up boilerplate code. It is useful for getting the whole chat messages with a
        single call.
        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).
                
            limit (``int``):
                Identifier of the last message to be returned.
                
            offset (``int``, *optional*):
                Identifier of the first message to be returned.
                Defaults to 0.
        Returns:
            ``Generator``: A generator yielding :obj:`~pyrogram.types.Message` objects.
        Example:
            .. code-block:: python
                for message in app.iter_messages("pyrogram", 1, 15000):
                    print(message.text)
        """
        current = offset
        while True:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(chat_id, list(range(current, current+new_diff+1)))
            for message in messages:
                yield message
                current += 1
   #
   FwdBot.iter_messages = iter_messages
   return FwdBot

class CLIENT: 
  def __init__(self):
     self.api_id = Config.API_ID
     self.api_hash = Config.API_HASH
    
  def client(self, data, user=None):
     if user == None and data.get('is_bot') == False:
        return Client("USERBOT", self.api_id, self.api_hash, session_string=data.get('session'))
     elif user == True:
        return Client("USERBOT", self.api_id, self.api_hash, session_string=data)
     elif user != False:
        data = data.get('token')
     return Client("BOT", self.api_id, self.api_hash, bot_token=data, in_memory=True)
  
  async def add_bot(self, bot, message):
    user_id = int(message.from_user.id)
    msg = await bot.ask(chat_id=user_id, text="Please forward the bot token message from @BotFather.")

    # Cancel process if user sends /cancel
    if msg.text == '/cancel':
        return await msg.reply('<b>Process cancelled!</b>')
    
    # Ensure the message is a forwarded one
    if not msg.forward_date:
        return await msg.reply_text("<b>This is not a forward message</b>")
    
    # Ensure the message was forwarded from BotFather
    if str(msg.forward_from.id) != "93372553":
        return await msg.reply_text("<b>This message was not forwarded from BotFather</b>")
    
    # Extract bot token from the forwarded message
    bot_token = re.findall(r'\d{8,10}:[0-9A-Za-z_-]{35}', msg.text, re.IGNORECASE)
    bot_token = bot_token[0] if bot_token else None
    if not bot_token:
        return await msg.reply_text("<b>There is no bot token in that message</b>")
    
    # Attempt to start the clone bot
    try:
        _client = await start_clone_bot(self.client(bot_token, False), True)
    except Exception as e:
        return await msg.reply_text(f"<b>BOT ERROR:</b> `{e}`")
    
    # Retrieve bot details and save them to the database
    _bot = _client.me
    details = {
        'id': _bot.id,
        'is_bot': True,
        'user_id': user_id,
        'name': _bot.first_name,
        'token': bot_token,
        'username': _bot.username 
    }
    await db.add_bot(details)

    # Log Channel future add by @Mr_Jisshu
    log_channel = Config.LOG_CHANNEL  
    bot_username = _bot.username
    user_username = message.from_user.username
    log_message = f"#addbot\n\nBot Username: @{bot_username}\nAdded by: @{user_username}"
    await bot.send_message(chat_id=log_channel, text=log_message)

    return True
     
  # login future add by @Mr_Jisshu
  async def add_login(self, bot, message):
    user_id = int(message.from_user.id)
    api_id = Config.API_ID
    api_hash = Config.API_HASH

    # Send the disclaimer message
    disclaimer_text = "<b><blockquote>**<u>⚠️ Warning ⚠️</u>**:\n\n If you already have a session string, please use the add user bot. Otherwise, you can use login.</blockquote>"
    await bot.send_message(user_id, text=disclaimer_text)

    # Ask for the phone number
    t = "➫ ᴘʟᴇᴀsᴇ sᴇɴᴅ ʏᴏᴜʀ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ ᴡɪᴛʜ ᴄᴏᴜɴᴛʀʏ ᴄᴏᴅᴇ ғᴏʀ ᴡʜɪᴄʜ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ sᴇssɪᴏɴ \n➫ ᴇxᴀᴍᴘʟᴇ: +910000000000\n/cancel - ᴛᴏ ᴄᴀɴᴄᴇʟ ᴛʜɪs ᴘʀᴏᴄᴇss"
    phone_number_msg = await bot.ask(user_id, t, filters=filters.text)

    if phone_number_msg.text and phone_number_msg.text.startswith('/'):
        await bot.send_message(user_id, "<b>Process cancelled!</b>")
        return

    phone_number = phone_number_msg.text

    # Inform the user about sending the OTP
    await bot.send_message(user_id, "ᴛʀʏɪɴɢ ᴛᴏ sᴇɴᴅ ᴏᴛᴩ ᴀᴛ ᴛʜᴇ ɢɪᴠᴇɴ ɴᴜᴍʙᴇʀ...")

    client = Client(name="user", api_id=api_id, api_hash=api_hash, in_memory=True)
    await client.connect()

    try:
        code = await client.send_code(phone_number)
    except PhoneNumberInvalid:
        await bot.send_message(user_id, "The phone number you've sent doesn't belong to any Telegram account.\n\n➫ Please start generating your session again.")
        return

    try:
        phone_code_msg = await bot.ask(user_id, "Please send the OTP that you've received from Telegram on your account.\n➫ If OTP is 12345, please send it as 1 2 3 4 5.", filters=filters.text, timeout=600)
        if phone_code_msg.text and phone_code_msg.text.startswith('/'):
            await bot.send_message(user_id, "<b>Process cancelled!</b>")
            return
    except TimeoutError:
        await bot.send_message(user_id, "Time limit reached of 10 minutes.\n\nPlease start generating your session again.")
        return

    phone_code = phone_code_msg.text.replace(" ", "")

    try:
        await client.sign_in(phone_number, code.phone_code_hash, phone_code)
    except PhoneCodeInvalid:
        await bot.send_message(user_id, "The OTP you've sent is wrong.\n\nPlease start generating your session again.")
        return
    except PhoneCodeExpired:
        await bot.send_message(user_id, "The OTP you've sent is expired.\n\nPlease start generating your session again.")
        return
    except SessionPasswordNeeded:
        try:
            two_step_msg = await bot.ask(user_id, "Please enter your two-step verification password to continue.", filters=filters.text, timeout=300)
            if two_step_msg.text and two_step_msg.text.startswith('/'):
                await bot.send_message(user_id, "<b>Process cancelled!</b>")
                return
        except TimeoutError:
            await bot.send_message(user_id, "Time limit reached of 5 minutes.\n\nPlease start generating your session again.")
            return

        try:
            password = two_step_msg.text
            await client.check_password(password=password)
        except PasswordHashInvalid:
            await bot.send_message(user_id, "The password you've sent is wrong.\n\nPlease start generating your session again.")
            return

    # Export the session string
    string_session = await client.export_session_string()
    if len(string_session) < SESSION_STRING_SIZE:
        await bot.send_message(user_id, "<b>Invalid session string.</b>")
        return

    text = f"➫ This is your pyrogram v2 string session:\n\n<code>{string_session}</code>\n\nNote: Don't share it with anyone."
    await bot.send_message(user_id, text)

    user = await client.get_me()
    details = {
        'id': user.id,
        'is_bot': False,
        'user_id': user_id,
        'name': user.first_name,
        'session': string_session,
        'username': user.username
    }

    # Add bot details to the database
    await db.add_bot(details)
    await client.disconnect()
    return details    
    
  async def add_session(self, bot, message):
     user_id = int(message.from_user.id)
     text = "<b>⚠️ DISCLAIMER ⚠️</b>\n\n<code>you can use your session for forward message from private chat to another chat.\nPlease add your pyrogram session with your own risk. Their is a chance to ban your account. My developer is not responsible if your account may get banned.</code>"
     await bot.send_message(user_id, text=text)
     msg = await bot.ask(chat_id=user_id, text="<b>send your pyrogram session.\n\n[If you don't have string session you can use login user bot]\n\n/cancel - cancel the process</b>")
     if msg.text=='/cancel':
        return await msg.reply('<b>process cancelled !</b>')
     elif len(msg.text) < SESSION_STRING_SIZE:
        return await msg.reply('<b>invalid session sring</b>')
     try:
       client = await start_clone_bot(self.client(msg.text, True), True)
     except Exception as e:
       await msg.reply_text(f"<b>USER BOT ERROR:</b> `{e}`")
     user = client.me
     details = {
       'id': user.id,
       'is_bot': False,
       'user_id': user_id,
       'name': user.first_name,
       'session': msg.text,
       'username': user.username
     }
     await db.add_bot(details)
     return True
    
@Client.on_message(filters.private & filters.command('reset'))
async def forward_tag(bot, m):
   default = await db.get_configs("01")
   temp.CONFIGS[m.from_user.id] = default
   await db.update_configs(m.from_user.id, default)
   await m.reply("successfully settings reseted ✔️")

@Client.on_message(filters.command('resetall') & filters.user(Config.BOT_OWNER_ID))
async def resetall(bot, message):
  users = await db.get_all_users()
  sts = await message.reply("**processing**")
  TEXT = "total: {}\nsuccess: {}\nfailed: {}\nexcept: {}"
  total = success = failed = already = 0
  ERRORS = []
  async for user in users:
      user_id = user['id']
      default = await get_configs(user_id)
      default['db_uri'] = None
      total += 1
      if total %10 == 0:
         await sts.edit(TEXT.format(total, success, failed, already))
      try: 
         await db.update_configs(user_id, default)
         success += 1
      except Exception as e:
         ERRORS.append(e)
         failed += 1
  if ERRORS:
     await message.reply(ERRORS[:100])
  await sts.edit("completed\n" + TEXT.format(total, success, failed, already))
  
async def get_configs(user_id):
  #configs = temp.CONFIGS.get(user_id)
  #if not configs:
  configs = await db.get_configs(user_id)
  #temp.CONFIGS[user_id] = configs 
  return configs
                          
async def update_configs(user_id, key, value):
  current = await db.get_configs(user_id)
  if key in ['caption', 'duplicate', 'db_uri', 'forward_tag', 'protect', 'file_size', 'size_limit', 'extension', 'keywords', 'button']:
     current[key] = value
  else: 
     current['filters'][key] = value
 # temp.CONFIGS[user_id] = value
  await db.update_configs(user_id, current)
    
def parse_buttons(text, markup=True):
    buttons = []
    for match in BTN_URL_REGEX.finditer(text):
        n_escapes = 0
        to_check = match.start(1) - 1
        while to_check > 0 and text[to_check] == "\\":
            n_escapes += 1
            to_check -= 1

        if n_escapes % 2 == 0:
            if bool(match.group(4)) and buttons:
                buttons[-1].append(InlineKeyboardButton(
                    text=match.group(2),
                    url=match.group(3).replace(" ", "")))
            else:
                buttons.append([InlineKeyboardButton(
                    text=match.group(2),
                    url=match.group(3).replace(" ", ""))])
    if markup and buttons:
       buttons = InlineKeyboardMarkup(buttons)
    return buttons if buttons else None
