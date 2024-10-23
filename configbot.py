import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import random
import os

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

PLAYER_FILE = 'list_players.txt'
PLAYER_WEEK_FILE = 'list_players_week.txt'
PLAYER_SOTRAN_FILE = 'list_players_sotran.txt'
PLAYER_DIEM_FILE = 'list_players_diem.txt'

async def getlistall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not os.path.exists(PLAYER_FILE):
            await update.message.reply_text("Không có người chơi đăng ký!")
            return

        players = []
        with open(PLAYER_FILE, 'r') as file:
            for line in file:
                ingame_name, rank = line.strip().split(',')
                players.append((ingame_name, rank))

        players.sort(key=lambda x: (x[1]), reverse=True)
        stt = 0
        response = "Danh sách người chơi đã đăng ký:\n"
        for ingame_name, rank in players:
            stt = stt + 1
            response += f"{stt}. {rank} {ingame_name}\n"

        await update.message.reply_text(response)
    except Exception as e:
        logging.error(f"Lỗi trong quá trình getlist: {e}")
        await update.message.reply_text("Lỗi trong quá trình getlist.")

async def getlistofweek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not os.path.exists(PLAYER_WEEK_FILE):
            await update.message.reply_text("Không có người chơi đăng ký trong tuần này!")
            return

        players = []
        with open(PLAYER_WEEK_FILE, 'r') as file:
            for line in file:
                ingame_name, rank, sotran = line.strip().split(',')
                players.append((ingame_name, rank, sotran))

        players.sort(key=lambda x: x[2], reverse=True)
        stt = 0
        response = "Danh sách người chơi đăng ký trong tuần này:\n"
        for ingame_name, rank, sotran in players:
            stt = stt + 1
            response += f"{stt}. {rank} {ingame_name} số trận: {sotran}\n"

        await update.message.reply_text(response)
    except Exception as e:
        logging.error(f"Lỗi trong quá trình getlistofweek: {e}")
        await update.message.reply_text("Lỗi trong quá trình getlistofweek!")

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) != 2:
            await update.message.reply_text("Sai cú pháp: /register <ingamename> <rank>")
            return

        ingame_name = args[0]
        rank = args[1]

        if rank not in ['R1', 'R2', 'R3', 'R4', 'R5']:
            await update.message.reply_text("Sai cú pháp rank là một trong các giá trị: R1, R2, R3, R4, R5")
            return

        if os.path.exists(PLAYER_FILE):
            with open(PLAYER_FILE, 'r') as file:
                for line in file:
                    if line.startswith(ingame_name + ','):
                        await update.message.reply_text(f"Người chơi {ingame_name} đã được đăng ký!")
                        return

        with open(PLAYER_FILE, 'a+') as file:
            file.seek(0, os.SEEK_END)
            if file.tell() > 0:
                file.write(f"\n{ingame_name},{rank}")
            else:
                file.write(f"{ingame_name},{rank}")

        with open(PLAYER_SOTRAN_FILE, 'a+') as file:
            file.seek(0, os.SEEK_END)
            if file.tell() > 0:
                file.write(f"\n{ingame_name},0")
            else:
                file.write(f"{ingame_name},0")

        with open(PLAYER_DIEM_FILE, 'a+') as file:
            file.seek(0, os.SEEK_END)
            if file.tell() > 0:
                file.write(f"\n{ingame_name},0")
            else:
                file.write(f"{ingame_name},0")

        await update.message.reply_text(f"Chào mừng {ingame_name} {rank} đã đăng ký thành công!")
    except Exception as e:
        logging.error(f"Lỗi trong register: {e}")
        await update.message.reply_text("Lỗi không thể đăng ký!")

async def registerweek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) != 2:
            await update.message.reply_text("Sai cú pháp: /registerweek <ingamename> <rank>")
            return

        ingame_name = args[0]
        rank = args[1]

        if rank not in ['R1', 'R2', 'R3', 'R4', 'R5']:
            await update.message.reply_text("Sai cú pháp rank là một trong các giá trị: R1, R2, R3, R4, R5")
            return

        player_exists = False
        if os.path.exists(PLAYER_FILE):
            with open(PLAYER_FILE, 'r') as file:
                for line in file:
                    if line.startswith(ingame_name + ','):
                        player_exists = True
                        break

        if not player_exists:
            await update.message.reply_text(f"Người chơi {ingame_name} chưa được đăng ký trong hệ thống!")
            return

        player_week_exists = False
        if os.path.exists(PLAYER_WEEK_FILE):
            with open(PLAYER_FILE, 'r') as file:
                for line in file:
                    if line.startswith(ingame_name + ','):
                        player_week_exists = True

        if player_week_exists:
            await update.message.reply_text(f"Người chơi {ingame_name} đã được đăng ký cho tuần này!")
            return

        sotran = 0
        if os.path.exists(PLAYER_SOTRAN_FILE):
            with open(PLAYER_FILE, 'r') as file:
                for line in file:
                    name, sotrandata = line.strip().split(',')
                    if name == ingame_name:
                        sotran = int(sotrandata)

        with open(PLAYER_WEEK_FILE, 'a') as file:
            file.write(f"\n{ingame_name},{rank},{sotran}")

        await update.message.reply_text(f"Chào mừng {ingame_name} {rank} đã đăng ký tuần này thành công!")
    except Exception as e:
        logging.error(f"Lỗi registerweek command: {e}")
        await update.message.reply_text("Lỗi không thể đăng ký!.")

async def random_teams(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not os.path.exists(PLAYER_WEEK_FILE):
            await update.message.reply_text("Chưa có người chơi đăng ký trong tuần này!")
            return

        players = []

        with open(PLAYER_WEEK_FILE, 'r') as file:
            for line in file:
                ingame_name, rank, sotran = line.strip().split(',')
                players.append((ingame_name, rank, int(sotran)))

        if len(players) < 10:
            await update.message.reply_text("Số người chơi dưới 10 người không thể random team!")
            return

        # sort theo số trận
        players.sort(key=lambda x: x[2], reverse=True)
        players = players[-10:]

        r1_players = [p for p in players if p[1] == 'R1']
        r2_players = [p for p in players if p[1] == 'R2']
        r3_players = [p for p in players if p[1] == 'R3']
        r4_players = [p for p in players if p[1] == 'R4']
        r5_players = [p for p in players if p[1] == 'R5']

        random.shuffle(r1_players)
        random.shuffle(r2_players)
        random.shuffle(r3_players)
        random.shuffle(r4_players)
        random.shuffle(r5_players)

        teams = [[], []]
        team_points = [0, 0]

        def add_player_to_team(player, team_index):
            teams[team_index].append(player[0])
            team_points[team_index] += int(player[1][1])

        while r1_players or r2_players or r3_players or r4_players or r5_players:
            for i in range(2):
                if r1_players:
                    add_player_to_team(r1_players.pop(), i)
                elif r2_players:
                    add_player_to_team(r2_players.pop(), i)
                elif r3_players:
                    add_player_to_team(r3_players.pop(), i)
                elif r4_players:
                    add_player_to_team(r4_players.pop(), i)
                elif r5_players:
                    add_player_to_team(r5_players.pop(), i)

        response = "Teams đã random:\n"
        for i, team in enumerate(teams):
            response += f"Team {i + 1} (Points: {team_points[i]}):\n"
            for player in team:
                response += f"  - {player}\n"
        await update.message.reply_text(response)
    except Exception as e:
        logging.error(f"Error in random_teams command: {e}")
        await update.message.reply_text("Lỗi không thể random")

if __name__ == '__main__':
    application = ApplicationBuilder().token('7988356940:AAGG13Q_EUHxPZJTE6WoYBn2YBX1lLgK2K0').build()

    application.add_handler(CommandHandler('register', register))

    application.add_handler(CommandHandler('registerweek', registerweek))

    application.add_handler(CommandHandler('random', random_teams))

    application.add_handler(CommandHandler('getlistall', getlistall))

    application.add_handler(CommandHandler('getlistofweek', getlistofweek))

    application.run_polling()