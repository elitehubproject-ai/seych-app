import vk_api
import os
import json
from dotenv import load_dotenv

load_dotenv()

class BotSender:
    def __init__(self):
        # Токен бота сообщества
        self.token = os.getenv('VK_BOT_TOKEN')
        if not self.token:
            raise ValueError("VK_BOT_TOKEN не найден в переменных окружения")
        
        # Инициализация VK API
        self.vk_session = vk_api.VkApi(token=self.token)
        self.vk = self.vk_session.get_api()
        
        # Загружаем ID чатов
        self.load_chat_ids()
    
    def load_chat_ids(self):
        """Загружает ID чатов из JSON файла"""
        try:
            if os.path.exists('chats_config.json'):
                with open('chats_config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.archive_chat_id = config.get('archive')
                    self.normal_chat_id = config.get('normal')
                    
                print(f"Архивный чат: {self.archive_chat_id}")
                print(f"Обычный чат: {self.normal_chat_id}")
        except Exception as e:
            print(f"Ошибка загрузки конфигурации: {e}")
    
    def send_to_normal_chat(self, message):
        """Отправляет сообщение в обычный чат от бота сообщества"""
        if not self.normal_chat_id:
            print("❌ Обычный чат не настроен")
            return
        
        try:
            self.vk.messages.send(
                peer_id=self.normal_chat_id,
                message=message,
                random_id=0
            )
            print(f"✅ Сообщение отправлено в обычный чат: {message}")
        except Exception as e:
            print(f"❌ Ошибка отправки: {e}")
    
    def send_to_archive_chat(self, message):
        """Отправляет сообщение в архивный чат от бота сообщества"""
        if not self.archive_chat_id:
            print("❌ Архивный чат не настроен")
            return
        
        try:
            self.vk.messages.send(
                peer_id=self.archive_chat_id,
                message=message,
                random_id=0
            )
            print(f"✅ Сообщение отправлено в архивный чат: {message}")
        except Exception as e:
            print(f"❌ Ошибка отправки: {e}")
    
    def run(self):
        """Запускает интерактивный режим отправки сообщений"""
        print("=== Отправка сообщений от бота сообщества ===")
        print("Команды:")
        print("  /normal <текст> - отправить в обычный чат")
        print("  /archive <текст> - отправить в архивный чат")
        print("  /exit - выход")
        print()
        
        while True:
            try:
                command = input("Введите команду: ").strip()
                
                if command == "/exit":
                    print("Выход...")
                    break
                
                if command.startswith("/normal "):
                    message = command[8:]  # Убираем "/normal "
                    if message:
                        self.send_to_normal_chat(message)
                    else:
                        print("❌ Введите текст сообщения")
                
                elif command.startswith("/archive "):
                    message = command[9:]  # Убираем "/archive "
                    if message:
                        self.send_to_archive_chat(message)
                    else:
                        print("❌ Введите текст сообщения")
                
                else:
                    print("❌ Неизвестная команда. Используйте /normal, /archive или /exit")
                    
            except KeyboardInterrupt:
                print("\nВыход...")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    sender = BotSender()
    sender.run()