import vk_api
import os
from dotenv import load_dotenv

load_dotenv()

def check_user_id():
    token = os.getenv('VK_USER_TOKEN')
    
    try:
        vk_session = vk_api.VkApi(token=token)
        vk = vk_session.get_api()
        
        user_info = vk.users.get()
        user_id = user_info[0]['id']
        name = f"{user_info[0]['first_name']} {user_info[0]['last_name']}"
        
        print(f"ID пользователя токена: {user_id}")
        print(f"Имя: {name}")
        
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    check_user_id()