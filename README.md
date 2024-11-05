![](https://camo.githubusercontent.com/47efefccd622962888745b474dba367a6b1716f032dc40fb7a34a8ad365cea88/68747470733a2f2f692e696d6775722e636f6d2f6f436f623377512e676966)

### About

The bot is specially designed for [SteamGifts.com](https://www.steamgifts.com/)

### Features

- Automatically enters giveaways.
- Undetectable.
- Сonvenient user interface.
- Сonfigurable.
- Sleeps to restock the points.
- Can run 24/7.
  Added by Maag
- Can use with docker
- Log for already join giveaways
- If you put variable DEFAULT_PAGE=1 in env, the bot only repeat the first page

### How to run

1. Download the latest version
2. Sign in on [SteamGifts.com](https://www.steamgifts.com/) by Steam.
3. Find `PHPSESSID` cookie in your browser.
4. Start the bot and follow instructions or configure the .env to use with docker

### Run from sources

```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
python src/cli.py
```

original creator: https://github.com/stilManiac/steamgifts-bot/
