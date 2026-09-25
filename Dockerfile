FROM python:3.12-slim

WORKDIR /app

# Копируем и устанавливаем зависимости отдельно для кэширования слоев
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной код проекта
COPY . .

# Команда для запуска бота
CMD ["python", "-m", "src.bot.main"]