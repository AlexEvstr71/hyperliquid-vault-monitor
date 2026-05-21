# Hyperliquid Vault Monitor

Проверяет топ vault'ов на Hyperliquid два раза в день (9:00 и 21:00 UTC) и отправляет результат в Telegram.

## Настройка

1. Создать бота в @BotFather, получить токен
2. Узнать свой chat ID через @userinfobot
3. Добавить Secrets в репозиторий:
   - `TELEGRAM_BOT_TOKEN` — токен бота
   - `TELEGRAM_CHAT_ID` — твой ID
