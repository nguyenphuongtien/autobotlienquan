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
TEAM_A_FILE = 'team_a.txt'
TEAM_B_FILE = 'team_b.txt'

AUTHORIZED_USERS = [643097997,722793625,668057873,858032816]

def restricted(func):
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in AUTHORIZED_USERS:
            await update.message.reply_text("Bạn không có quyền sử dụng lệnh này!")
            return
        return await func(update, context, *args, **kwargs)
    return wrapped

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
        await update.message.reply_text("Lỗi trong quá trình getlistofweek!")\

async def gettop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not os.path.exists(PLAYER_DIEM_FILE):
            await update.message.reply_text("Không có dữ liệu điểm của người chơi!")
            return

        player_points = []
        with open(PLAYER_DIEM_FILE, 'r') as file:
            for line in file:
                ingame_name, points = line.strip().split(',')
                player_points.append((ingame_name, int(points)))

        # Sort players by points in descending order
        player_points.sort(key=lambda x: x[1], reverse=True)

        # Prepare the response message
        response = "Top người chơi:\n"
        i = 0
        for ingame_name, points in player_points:
            i += 1
            response += f"{i}. {ingame_name}: {points} điểm\n"

        await update.message.reply_text(response)
    except Exception as e:
        logging.error(f"Lỗi trong gettop: {e}")
        await update.message.reply_text("Lỗi không thể lấy danh sách top người chơi!")

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
        if len(args) != 1:
            await update.message.reply_text("Sai cú pháp: /registerweek <ingamename>")
            return

        ingame_name = args[0]

        rank = None
        if os.path.exists(PLAYER_FILE):
            with open(PLAYER_FILE, 'r') as file:
                for line in file:
                    name, player_rank = line.strip().split(',')
                    if name == ingame_name:
                        rank = player_rank
                        break

        if rank is None:
            await update.message.reply_text(f"Người chơi {ingame_name} chưa được đăng ký trong hệ thống!")
            return

        player_week_exists = False
        if os.path.exists(PLAYER_WEEK_FILE):
            with open(PLAYER_WEEK_FILE, 'r') as file:
                for line in file:
                    if line.startswith(ingame_name + ','):
                        player_week_exists = True
                        break

        if player_week_exists:
            await update.message.reply_text(f"Người chơi {ingame_name} đã được đăng ký cho tuần này!")
            return

        sotran = 0
        if os.path.exists(PLAYER_SOTRAN_FILE):
            with open(PLAYER_SOTRAN_FILE, 'r') as file:
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

@restricted
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

        with open(TEAM_A_FILE, 'w') as file:
            file.write('')

        with open(TEAM_B_FILE, 'w') as file:
            file.write('')

        with open(TEAM_A_FILE, 'a+') as file:
            for i in teams[0]:
                file.seek(0, os.SEEK_END)
                if file.tell() > 0:
                    file.write(f"\n{i}")
                else:
                    file.write(f"{i}")

        with open(TEAM_B_FILE, 'a+') as file:
            for i in teams[1]:
                file.seek(0, os.SEEK_END)
                if file.tell() > 0:
                    file.write(f"\n{i}")
                else:
                    file.write(f"{i}")

        response = "Teams đã random:\n"
        for i, team in enumerate(teams):
            response += f"Team {i + 1} (Points: {team_points[i]}):\n"
            for player in team:
                response += f"  - {player}\n"
        await update.message.reply_text(response)
    except Exception as e:
        logging.error(f"Error in random_teams command: {e}")
        await update.message.reply_text("Lỗi không thể random")

@restricted
async def resetplayerweek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open(PLAYER_WEEK_FILE, 'w') as file:
            file.write('')

        with open(TEAM_A_FILE, 'w') as file:
            file.write('')

        with open(TEAM_B_FILE, 'w') as file:
            file.write('')

        await update.message.reply_text("Reset người chơi tuần này thành công!")
    except Exception as e:
        logging.error(f"Lỗi resetplayerweek command: {e}")
        await update.message.reply_text("Lỗi không thể reset người chơi tuần này!")

@restricted
async def pluspoint(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) != 2:
            await update.message.reply_text("Sai cú pháp: /pluspoint <TEAMNAME> <point>")
            return

        team_name = args[0].upper()
        point = int(args[1])

        if team_name not in ['TEAM_A', 'TEAM_B']:
            await update.message.reply_text("Sai cú pháp: TEAMNAME phải là TEAM_A hoặc TEAM_B")
            return

        file_name = TEAM_A_FILE if team_name == 'TEAM_A' else TEAM_B_FILE

        if not os.path.exists(file_name):
            await update.message.reply_text(f"Không tìm thấy file cho {team_name}!")
            return

        with open(file_name, 'r') as file:
            players = [line.strip() for line in file.readlines()]

        player_points = {}
        if os.path.exists(PLAYER_DIEM_FILE):
            with open(PLAYER_DIEM_FILE, 'r') as file:
                for line in file:
                    ingame_name, current_points = line.strip().split(',')
                    player_points[ingame_name] = int(current_points)

        for player in players:
            if player in player_points:
                player_points[player] += point
            else:
                player_points[player] = point

        with open(PLAYER_DIEM_FILE, 'w') as file:
            for ingame_name, total_points in player_points.items():
                file.write(f"{ingame_name},{total_points}\n")

        await update.message.reply_text(f"Đã cộng {point} điểm cho mỗi người chơi trong {team_name}!")

    except Exception as e:
        logging.error(f"Lỗi trong pluspoint: {e}")
        await update.message.reply_text("Lỗi không thể cộng điểm!")

async def get_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        await update.message.reply_text(f"User ID của bạn là: {user_id}")
    except Exception as e:
        logging.error(f"Lỗi trong get_user_id: {e}")
        await update.message.reply_text("Lỗi không thể lấy User ID!")

@restricted
async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) != 2:
            await update.message.reply_text("Sai cú pháp: /remove <listname> <ingamename>")
            return

        list_type = args[0].upper()
        ingame_name = args[1]

        if list_type == 'LISTALL':
            file_path = PLAYER_FILE
        elif list_type == 'LISTWEEK':
            file_path = PLAYER_WEEK_FILE
        else:
            await update.message.reply_text("Sai cú pháp: listname phải là LISTALL hoặc LISTWEEK")
            return

        if not os.path.exists(file_path):
            await update.message.reply_text("Không có người chơi nào được đăng ký!")
            return

        with open(file_path, 'r') as file:
            players = [line.strip() for line in file.readlines()]

        if ingame_name not in [player.split(',')[0] for player in players]:
            await update.message.reply_text(f"Người chơi {ingame_name} không có trong danh sách đăng ký!")
            return

        players = [player for player in players if not player.startswith(ingame_name + ',')]

        with open(file_path, 'w') as file:
            for player in players:
                file.write(f"{player}\n")

        if list_type == 'LISTALL':
            with open(PLAYER_SOTRAN_FILE, 'r') as file:
                players = [line.strip() for line in file.readlines()]

            players = [player for player in players if not player.startswith(ingame_name + ',')]

            with open(PLAYER_SOTRAN_FILE, 'w') as file:
                for player in players:
                    file.write(f"{player}\n")

            with open(PLAYER_DIEM_FILE, 'r') as file:
                players = [line.strip() for line in file.readlines()]

            players = [player for player in players if not player.startswith(ingame_name + ',')]

            with open(PLAYER_DIEM_FILE, 'w') as file:
                for player in players:
                    file.write(f"{player}\n")

        await update.message.reply_text(f"Đã xóa {ingame_name} khỏi danh sách {list_type.lower()}!")
    except Exception as e:
        logging.error(f"Lỗi trong remove: {e}")
        await update.message.reply_text("Lỗi không thể xóa người chơi!")

async def getmatch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not os.path.exists(TEAM_A_FILE) or not os.path.exists(TEAM_B_FILE):
            await update.message.reply_text("Không có dữ liệu đội!")
            return

        team_a = []
        team_b = []

        with open(TEAM_A_FILE, 'r') as file:
            team_a = [line.strip() for line in file.readlines()]

        with open(TEAM_B_FILE, 'r') as file:
            team_b = [line.strip() for line in file.readlines()]

        if not team_a or not team_b:
            await update.message.reply_text("Dữ liệu đội không đầy đủ!")
            return

        response = "Trận đấu:\n"
        response += "Đội A:\n"
        for player in team_a:
            response += f"  - {player}\n"

        response += "Đội B:\n"
        for player in team_b:
            response += f"  - {player}\n"

        await update.message.reply_text(response)
    except Exception as e:
        logging.error(f"Lỗi trong getmatch: {e}")
        await update.message.reply_text("Lỗi không thể lấy danh sách trận đấu!")

@restricted
async def congsotran(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not os.path.exists(TEAM_A_FILE) or not os.path.exists(TEAM_B_FILE):
            await update.message.reply_text("Không có dữ liệu đội!")
            return

        team_a = []
        team_b = []

        with open(TEAM_A_FILE, 'r') as file:
            team_a = [line.strip() for line in file.readlines()]

        with open(TEAM_B_FILE, 'r') as file:
            team_b = [line.strip() for line in file.readlines()]

        players = team_a + team_b

        if not os.path.exists(PLAYER_SOTRAN_FILE):
            await update.message.reply_text("Không có dữ liệu số trận của người chơi!")
            return

        player_matches = {}
        with open(PLAYER_SOTRAN_FILE, 'r') as file:
            for line in file:
                ingame_name, matches = line.strip().split(',')
                player_matches[ingame_name] = int(matches)

        for player in players:
            if player in player_matches:
                player_matches[player] += 1
            else:
                player_matches[player] = 1

        with open(PLAYER_SOTRAN_FILE, 'w') as file:
            for ingame_name, matches in player_matches.items():
                file.write(f"{ingame_name},{matches}\n")

        await update.message.reply_text("Đã cộng số trận cho các người chơi trong đội A và đội B!")
    except Exception as e:
        logging.error(f"Lỗi trong congsotran: {e}")
        await update.message.reply_text("Lỗi không thể cộng số trận!")


if __name__ == '__main__':
    application = ApplicationBuilder().token('7988356940:AAGG13Q_EUHxPZJTE6WoYBn2YBX1lLgK2K0').build()

    application.add_handler(CommandHandler('dangky', register))

    application.add_handler(CommandHandler('dangkytuan', registerweek))

    application.add_handler(CommandHandler('laybxh', gettop))

    application.add_handler(CommandHandler('laydanhsachdangky', getlistall))

    application.add_handler(CommandHandler('laydanhsachtuan', getlistofweek))

    application.add_handler(CommandHandler('getuserid', get_user_id))

    application.add_handler(CommandHandler('reset', resetplayerweek))

    application.add_handler(CommandHandler('congdiem', pluspoint))

    application.add_handler(CommandHandler('random', random_teams))

    application.add_handler(CommandHandler('remove', remove))

    application.add_handler(CommandHandler('xemtrandau', getmatch))

    application.add_handler(CommandHandler('congsotran', congsotran))


    application.run_polling()