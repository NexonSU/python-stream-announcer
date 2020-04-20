# python-stream-announcer
Simple Stream Telegram Announcer from Youtube and Twitch

## twitch.py requirements
Requests library:
```bash
pip install requests
```

## youtube.py requirements
Requests library:
```bash
pip install requests
```
BeautifulSoup library:
```bash
pip install beautifulsoup4
```
youtube-dl:
```bash
pip install youtube-dl
```
ffmpeg:

Before installing ffmpeg wrapper, install ffmpeg binary to your system
```bash
pip install ffmpeg-python
```

# TODO
- [X] Move keys and IDs to config file
- [X] Change temp file storage to something like pickle
- [X] Add logging
- [X] Integrate youtube-dl to youtube.py
- [X] Integrate ffmpeg to youtube.py
- [ ] Upload files directly to telegram without web-server in youtube.py
- [ ] English translate
