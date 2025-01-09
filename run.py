import os
from app import create_app

# Определяем текущую среду
env = os.getenv('FLASK_ENV')

# Создаем приложение
app = create_app(env)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000)