import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

class ChatDebugger:
    def __init__(self):
        self.token = os.getenv('VK_BOT_TOKEN')
        self.group_id = os.getenv('VK_GROUP_ID')
        
        if not self.token or not self.group_id:
            print("Ошибка: проверьте настройки в .env файле")
            return
        
        self.vk_session = vk_api.VkApi(token=self.token)
        self.longpoll = VkBotLongPoll(self.vk_session, self.group_id)
        self.vk = self.vk_session.get_api()
        
    def run(self):
        print("Отладчик чатов запущен...")
        print("Напишите сообщение в любой чат чтобы увидеть его ID")
        print("Для выхода нажмите Ctrl+C")
        
        try:
            for event in self.longpoll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW:
                    message = event.message
                    print(f"\n=== НОВОЕ СООБЩЕНИЕ ===")
                    print(f"ID пользователя: {message['from_id']}")
                    print(f"ID чата: {message['peer_id']}")
                    print(f"Текст: {message['text']}")
                    print(f"Тип чата: {'личные сообщения' if message['peer_id'] == message['from_id'] else 'беседа'}")
                    
                    # Отправляем ответ с ID чата
                    self.vk.messages.send(
                        peer_id=message['peer_id'],
                        message=f"ID этого чата: {message['peer_id']}",
                        random_id=0
                    )
                    
        except KeyboardInterrupt:
            print("\nОтладчик остановлен")

if __name__ == "__main__":
    debugger = ChatDebugger()
    debugger.run()
