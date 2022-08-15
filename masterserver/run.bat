cd /D "%~dp0"
gunicorn -w 1 server:app