import bot


if __name__ == '__main__':
    with open("token.txt") as token_file:
        TOKEN = token_file.read()
    bot.run_bot(TOKEN)
