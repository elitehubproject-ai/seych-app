import subprocess
import sys

def install_requirements():
    """Устанавливает зависимости из requirements.txt"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Зависимости успешно установлены")
    except subprocess.CalledProcessError:
        print("❌ Ошибка при установке зависимостей")

def check_requirements():
    """Проверяет установлены ли все необходимые пакеты"""
    required_packages = ['vk-api', 'python-dotenv']
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} установлен")
        except ImportError:
            print(f"❌ {package} не установлен")

if __name__ == "__main__":
    print("Проверка и установка зависимостей...")
    install_requirements()
    print("\nПроверка установленных пакетов:")
    check_requirements()
    print("\n🔥 Настройка завершена! Создайте файл .env и запустите бота командой: python bot.py")