import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import random
import os

# Initialize logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# File to store player information
PLAYER_FILE = 'list_players.txt'

# File to store list of players by week
PLAYER_WEEK_FILE = 'list_players_week.txt'

async def showlistweek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not os.path.exists(PLAYER_WEEK_FILE):
            await update.message.reply_text("No players registered for the week.")
            return

        players = []
        with open(PLAYER_WEEK_FILE, 'r') as file:
            for line in file:
                ingame_name, rank = line.strip().split(',')
                players.append((ingame_name, rank))

        # Sort players by rank
        players.sort(key=lambda x: x[1])

        response = "List of Players for the Week:\n"
        for ingame_name, rank in players:
            response += f"{ingame_name} - {rank}\n"

        await update.message.reply_text(response)
    except Exception as e:
        logging.error(f"Error in showlistweek command: {e}")
        await update.message.reply_text("An error occurred while showing the weekly list.")

async def showlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not os.path.exists(PLAYER_FILE):
            await update.message.reply_text("No players registered.")
            return

        players = []
        with open(PLAYER_FILE, 'r') as file:
            for line in file:
                ingame_name, rank = line.strip().split(',')
                players.append((ingame_name, rank))

        # Sort players by rank
        players.sort(key=lambda x: (x[1], x[0]))

        response = "List of Players:\n"
        for ingame_name, rank in players:
            response += f"{ingame_name} - {rank}\n"

        await update.message.reply_text(response)
    except Exception as e:
        logging.error(f"Error in showlist command: {e}")
        await update.message.reply_text("An error occurred while showing the list.")

#register a player
async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) != 2:
            await update.message.reply_text("Sai cú pháp: /register <IngameName> <Rank>")
            return

        ingame_name = args[0]
        rank = args[1]

        if rank not in ['R1', 'R2', 'R3']:
            await update.message.reply_text("Rank không đúng phải là một trong ba giá trị: R1, R2, R3!")
            return

        # Check if the player already exists
        if os.path.exists(PLAYER_FILE):
            with open(PLAYER_FILE, 'r') as file:
                for line in file:
                    if line.startswith(ingame_name + ','):
                        await update.message.reply_text(f"Người chơi {ingame_name} đã được đăng ký!")
                        return

        # Save the player information to the file
        with open(PLAYER_FILE, 'a') as file:
            file.write(f"\n{ingame_name},{rank}")

        await update.message.reply_text(f"Chào mừng {ingame_name} với rank {rank} đã đăng ký thành công!")
    except Exception as e:
        logging.error(f"Error in register command: {e}")
        await update.message.reply_text("An error occurred during registration.")

async def registerweek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) != 2:
            await update.message.reply_text("Sai cú pháp: /registerweek <IngameName> <Rank>")
            return

        ingame_name = args[0]
        rank = args[1]

        if rank not in ['R1', 'R2', 'R3']:
            await update.message.reply_text("Rank không đúng phải là một trong ba giá trị: R1, R2, R3")
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

        # Save the player information to the weekly file
        with open(PLAYER_WEEK_FILE, 'a') as file:
            file.write(f"\n{ingame_name},{rank}")

        await update.message.reply_text(f"Chào mừng {ingame_name} với rank {rank} đã đăng ký tuần này thành công!")
    except Exception as e:
        logging.error(f"Error in registerweek command: {e}")
        await update.message.reply_text("An error occurred during weekly registration.")

# Random teams
async def random_teams(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not os.path.exists(PLAYER_WEEK_FILE):
            await update.message.reply_text("No players registered for the week.")
            return

        r1_players = []
        r2_players = []
        r3_players = []

        with open(PLAYER_WEEK_FILE, 'r') as file:
            for line in file:
                try:
                    ingame_name, rank = line.strip().split(',')
                    if rank == 'R1':
                        r1_players.append(ingame_name)
                    elif rank == 'R2':
                        r2_players.append(ingame_name)
                    elif rank == 'R3':
                        r3_players.append(ingame_name)
                except ValueError:
                    break

        random.shuffle(r1_players)
        random.shuffle(r2_players)
        random.shuffle(r3_players)

        total_players = len(r1_players) + len(r2_players) + len(r3_players)
        if total_players < 10:
            await update.message.reply_text("Số người chơi dưới 10 người không thể random team!")
            return

        if total_players < 15:
            num_teams = 2
        elif total_players < 20:
            num_teams = 3
        elif total_players < 25:
            num_teams = 4
        elif total_players < 30:
            num_teams = 5
        else:
            await update.message.reply_text("chưa được cấu hình lớn hơn 5 đội chơi!")
            return

        teams = [[] for _ in range(num_teams)]
        team_points = [0] * num_teams

        total_points = len(r1_players) * 3 + len(r2_players) * 2 + len(r3_players)
        average_points_per_player = total_points / total_players

        while r1_players or r2_players or r3_players:
            for i in range(1):
                player_picked = False
                while not player_picked:
                    try:
                        rankRandom = ['R1', 'R2', 'R3']
                        choice = random.choice(rankRandom)
                        if not r1_players:
                            choice = random.choice(rankRandom.remove('R1'))

                        if not r2_players:
                            choice = random.choice(rankRandom.remove('R2'))

                        if not r2_players:
                            choice = random.choice(rankRandom.remove('R3'))

                        if choice == 'R1' and r1_players:
                            player = r1_players.pop()
                            teams[i].append(player)
                            team_points[i] += 3
                        elif choice == 'R2' and r2_players:
                            player = r2_players.pop()
                            teams[i].append(player)
                            team_points[i] += 2
                        elif choice == 'R3' and r3_players:
                            player = r3_players.pop()
                            teams[i].append(player)
                            team_points[i] += 1

                        if (len(teams[i]) == 5):
                            player_picked = True

                    except IndexError:
                        break

        response = "Randomized Teams:\n"
        for i, team in enumerate(teams):
            response += f"Team {i + 1}:\n"
            for player in team:
                response += f"  - {player}\n"
        await update.message.reply_text(response)
    except Exception as e:
        logging.error(f"Error in random_teams command: {e}")
        await update.message.reply_text("An error occurred during team randomization.")

if __name__ == '__main__':
    application = ApplicationBuilder().token('7988356940:AAGG13Q_EUHxPZJTE6WoYBn2YBX1lLgK2K0').build()

    application.add_handler(CommandHandler('register', register))

    application.add_handler(CommandHandler('registerweek', registerweek))

    application.add_handler(CommandHandler('random', random_teams))

    application.add_handler(CommandHandler('showlist', showlist))

    application.add_handler(CommandHandler('showlistweek', showlistweek))

    application.run_polling()