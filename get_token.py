import vk_api

# Получение токена пользователя
def get_user_token():
    print("Перейди по ссылке и получи токен:")
    print("https://oauth.vk.com/authorize?client_id=2274003&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=messages,offline&response_type=token&v=5.131")
    
    token = input("Вставь токен сюда: ")
    
    # Проверяем токен
    try:
        vk_session = vk_api.VkApi(token=token)
        vk = vk_session.get_api()
        user_info = vk.users.get()
        print(f"Токен работает! Пользователь: {user_info[0]['first_name']} {user_info[0]['last_name']}")
        
        # Записываем в .env
        with open('.env', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Заменяем токен
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('VK_USER_TOKEN='):
                lines[i] = f'VK_USER_TOKEN={token}'
                break
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print("Токен сохранен в .env файл!")
        
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    get_user_token()