import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import os
import json
import random
import time
import threading
from datetime import datetime, timedelta
from dotenv import load_dotenv
from collections import defaultdict, Counter

load_dotenv()

DEVELOPER_ID = 532796366
vk_session = vk_api.VkApi(token=os.getenv('VK_BOT_TOKEN'))
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, group_id=int(os.getenv('VK_GROUP_ID')))
upload = vk_api.VkUpload(vk_session)  # Добавьте эту строку для загрузки фото

# Словарь для преобразования сроков в дни
DURATION_TO_DAYS = {
    '1 день': 1,
    'неделя': 7,
    'месяц': 30,
    'полгода': 180,
    'год': 365,
    'навсегда': -1
}

# Словарь для преобразования типов кейсов
CASE_TYPES = {
    'ng': 'новогодний',
    'ng_case': 'новогодний кейс',
    'random': 'рандомный'
}

# Словарь подписок
SUBSCRIPTIONS = {
    'vip': {'id': 1, 'name': 'V.I.P'},
    'premium': {'id': 2, 'name': 'PREMIUM'},
    'deluxe': {'id': 3, 'name': 'DELUXE'},
    'luxe': {'id': 4, 'name': 'LUXE'}
}

# ========== ФАЙЛЫ ДАННЫХ БАНКА ==========
ELITE_DATA_FILE = 'elite_data.json'
BANK_DATA_FILE = 'bank_data.json'
NICKNAMES_FILE = 'nicknames.json'
TRANSACTIONS_FILE = 'transactions.json'
BANK_SESSIONS_FILE = 'bank_sessions.json'  # Новый файл для отслеживания сессий банка
BANK_WAITING_OPERATION = 'bank_waiting_operation.json'  # Файл для ожидающих операций

# ========== КОНСТАНТЫ БАНКА ==========
BANK_STORAGE_LIMIT = 10000
CASH_PER_MESSAGE = 1

def load_elite_data():
    """Загружает данные о валюте Elite"""
    try:
        with open(ELITE_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_elite_data(data):
    """Сохраняет данные о валюте Elite"""
    with open(ELITE_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_bank_data():
    """Загружает данные банка"""
    try:
        with open(BANK_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_bank_data(data):
    """Сохраняет данные банка"""
    with open(BANK_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_nicknames():
    """Загружает никнеймы пользователей"""
    try:
        with open(NICKNAMES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_nicknames(data):
    """Сохраняет никнеймы пользователей"""
    with open(NICKNAMES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_transactions():
    """Загружает историю транзакций"""
    try:
        with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_transactions(data):
    """Сохраняет историю транзакций"""
    with open(TRANSACTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_bank_sessions():
    """Загружает активные сессии банка"""
    try:
        with open(BANK_SESSIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_bank_sessions(data):
    """Сохраняет активные сессии банка"""
    with open(BANK_SESSIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_waiting_operations():
    """Загружает ожидающие операции банка"""
    try:
        with open(BANK_WAITING_OPERATION, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_waiting_operations(data):
    """Сохраняет ожидающие операции банка"""
    with open(BANK_WAITING_OPERATION, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user_name(user_id):
    try:
        user = vk.users.get(user_ids=user_id)[0]
        return f"{user.get('first_name', '')} {user.get('last_name', '')}"
    except:
        return "Пользователь"

def get_nickname(user_id):
    """Получает никнейм пользователя"""
    nicknames = load_nicknames()
    return nicknames.get(str(user_id), None)

def get_display_name(user_id):
    """Получает отображаемое имя (ник или обычное имя)"""
    nickname = get_nickname(user_id)
    if nickname:
        return nickname
    return get_user_name(user_id)

def get_case_type_name(case_type):
    """Преобразует сокращенное название кейса в полное"""
    return CASE_TYPES.get(case_type, case_type)

def load_chats():
    try:
        with open('chats_config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def load_cases():
    try:
        with open('cases.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        return {}

def load_expiring_prizes():
    try:
        with open('expiring_prizes.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def load_inventory():
    try:
        with open('inventory.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_cases(cases):
    with open('cases.json', 'w', encoding='utf-8') as f:
        json.dump(cases, f, ensure_ascii=False, indent=2)

def save_expiring_prizes(prizes):
    with open('expiring_prizes.json', 'w', encoding='utf-8') as f:
        json.dump(prizes, f, ensure_ascii=False, indent=2)

def save_inventory(inventory):
    with open('inventory.json', 'w', encoding='utf-8') as f:
        json.dump(inventory, f, ensure_ascii=False, indent=2)

def load_new_year_greetings():
    """Загружает данные о новогодних поздравлениях"""
    try:
        with open('new_year_greetings.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'last_greeting_date': None, 'last_greeted_user': None, 'enabled': True}

def save_new_year_greetings(greetings):
    """Сохраняет данные о новогодних поздравлениях"""
    with open('new_year_greetings.json', 'w', encoding='utf-8') as f:
        json.dump(greetings, f, ensure_ascii=False, indent=2)

def send_new_year_greeting(user_id, peer_id, event_type=None, callback_data=None):
    """Отправляет новогоднее поздравление пользователю"""
    today = datetime.now().strftime('%Y-%m-%d')
    current_hour = datetime.now().hour
    
    # Проверяем, сейчас декабрь и приближается Новый год
    current_month = datetime.now().month
    if current_month != 12:
        return
    
    greetings = load_new_year_greetings()
    
    # Если поздравления отключены
    if not greetings.get('enabled', True):
        return
    
    # Проверяем, нужно ли отправлять поздравление сегодня
    last_date = greetings.get('last_greeting_date')
    last_user = greetings.get('last_greeted_user')
    
    # Если сегодня еще не поздравляли или поздравляли другого пользователя
    if last_date != today or last_user != str(user_id):
        # Новогодние поздравления
        new_year_messages = [
            "🎄 С наступающим Новым годом! Пусть он принесет много радости, счастья и удачи!",
            "❄️ С наступающим! Желаю, чтобы Новый год стал самым ярким и успешным в вашей жизни!",
            "✨ С Новым годом! Пусть все мечты сбываются, а каждый день будет наполнен волшебством!",
            "🎅 С наступающим Новым годом! Желаю здоровья, благополучия и исполнения всех желаний!",
            "🎁 С Новым годом! Пусть этот год принесет вам только позитивные перемены и радостные моменты!",
            "🌟 С наступающим! Пусть Новый год будет полон тепла, уюта и счастливых событий!",
            "🦌 С Новым годом! Желаю, чтобы все плохое осталось в старом году, а новый начался с чистого листа!",
            "⛄ С наступающим Новым годом! Пусть он будет щедрым на подарки судьбы и приятные сюрпризы!"
        ]
        
        message = random.choice(new_year_messages)
        
        try:
            # Если это callback событие (пользователь нажал кнопку), отправляем snackbar
            if event_type == 'callback' and callback_data:
                vk.messages.sendMessageEventAnswer(
                    event_id=callback_data['event_id'],
                    user_id=user_id,
                    peer_id=peer_id,
                    event_data=json.dumps({'type': 'show_snackbar', 'text': f"🎄 {message}"})
                )
                print(f"✓ Отправлено новогоднее snackbar уведомление пользователю {user_id}")
            else:
                # Отправляем приватное сообщение с новогодней иконкой
                vk.messages.send(
                    peer_id=user_id,
                    message=f"🎄 {message}",
                    random_id=random.randint(1, 2147483647)
                )
                print(f"✓ Отправлено новогоднее приватное уведомление пользователю {user_id}")
            
            # Обновляем данные о поздравлении
            greetings['last_greeting_date'] = today
            greetings['last_greeted_user'] = str(user_id)
            save_new_year_greetings(greetings)
            
        except Exception as e:
            print(f"✗ Ошибка при отправке новогоднего уведомления: {e}")

def toggle_new_year_greetings(enable=True):
    """Включает/выключает новогодние поздравления"""
    greetings = load_new_year_greetings()
    greetings['enabled'] = enable
    save_new_year_greetings(greetings)
    status = "включены" if enable else "выключены"
    print(f"✓ Новогодние поздравления {status}")

def create_case(case_type, sender_id, recipient_id, from_admin=True):
    case_id = random.randint(100000, 999999)
    return {
        'id': case_id,
        'type': case_type,
        'sender_id': sender_id,
        'recipient_id': recipient_id,
        'opened': False,
        'waiting_gift': False,
        'in_inventory': False,
        'message_id': None,
        'conversation_message_id': None,
        'peer_id': None,
        'from_admin': from_admin,
        'current_sender_id': sender_id
    }

def create_subscription(sub_type, sender_id, recipient_id, duration, from_admin=True):
    sub_id = random.randint(100000, 999999)
    return {
        'id': sub_id,
        'type': sub_type,
        'sender_id': sender_id,
        'recipient_id': recipient_id,
        'opened': False,
        'waiting_gift': False,
        'in_inventory': False,
        'message_id': None,
        'conversation_message_id': None,
        'peer_id': None,
        'from_admin': from_admin,
        'current_sender_id': sender_id,
        'duration': duration,
        'subscription_type': sub_type,
        'subscription_id': SUBSCRIPTIONS.get(sub_type, {}).get('id', 1),
        'subscription_name': SUBSCRIPTIONS.get(sub_type, {}).get('name', 'Подписка')
    }

def get_random_prize():
    prizes = [
        {'id': 1, 'name': 'V.I.P'},
        {'id': 2, 'name': 'PREMIUM'},
        {'id': 3, 'name': 'DELUXE'},
        {'id': 4, 'name': 'LUXE'}
    ]
    durations = ['1 день', 'неделя', 'месяц', 'полгода', 'год', 'навсегда']
    
    prize = random.choice(prizes)
    duration = random.choice(durations)
    
    return prize, duration

def get_random_subscription_duration():
    durations = ['1 день', 'неделя', 'месяц', 'полгода', 'год', 'навсегда']
    return random.choice(durations)

def send_to_archive(message):
    try:
        chats = load_chats()
        archive_chat = chats.get('archive')
        if archive_chat:
            user_session = vk_api.VkApi(token=os.getenv('VK_USER_TOKEN'))
            user_vk = user_session.get_api()
            user_vk.messages.send(
                peer_id=archive_chat,
                message=message,
                random_id=random.randint(1, 2147483647)
            )
            print(f"✓ Отправлено в архивный чат: {message}")
    except Exception as e:
        print(f"✗ Ошибка отправки в архив: {e}")

def add_expiring_prize(user_id, prize_id, duration_str):
    if duration_str == 'навсегда':
        return
    
    days = DURATION_TO_DAYS.get(duration_str, 30)
    expire_date = datetime.now() + timedelta(days=days)
    
    prize_data = {
        'user_id': user_id,
        'prize_id': prize_id,
        'duration': duration_str,
        'expire_date': expire_date.isoformat(),
        'notified': False
    }
    
    prizes = load_expiring_prizes()
    prize_key = f"{user_id}_{prize_id}_{int(time.time())}"
    prizes[prize_key] = prize_data
    save_expiring_prizes(prizes)
    
    print(f"✓ Добавлен отслеживаемый приз: пользователь {user_id}, приз {prize_id}, срок {duration_str}")

def check_expired_prizes():
    while True:
        try:
            prizes = load_expiring_prizes()
            current_time = datetime.now()
            
            for prize_key, prize_data in prizes.items():
                if prize_data.get('notified'):
                    continue
                    
                expire_date = datetime.fromisoformat(prize_data['expire_date'])
                
                if current_time >= expire_date:
                    user_id = prize_data['user_id']
                    
                    try:
                        user_info = vk.users.get(user_ids=user_id, fields='screen_name')[0]
                        username = user_info.get('screen_name', f'id{user_id}')
                        
                        send_to_archive(f"роль @{username} 0")
                        print(f"⚠️ Срок приза истек: сброс роли для пользователя {user_id}")
                        
                        prize_data['notified'] = True
                        prizes[prize_key] = prize_data
                        
                    except Exception as e:
                        print(f"✗ Ошибка при сбросе истекшего приза: {e}")
            
            save_expiring_prizes(prizes)
            
            for prize_key, prize_data in list(prizes.items()):
                if prize_data.get('notified'):
                    expire_date = datetime.fromisoformat(prize_data['expire_date'])
                    if current_time >= expire_date + timedelta(days=7):
                        del prizes[prize_key]
            
            save_expiring_prizes(prizes)
            
        except Exception as e:
            print(f"✗ Ошибка при проверке истекших призов: {e}")
        
        time.sleep(300)

# ========== ФУНКЦИИ БАНКА И ВАЛЮТЫ ==========

def get_user_balance(user_id):
    """Получает баланс пользователя (наличные)"""
    elite_data = load_elite_data()
    user_id_str = str(user_id)
    if user_id_str in elite_data:
        return elite_data[user_id_str].get('cash', 0)
    return 0

def get_user_bank_balance(user_id):
    """Получает баланс пользователя в банке"""
    bank_data = load_bank_data()
    user_id_str = str(user_id)
    if user_id_str in bank_data:
        return bank_data[user_id_str].get('balance', 0)
    return 0

def update_user_balance(user_id, amount, is_bank=False):
    """Обновляет баланс пользователя"""
    if is_bank:
        bank_data = load_bank_data()
        user_id_str = str(user_id)
        
        if user_id_str not in bank_data:
            bank_data[user_id_str] = {
                'balance': 0,
                'transactions_count': 0,
                'frequent_transfers': {},
                'created_at': datetime.now().isoformat()
            }
        
        bank_data[user_id_str]['balance'] = max(0, bank_data[user_id_str]['balance'] + amount)
        save_bank_data(bank_data)
    else:
        elite_data = load_elite_data()
        user_id_str = str(user_id)
        
        if user_id_str not in elite_data:
            elite_data[user_id_str] = {
                'cash': 0,
                'total_earned': 0,
                'messages_count': 0,
                'last_message_time': None
            }
        
        elite_data[user_id_str]['cash'] = max(0, elite_data[user_id_str]['cash'] + amount)
        save_elite_data(elite_data)

def add_transaction(sender_id, receiver_id, amount, transaction_type='transfer'):
    """Добавляет транзакцию в историю"""
    transactions = load_transactions()
    
    transaction = {
        'id': len(transactions) + 1,
        'sender_id': sender_id,
        'receiver_id': receiver_id,
        'amount': amount,
        'type': transaction_type,
        'timestamp': datetime.now().isoformat(),
        'sender_name': get_display_name(sender_id),
        'receiver_name': get_display_name(receiver_id)
    }
    
    transactions.append(transaction)
    
    # Ограничиваем историю последними 1000 транзакций
    if len(transactions) > 1000:
        transactions = transactions[-1000:]
    
    save_transactions(transactions)
    
    # Обновляем частые переводы в банке
    if sender_id and receiver_id and amount > 0:
        bank_data = load_bank_data()
        sender_str = str(sender_id)
        
        if sender_str in bank_data:
            if receiver_id not in bank_data[sender_str]['frequent_transfers']:
                bank_data[sender_str]['frequent_transfers'][str(receiver_id)] = 0
            bank_data[sender_str]['frequent_transfers'][str(receiver_id)] += 1
            bank_data[sender_str]['transactions_count'] = bank_data[sender_str].get('transactions_count', 0) + 1
            save_bank_data(bank_data)

def get_frequent_transfer(user_id):
    """Получает самый частый перевод пользователя"""
    bank_data = load_bank_data()
    user_id_str = str(user_id)
    
    if user_id_str in bank_data:
        transfers = bank_data[user_id_str].get('frequent_transfers', {})
        if transfers:
            most_common = max(transfers.items(), key=lambda x: x[1])
            target_id = int(most_common[0])
            count = most_common[1]
            target_name = get_display_name(target_id)
            return target_name, count
    
    return "Нет данных", 0

def handle_currency_message(user_id, peer_id):
    """Обрабатывает сообщение для начисления валюты"""
    elite_data = load_elite_data()
    user_id_str = str(user_id)
    
    if user_id_str not in elite_data:
        elite_data[user_id_str] = {
            'cash': 0,
            'total_earned': 0,
            'messages_count': 0,
            'last_message_time': None
        }
    
    # Проверяем, чтобы нельзя было фармить слишком быстро
    current_time = datetime.now()
    last_message_time = elite_data[user_id_str].get('last_message_time')
    
    if last_message_time:
        last_time = datetime.fromisoformat(last_message_time)
        time_diff = (current_time - last_time).total_seconds()
        
        # Минимальный интервал между сообщениями - 30 секунд
        if time_diff < 30:
            return False
    
    # Начисляем валюту
    elite_data[user_id_str]['cash'] = elite_data[user_id_str].get('cash', 0) + CASH_PER_MESSAGE
    elite_data[user_id_str]['total_earned'] = elite_data[user_id_str].get('total_earned', 0) + CASH_PER_MESSAGE
    elite_data[user_id_str]['messages_count'] = elite_data[user_id_str].get('messages_count', 0) + 1
    elite_data[user_id_str]['last_message_time'] = current_time.isoformat()
    
    save_elite_data(elite_data)
    return True

# ========== ФУНКЦИИ ДЛЯ СЕССИЙ БАНКА ==========

def is_bank_session_active(user_id, peer_id):
    """Проверяет, активна ли сессия банка у пользователя"""
    sessions = load_bank_sessions()
    user_sessions = sessions.get(str(user_id), {})
    return user_sessions.get('active', False) and user_sessions.get('peer_id') == peer_id

def is_waiting_operation(user_id, peer_id):
    """Проверяет, ожидает ли пользователь операции"""
    operations = load_waiting_operations()
    user_ops = operations.get(str(user_id), {})
    return user_ops.get('waiting', False) and user_ops.get('peer_id') == peer_id

def activate_bank_session(user_id, peer_id):
    """Активирует сессию банка"""
    sessions = load_bank_sessions()
    if str(user_id) not in sessions:
        sessions[str(user_id)] = {}
    
    sessions[str(user_id)] = {
        'active': True,
        'peer_id': peer_id,
        'last_active': datetime.now().isoformat()
    }
    save_bank_sessions(sessions)

def set_waiting_operation(user_id, peer_id, operation_type):
    """Устанавливает ожидание операции"""
    operations = load_waiting_operations()
    operations[str(user_id)] = {
        'waiting': True,
        'peer_id': peer_id,
        'operation_type': operation_type,
        'started': datetime.now().isoformat()
    }
    save_waiting_operations(operations)

def deactivate_bank_session(user_id):
    """Деактивирует сессию банка"""
    sessions = load_bank_sessions()
    if str(user_id) in sessions:
        sessions[str(user_id)] = {
            'active': False,
            'peer_id': None,
            'last_active': datetime.now().isoformat()
        }
        save_bank_sessions(sessions)

def clear_waiting_operation(user_id):
    """Очищает ожидание операции"""
    operations = load_waiting_operations()
    if str(user_id) in operations:
        operations[str(user_id)] = {
            'waiting': False,
            'peer_id': None,
            'operation_type': None,
            'started': None
        }
        save_waiting_operations(operations)

def complete_bank_operation(user_id, peer_id, amount, operation_type):
    """Завершает операцию в банке и закрывает сессию"""
    cash_balance = get_user_balance(user_id)
    bank_balance = get_user_bank_balance(user_id)
    
    if operation_type == 'deposit':
        # Пополнение
        if cash_balance >= amount:
            if bank_balance + amount <= BANK_STORAGE_LIMIT:
                update_user_balance(user_id, -amount, is_bank=False)
                update_user_balance(user_id, amount, is_bank=True)
                add_transaction(user_id, None, amount, 'deposit')
                
                message = f"✅ Успешно положено {amount} Элитов в банк.\n"
                message += f"💵 Наличные: {cash_balance - amount} Элитов\n"
                message += f"🏦 В банке: {bank_balance + amount} Элитов\n\n"
                message += "🏦 *Банк закрыт. Для повторного открытия используйте команду ?bank*"
                
                vk.messages.send(
                    peer_id=peer_id,
                    message=message,
                    random_id=random.randint(1, 2147483647)
                )
                
                # Закрываем сессию
                deactivate_bank_session(user_id)
                clear_waiting_operation(user_id)
                return True
            else:
                message = f"❌ Превышен лимит банка ({BANK_STORAGE_LIMIT} Элитов).\n"
                message += f"🏦 Текущий баланс: {bank_balance} Элитов\n"
                message += f"💵 Можно положить: {BANK_STORAGE_LIMIT - bank_balance} Элитов\n\n"
                message += "🏦 *Банк закрыт. Для повторного открытия используйте команду ?bank*"
                
                vk.messages.send(
                    peer_id=peer_id,
                    message=message,
                    random_id=random.randint(1, 2147483647)
                )
                
                # Закрываем сессию
                deactivate_bank_session(user_id)
                clear_waiting_operation(user_id)
                return True
        else:
            message = f"❌ Недостаточно наличных для пополнения.\n"
            message += f"💵 Наличные: {cash_balance} Элитов\n"
            message += f"🏦 В банке: {bank_balance} Элитов\n\n"
            message += "🏦 *Банк закрыт. Для повторного открытия используйте команду ?bank*"
            
            vk.messages.send(
                peer_id=peer_id,
                message=message,
                random_id=random.randint(1, 2147483647)
            )
            
            # Закрываем сессию
            deactivate_bank_session(user_id)
            clear_waiting_operation(user_id)
            return True
    
    elif operation_type == 'withdraw':
        # Снятие
        if bank_balance >= amount:
            update_user_balance(user_id, -amount, is_bank=True)
            update_user_balance(user_id, amount, is_bank=False)
            add_transaction(None, user_id, amount, 'withdraw')
            
            message = f"✅ Успешно снято {amount} Элитов из банка.\n"
            message += f"💵 Наличные: {cash_balance + amount} Элитов\n"
            message += f"🏦 В банке: {bank_balance - amount} Элитов\n\n"
            message += "🏦 *Банк закрыт. Для повторного открытия используйте команду ?bank*"
            
            vk.messages.send(
                peer_id=peer_id,
                message=message,
                random_id=random.randint(1, 2147483647)
            )
            
            # Закрываем сессию
            deactivate_bank_session(user_id)
            clear_waiting_operation(user_id)
            return True
        else:
            message = f"❌ Недостаточно средств в банке для снятия.\n"
            message += f"💵 Наличные: {cash_balance} Элитов\n"
            message += f"🏦 В банке: {bank_balance} Элитов\n\n"
            message += "🏦 *Банк закрыт. Для повторного открытия используйте команду ?bank*"
            
            vk.messages.send(
                peer_id=peer_id,
                message=message,
                random_id=random.randint(1, 2147483647)
            )
            
            # Закрываем сессию
            deactivate_bank_session(user_id)
            clear_waiting_operation(user_id)
            return True
    
    return False

# ========== КЛАВИАТУРЫ БАНКА ==========

def create_bank_keyboard(user_id, section="main", page=1):
    """Создает клавиатуру для банка"""
    if section == "main":
        keyboard = {
            "inline": True,
            "buttons": [
                [
                    {
                        "action": {
                            "type": "callback",
                            "label": "💰 Личное хранилище",
                            "payload": json.dumps({"action": "bank_storage", "user_id": user_id})
                        },
                        "color": "positive"
                    }
                ],
                [
                    {
                        "action": {
                            "type": "callback",
                            "label": "📊 Транзакции",
                            "payload": json.dumps({"action": "bank_transactions", "user_id": user_id, "page": 1})
                        },
                        "color": "primary"
                    }
                ],
                [
                    {
                        "action": {
                            "type": "callback",
                            "label": "❌ Закрыть банк",
                            "payload": json.dumps({"action": "close_bank", "user_id": user_id})
                        },
                        "color": "negative"
                    }
                ]
            ]
        }
        return keyboard
    
    elif section == "storage":
        keyboard = {
            "inline": True,
            "buttons": [
                [
                    {
                        "action": {
                            "type": "callback",
                            "label": "💵 Снять",
                            "payload": json.dumps({"action": "bank_withdraw", "user_id": user_id})
                        },
                        "color": "positive"
                    },
                    {
                        "action": {
                            "type": "callback",
                            "label": "💳 Положить",
                            "payload": json.dumps({"action": "bank_deposit", "user_id": user_id})
                        },
                        "color": "primary"
                    }
                ],
                [
                    {
                        "action": {
                            "type": "callback",
                            "label": "⬅️ Назад",
                            "payload": json.dumps({"action": "bank_main", "user_id": user_id})
                        },
                        "color": "secondary"
                    }
                ]
            ]
        }
        return keyboard
    
    elif section == "transactions":
        transactions = load_transactions()
        user_transactions = [t for t in transactions if t['sender_id'] == user_id or t['receiver_id'] == user_id]
        total_pages = (len(user_transactions) + 9) // 10  # 10 транзакций на страницу
        
        buttons = []
        
        # Пагинация
        if total_pages > 1:
            pagination_row = []
            
            if page > 1:
                pagination_row.append({
                    "action": {
                        "type": "callback",
                        "label": "⬅️",
                        "payload": json.dumps({"action": "bank_transactions", "user_id": user_id, "page": page - 1})
                    },
                    "color": "primary"
                })
            
            pagination_row.append({
                "action": {
                    "type": "text",
                    "label": f"{page}/{total_pages}",
                    "payload": "{}"
                },
                "color": "secondary"
            })
            
            if page < total_pages:
                pagination_row.append({
                    "action": {
                        "type": "callback",
                        "label": "➡️",
                        "payload": json.dumps({"action": "bank_transactions", "user_id": user_id, "page": page + 1})
                    },
                    "color": "primary"
                })
            
            buttons.append(pagination_row)
        
        buttons.append([
            {
                "action": {
                    "type": "callback",
                    "label": "⬅️ Назад",
                    "payload": json.dumps({"action": "bank_main", "user_id": user_id})
                },
                "color": "secondary"
            }
        ])
        
        keyboard = {"inline": True, "buttons": buttons}
        return keyboard

# ========== ОТПРАВКА СООБЩЕНИЙ БАНКА ==========

# ========== ОТПРАВКА СООБЩЕНИЙ БАНКА ==========

# ========== ОТПРАВКА СООБЩЕНИЙ БАНКА ==========

def send_bank_message(peer_id, user_id, section="main", edit_message_id=None, page=1):
    """Отправляет или редактирует сообщение банка (как инвентарь)"""
    # Получаем данные для сообщения
    cash_balance = get_user_balance(user_id)
    bank_balance = get_user_bank_balance(user_id)
    display_name = get_display_name(user_id)
    
    if section == "main":
        message = f"🏦 Elite Bank\n\n"
        message += f"👤 Владелец: [id{user_id}|{display_name}]\n"
        message += f"💰 Наличные: {cash_balance} Элитов\n"
        message += f"🏦 В банке: {bank_balance} Элитов\n"
        message += f"📊 Лимит хранилища: {BANK_STORAGE_LIMIT} Элитов\n\n"
        message += "Выберите раздел:"
    
    elif section == "storage":
        bank_data = load_bank_data()
        user_id_str = str(user_id)
        
        transactions_count = 0
        frequent_target = "Нет данных"
        frequent_count = 0
        
        if user_id_str in bank_data:
            transactions_count = bank_data[user_id_str].get('transactions_count', 0)
            frequent_target, frequent_count = get_frequent_transfer(user_id)
        
        message = f"💰 *Личное хранилище*\n\n"
        message += f"💵 Наличные: {cash_balance} Элитов\n"
        message += f"🏦 В банке: {bank_balance} Элитов\n"
        message += f"📈 Кол-во транзакций: {transactions_count}\n"
        message += f"🔄 Постоянный перевод: {frequent_target} ({frequent_count} раз)\n\n"
        message += "Выберите действие:"
    
    elif section == "transactions":
        transactions = load_transactions()
        user_transactions = [t for t in transactions if t['sender_id'] == user_id or t['receiver_id'] == user_id]
        
        # Пагинация
        items_per_page = 10
        total_pages = (len(user_transactions) + items_per_page - 1) // items_per_page
        start_idx = (page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, len(user_transactions))
        
        message = f"📊 *Транзакции* (страница {page}/{total_pages if total_pages > 0 else 1})\n\n"
        
        if user_transactions and start_idx < len(user_transactions):
            for i, trans in enumerate(user_transactions[start_idx:end_idx], start_idx + 1):
                time_str = datetime.fromisoformat(trans['timestamp']).strftime('%d.%m %H:%M')
                amount = trans['amount']
                
                if trans['sender_id'] == user_id:
                    # Исходящий перевод
                    message += f"🔻 {time_str} → {trans['receiver_name']}: {amount} Элитов\n"
                else:
                    # Входящий перевод
                    message += f"🟢 {time_str} ← {trans['sender_name']}: {amount} Элитов\n"
        else:
            message += "📭 История транзакций пуста\n"
        
        message += "\nИспользуйте кнопки для навигации:"
    
    try:
        keyboard = create_bank_keyboard(user_id, section, page)
        keyboard_json = json.dumps(keyboard)
        
        if edit_message_id:
            # Редактируем существующее сообщение (как в инвентаре)
            try:
                vk.messages.edit(
                    peer_id=peer_id,
                    message_id=edit_message_id,
                    message=message,
                    keyboard=keyboard_json
                )
                print(f"✓ Сообщение банка отредактировано: {section}, страница {page}")
            except Exception as e:
                print(f"✗ Ошибка редактирования сообщения банка: {e}")
                # Если не удалось отредактировать, удаляем старое и отправляем новое
                try:
                    vk.messages.delete(
                        delete_for_all=1,
                        peer_id=peer_id,
                        cmids=edit_message_id
                    )
                except:
                    pass
                
                # Отправляем новое сообщение
                try:
                    # Пробуем отправить с фотографией только при первом открытии банка
                    if section == "main":
                        try:
                            upload = vk_api.VkUpload(vk_session)
                            # Пробуем разные пути к файлу
                            photo_paths = [
                                'uploads/bank.jpg',
                                'bank.jpg',
                                './uploads/bank.jpg',
                                './bank.jpg'
                            ]
                            
                            photo = None
                            for photo_path in photo_paths:
                                try:
                                    photo = upload.photo_messages(photo_path)[0]
                                    print(f"✓ Фото найдено по пути: {photo_path}")
                                    break
                                except Exception as path_error:
                                    continue
                            
                            if photo:
                                attachment = f"photo{photo['owner_id']}_{photo['id']}"
                                response = vk.messages.send(
                                    peer_id=peer_id,
                                    message=message,
                                    keyboard=keyboard_json,
                                    attachment=attachment,
                                    random_id=random.randint(1, 2147483647)
                                )
                                return response
                            else:
                                print("✗ Фото банка не найдено ни по одному из путей")
                                # Отправляем без фото
                                response = vk.messages.send(
                                    peer_id=peer_id,
                                    message=message,
                                    keyboard=keyboard_json,
                                    random_id=random.randint(1, 2147483647)
                                )
                                return response
                        except Exception as photo_error:
                            print(f"✗ Ошибка загрузки фото: {photo_error}")
                            # Если не удалось загрузить фото, отправляем без него
                            response = vk.messages.send(
                                peer_id=peer_id,
                                message=message,
                                keyboard=keyboard_json,
                                random_id=random.randint(1, 2147483647)
                            )
                            return response
                    else:
                        # Для других разделов отправляем без фото
                        response = vk.messages.send(
                            peer_id=peer_id,
                            message=message,
                            keyboard=keyboard_json,
                            random_id=random.randint(1, 2147483647)
                        )
                        return response
                except Exception as send_error:
                    print(f"✗ Ошибка отправки сообщения: {send_error}")
        else:
            # Отправляем новое сообщение (только при первом открытии банка)
            try:
                # Пробуем отправить с фотографией только при первом открытии банка
                if section == "main":
                    try:
                        upload = vk_api.VkUpload(vk_session)
                        # Пробуем разные пути к файлу
                        photo_paths = [
                            'uploads/bank.jpg',
                            'bank.jpg',
                            './uploads/bank.jpg',
                            './bank.jpg'
                        ]
                        
                        photo = None
                        for photo_path in photo_paths:
                            try:
                                photo = upload.photo_messages(photo_path)[0]
                                print(f"✓ Фото найдено по пути: {photo_path}")
                                break
                            except Exception as path_error:
                                continue
                        
                        if photo:
                            attachment = f"photo{photo['owner_id']}_{photo['id']}"
                            response = vk.messages.send(
                                peer_id=peer_id,
                                message=message,
                                keyboard=keyboard_json,
                                attachment=attachment,
                                random_id=random.randint(1, 2147483647)
                            )
                            print(f"✓ Сообщение банка с фото отправлено")
                            return response
                        else:
                            print("✗ Фото банка не найдено ни по одному из путей")
                            # Отправляем без фото
                            response = vk.messages.send(
                                peer_id=peer_id,
                                message=message,
                                keyboard=keyboard_json,
                                random_id=random.randint(1, 2147483647)
                            )
                            return response
                    except Exception as photo_error:
                        print(f"✗ Ошибка загрузки фото: {photo_error}")
                        # Если не удалось загрузить фото, отправляем без него
                        response = vk.messages.send(
                            peer_id=peer_id,
                            message=message,
                            keyboard=keyboard_json,
                            random_id=random.randint(1, 2147483647)
                        )
                        return response
                else:
                    # Для других разделов отправляем без фото
                    response = vk.messages.send(
                        peer_id=peer_id,
                        message=message,
                        keyboard=keyboard_json,
                        random_id=random.randint(1, 2147483647)
                    )
                    return response
            except Exception as e:
                print(f"✗ Ошибка отправки сообщения банка: {e}")
                return None
    except Exception as e:
        print(f"✗ Ошибка создания клавиатуры банка: {e}")
        return None

# ========== ФУНКЦИИ ДЛЯ НИКНЕЙМОВ ==========

def set_nickname(user_id, nickname):
    """Устанавливает никнейм пользователю"""
    nicknames = load_nicknames()
    user_id_str = str(user_id)
    
    # Проверяем, не занят ли никнейм
    for uid, nick in nicknames.items():
        if nick == nickname and uid != user_id_str:
            return False, "Этот никнейм уже занят"
    
    old_nickname = nicknames.get(user_id_str)
    nicknames[user_id_str] = nickname
    save_nicknames(nicknames)
    
    return True, old_nickname

def reset_nickname(user_id):
    """Сбрасывает никнейм пользователя"""
    nicknames = load_nicknames()
    user_id_str = str(user_id)
    
    if user_id_str in nicknames:
        old_nickname = nicknames[user_id_str]
        del nicknames[user_id_str]
        save_nicknames(nicknames)
        return True, old_nickname
    
    return False, None

def get_all_nicknames():
    """Получает все никнеймы"""
    nicknames = load_nicknames()
    result = []
    
    for user_id, nickname in nicknames.items():
        user_name = get_user_name(int(user_id))
        result.append(f"{nickname} - {user_name}")
    
    return result

def create_case_keyboard(item_id, item_type='case'):
    if item_type == 'case':
        keyboard = {
            "inline": True,
            "buttons": [
                [
                    {
                        "action": {
                            "type": "callback",
                            "label": "🎁 Открыть",
                            "payload": json.dumps({"action": "open_case", "case_id": item_id})
                        },
                        "color": "positive"
                    },
                    {
                        "action": {
                            "type": "callback",
                            "label": "📦 В инвентарь",
                            "payload": json.dumps({"action": "to_inventory", "case_id": item_id})
                        },
                        "color": "primary"
                    }
                ],
                [
                    {
                        "action": {
                            "type": "callback",
                            "label": "🎀 Подарить",
                            "payload": json.dumps({"action": "gift_case", "case_id": item_id})
                        },
                        "color": "secondary"
                    }
                ]
            ]
        }
    else:  # subscription
        keyboard = {
            "inline": True,
            "buttons": [
                [
                    {
                        "action": {
                            "type": "callback",
                            "label": "⭐ Использовать",
                            "payload": json.dumps({"action": "open_subscription", "sub_id": item_id})
                        },
                        "color": "positive"
                    },
                    {
                        "action": {
                            "type": "callback",
                            "label": "📦 В инвентарь",
                            "payload": json.dumps({"action": "to_inventory_sub", "sub_id": item_id})
                        },
                        "color": "primary"
                    }
                ],
                [
                    {
                        "action": {
                            "type": "callback",
                            "label": "🎀 Подарить",
                            "payload": json.dumps({"action": "gift_subscription", "sub_id": item_id})
                        },
                        "color": "secondary"
                    }
                ]
            ]
        }
    return keyboard

def create_inventory_keyboard(user_id, section="main", page=1):
    inventory = load_inventory()
    user_inv = inventory.get(str(user_id), {})
    
    if section == "main":
        keyboard = {
            "inline": True,
            "buttons": [
                [
                    {
                        "action": {
                            "type": "callback",
                            "label": "🎁 Кейсы",
                            "payload": json.dumps({"action": "inv_section", "section": "cases", "user_id": user_id, "page": 1})
                        },
                        "color": "positive"
                    }
                ],
                [
                    {
                        "action": {
                            "type": "callback",
                            "label": "⭐ Подписки",
                            "payload": json.dumps({"action": "inv_section", "section": "subscriptions", "user_id": user_id, "page": 1})
                        },
                        "color": "primary"
                    }
                ],
                [
                    {
                        "action": {
                            "type": "callback",
                            "label": "📦 Прочее",
                            "payload": json.dumps({"action": "inv_section", "section": "other", "user_id": user_id, "page": 1})
                        },
                        "color": "secondary"
                    }
                ],
                [
                    {
                        "action": {
                            "type": "callback",
                            "label": "❌ Закрыть",
                            "payload": json.dumps({"action": "close_inventory", "user_id": user_id})
                        },
                        "color": "negative"
                    }
                ]
            ]
        }
        return keyboard
    
    elif section == "cases":
        cases_list = user_inv.get('cases', [])
        total_cases = len(cases_list)
        items_per_page = 3
        
        total_pages = (total_cases + items_per_page - 1) // items_per_page if total_cases > 0 else 1
        start_idx = (page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_cases)
        
        buttons = []
        
        if cases_list and start_idx < total_cases:
            for case in cases_list[start_idx:end_idx]:
                case_data = case.get('data', {})
                case_type = case_data.get('type', 'ng')
                case_type_name = get_case_type_name(case_type)
                case_id = case['id']
                
                row = [
                    {
                        "action": {
                            "type": "callback",
                            "label": f"🎁 {case_type_name}",
                            "payload": json.dumps({"action": "use_case_from_inv", "case_id": case_id, "user_id": user_id, "page": page})
                        },
                        "color": "positive"
                    },
                    {
                        "action": {
                            "type": "callback",
                            "label": "🎀 Подарить",
                            "payload": json.dumps({"action": "gift_case_from_inv", "case_id": case_id, "user_id": user_id, "page": page})
                        },
                        "color": "secondary"
                    }
                ]
                buttons.append(row)
        else:
            buttons.append([
                {
                    "action": {
                        "type": "text",
                        "label": "📭 Пусто",
                        "payload": "{}"
                    },
                    "color": "secondary"
                }
            ])
        
        # Пагинация - только если есть больше 1 страницы
        if total_pages > 1:
            pagination_row = []
            
            if page > 1:
                pagination_row.append({
                    "action": {
                        "type": "callback",
                        "label": "⬅️ Назад",
                        "payload": json.dumps({"action": "inv_section", "section": "cases", "user_id": user_id, "page": page - 1})
                    },
                    "color": "primary"
                })
            
            pagination_row.append({
                "action": {
                    "type": "callback",
                    "label": f"{page}/{total_pages}",
                    "payload": json.dumps({"action": "inv_section", "section": "cases", "user_id": user_id, "page": page})
                },
                "color": "secondary"
            })
            
            if page < total_pages:
                pagination_row.append({
                    "action": {
                        "type": "callback",
                        "label": "➡️ Вперед",
                        "payload": json.dumps({"action": "inv_section", "section": "cases", "user_id": user_id, "page": page + 1})
                    },
                    "color": "primary"
                })
            
            if pagination_row:
                buttons.append(pagination_row)
        
        buttons.append([
            {
                "action": {
                    "type": "callback",
                    "label": "⬅️ В главное",
                    "payload": json.dumps({"action": "inv_section", "section": "main", "user_id": user_id, "page": 1})
                },
                "color": "primary"
            }
        ])
        
        keyboard = {"inline": True, "buttons": buttons}
        return keyboard
    
    elif section == "subscriptions":
        subs_list = user_inv.get('subscriptions', [])
        total_subs = len(subs_list)
        items_per_page = 3
        
        total_pages = (total_subs + items_per_page - 1) // items_per_page if total_subs > 0 else 1
        start_idx = (page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_subs)
        
        buttons = []
        
        if subs_list and start_idx < total_subs:
            for sub in subs_list[start_idx:end_idx]:
                sub_data = sub.get('data', {})
                sub_name = sub_data.get('subscription_name', 'Подписка')
                sub_id = sub['id']
                
                row = [
                    {
                        "action": {
                            "type": "callback",
                            "label": f"⭐ {sub_name}",
                            "payload": json.dumps({"action": "use_sub_from_inv", "sub_id": sub_id, "user_id": user_id, "page": page})
                        },
                        "color": "positive"
                    },
                    {
                        "action": {
                            "type": "callback",
                            "label": "🎀 Подарить",
                            "payload": json.dumps({"action": "gift_sub_from_inv", "sub_id": sub_id, "user_id": user_id, "page": page})
                        },
                        "color": "secondary"
                    }
                ]
                buttons.append(row)
        else:
            buttons.append([
                {
                    "action": {
                        "type": "text",
                        "label": "📭 Пусто",
                        "payload": "{}"
                    },
                    "color": "secondary"
                }
            ])
        
        # Пагинация
        if total_pages > 1:
            pagination_row = []
            
            if page > 1:
                pagination_row.append({
                    "action": {
                        "type": "callback",
                        "label": "⬅️ Назад",
                        "payload": json.dumps({"action": "inv_section", "section": "subscriptions", "user_id": user_id, "page": page - 1})
                    },
                    "color": "primary"
                })
            
            pagination_row.append({
                "action": {
                    "type": "callback",
                    "label": f"{page}/{total_pages}",
                    "payload": json.dumps({"action": "inv_section", "section": "subscriptions", "user_id": user_id, "page": page})
                },
                "color": "secondary"
            })
            
            if page < total_pages:
                pagination_row.append({
                    "action": {
                        "type": "callback",
                        "label": "➡️ Вперед",
                        "payload": json.dumps({"action": "inv_section", "section": "subscriptions", "user_id": user_id, "page": page + 1})
                    },
                    "color": "primary"
                })
            
            if pagination_row:
                buttons.append(pagination_row)
        
        buttons.append([
            {
                "action": {
                    "type": "callback",
                    "label": "⬅️ В главное",
                    "payload": json.dumps({"action": "inv_section", "section": "main", "user_id": user_id, "page": 1})
                },
                "color": "primary"
            }
        ])
        
        keyboard = {"inline": True, "buttons": buttons}
        return keyboard
    
    elif section == "other":
        other_list = user_inv.get('other', [])
        buttons = []
        
        if other_list:
            for item in other_list[:5]:
                buttons.append([
                    {
                        "action": {
                            "type": "callback",
                            "label": f"📦 {item.get('data', {}).get('name', 'Предмет')}",
                            "payload": json.dumps({"action": "use_item", "item_type": "other", "item_id": item['id'], "user_id": user_id})
                        },
                        "color": "secondary"
                    }
                ])
        else:
            buttons.append([
                {
                    "action": {
                        "type": "text",
                        "label": "📭 Пусто",
                        "payload": "{}"
                    },
                    "color": "secondary"
                }
            ])
        
        buttons.append([
            {
                "action": {
                    "type": "callback",
                    "label": "⬅️ В главное",
                    "payload": json.dumps({"action": "inv_section", "section": "main", "user_id": user_id, "page": 1})
                },
                "color": "primary"
            }
        ])
        
        keyboard = {"inline": True, "buttons": buttons}
        return keyboard
    
    return {
        "inline": True,
        "buttons": [
            [
                {
                    "action": {
                        "type": "callback",
                        "label": "⬅️ В главное",
                        "payload": json.dumps({"action": "inv_section", "section": "main", "user_id": user_id, "page": 1})
                    },
                    "color": "primary"
                }
            ]
        ]
    }

def delete_message(peer_id, message_id):
    try:
        vk.messages.delete(
            delete_for_all=1,
            peer_id=peer_id,
            cmids=message_id
        )
        print(f"✓ Сообщение {message_id} удалено")
        return True
    except Exception as e:
        print(f"✗ Ошибка удаления сообщения {message_id}: {e}")
        return False

def send_new_message_with_prize(peer_id, user_id, prize, duration, item_type="case"):
    recipient_name = get_user_name(user_id)
    
    if item_type == "case":
        message = f"[id{user_id}|{recipient_name}] Вы успешно открыли кейс\n\n📦 Содержимое: {prize['name']}\n⏰ Срок: {duration}\n🔍 Проверить: !роль"
    else:  # subscription
        message = f"[id{user_id}|{recipient_name}] Вы успешно использовали подписку\n\n⭐ Подписка: {prize['name']}\n⏰ Срок: {duration}\n🔍 Проверить: !роль"
    
    vk.messages.send(
        peer_id=peer_id,
        message=message,
        random_id=random.randint(1, 2147483647)
    )
    
    try:
        user_info = vk.users.get(user_ids=user_id, fields='screen_name')[0]
        username = user_info.get('screen_name', f'id{user_id}')
        send_to_archive(f"роль @{username} {prize['id']}")
    except:
        send_to_archive(f"роль @id{user_id} {prize['id']}")
    
    if duration != 'навсегда':
        add_expiring_prize(user_id, prize['id'], duration)

def add_to_inventory(user_id, item_type, item_data):
    inventory = load_inventory()
    
    if str(user_id) not in inventory:
        inventory[str(user_id)] = {
            'cases': [],
            'subscriptions': [],
            'other': []
        }
    
    item_id = random.randint(1000, 9999)
    item = {
        'id': item_id,
        'type': item_type,
        'data': item_data,
        'added_date': datetime.now().isoformat()
    }
    
    if item_type == 'case':
        inventory[str(user_id)]['cases'].append(item)
    elif item_type == 'subscription':
        inventory[str(user_id)]['subscriptions'].append(item)
    elif item_type == 'other':
        inventory[str(user_id)]['other'].append(item)
    
    save_inventory(inventory)
    print(f"✓ Предмет добавлен в инвентарь пользователя {user_id}: {item_type}")
    return item_id

def remove_from_inventory(user_id, item_type, item_id):
    inventory = load_inventory()
    
    if str(user_id) not in inventory:
        return False
    
    if item_type == 'case':
        items = inventory[str(user_id)]['cases']
    elif item_type == 'subscription':
        items = inventory[str(user_id)]['subscriptions']
    elif item_type == 'other':
        items = inventory[str(user_id)]['other']
    else:
        return False
    
    for i, item in enumerate(items):
        if item['id'] == item_id:
            del items[i]
            save_inventory(inventory)
            print(f"✓ Предмет удален из инвентаря пользователя {user_id}: {item_type} ID {item_id}")
            return True
    
    return False

def send_inventory_message(peer_id, user_id, section="main", edit_message_id=None, page=1):
    inventory = load_inventory()
    user_inv = inventory.get(str(user_id), {})
    
    if section == "main":
        cases_count = len(user_inv.get('cases', []))
        subs_count = len(user_inv.get('subscriptions', []))
        other_count = len(user_inv.get('other', []))
        
        message = f"📦 *Инвентарь [id{user_id}|{get_user_name(user_id)}]*\n\n"
        message += f"🎁 Кейсы: {cases_count}\n"
        message += f"⭐ Подписки: {subs_count}\n"
        message += f"📦 Прочее: {other_count}\n\n"
        message += "Выберите раздел:"
    
    elif section == "cases":
        cases_list = user_inv.get('cases', [])
        total_cases = len(cases_list)
        items_per_page = 3
        total_pages = (total_cases + items_per_page - 1) // items_per_page if total_cases > 0 else 1
        start_idx = (page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_cases)
        
        message = f"🎁 *Кейсы в инвентаре* (страница {page}/{total_pages})\n\n"
        
        if cases_list and start_idx < total_cases:
            for i, case in enumerate(cases_list[start_idx:end_idx], start_idx + 1):
                case_data = case.get('data', {})
                case_type = case_data.get('type', 'ng')
                case_type_name = get_case_type_name(case_type)
                message += f"{i}. {case_type_name} кейс\n"
        else:
            message += "📭 Кейсов нет в инвентаре\n"
        
        message += "\nВыберите действие:"
    
    elif section == "subscriptions":
        subs_list = user_inv.get('subscriptions', [])
        total_subs = len(subs_list)
        items_per_page = 3
        total_pages = (total_subs + items_per_page - 1) // items_per_page if total_subs > 0 else 1
        start_idx = (page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_subs)
        
        message = f"⭐ *Подписки в инвентаре* (страница {page}/{total_pages})\n\n"
        
        if subs_list and start_idx < total_subs:
            for i, sub in enumerate(subs_list[start_idx:end_idx], start_idx + 1):
                sub_data = sub.get('data', {})
                sub_name = sub_data.get('subscription_name', 'Подписка')
                duration = sub_data.get('duration', 'Не указано')
                message += f"{i}. {sub_name} ({duration})\n"
        else:
            message += "📭 Подписок нет в инвентаре\n"
        
        message += "\nВыберите действие:"
    
    elif section == "other":
        other_list = user_inv.get('other', [])
        message = f"📦 *Прочие предметы*\n\n"
        
        if other_list:
            for i, item in enumerate(other_list[:5], 1):
                item_name = item.get('data', {}).get('name', 'Неизвестно')
                message += f"{i}. {item_name}\n"
        else:
            message += "📭 Предметов нет\n"
        
        message += "\nВыберите предмет:"
    
    try:
        keyboard = create_inventory_keyboard(user_id, section, page)
        
        if len(keyboard.get('buttons', [])) > 10:
            keyboard = {
                "inline": True,
                "buttons": [
                    [
                        {
                            "action": {
                                "type": "callback",
                                "label": "⚠️ Упростить",
                                "payload": json.dumps({"action": "inv_section", "section": "main", "user_id": user_id, "page": 1})
                            },
                            "color": "primary"
                        }
                    ]
                ]
            }
            message = "⚠️ Слишком много предметов для отображения. Пожалуйста, используйте другую страницу.\n\n" + message
    except Exception as e:
        print(f"✗ Ошибка создания клавиатуры: {e}")
        keyboard = {
            "inline": True,
            "buttons": [
                [
                    {
                        "action": {
                            "type": "callback",
                            "label": "⬅️ В главное",
                            "payload": json.dumps({"action": "inv_section", "section": "main", "user_id": user_id, "page": 1})
                        },
                        "color": "primary"
                    }
                ]
            ]
        }
    
    keyboard_json = json.dumps(keyboard)
    
    if edit_message_id:
        try:
            vk.messages.edit(
                peer_id=peer_id,
                message_id=edit_message_id,
                message=message,
                keyboard=keyboard_json
            )
            print(f"✓ Сообщение инвентаря отредактировано: {section}, страница {page}")
        except Exception as e:
            print(f"✗ Ошибка редактирования сообщения инвентаря: {e}")
            try:
                vk.messages.send(
                    peer_id=peer_id,
                    message=message,
                    keyboard=keyboard_json,
                    random_id=random.randint(1, 2147483647)
                )
                try:
                    delete_message(peer_id, edit_message_id)
                except:
                    pass
            except Exception as send_error:
                print(f"✗ Ошибка отправки сообщения: {send_error}")
    else:
        try:
            vk.messages.send(
                peer_id=peer_id,
                message=message,
                keyboard=keyboard_json,
                random_id=random.randint(1, 2147483647)
            )
        except Exception as e:
            print(f"✗ Ошибка отправки сообщения инвентаря: {e}")

# ========== ОСНОВНАЯ ОБРАБОТКА КОМАНД ==========

def handle_command(event):
    chats = load_chats()
    if event.peer_id not in [chats.get('archive'), chats.get('normal'), chats.get('test'), chats.get('test2')]:
        return
        
    text = event.text
    user_id = event.from_id
    peer_id = event.peer_id
    
    is_archive = peer_id == chats.get('archive')
    
    # ========== НОВЫЕ КОМАНДЫ БАНКА И ВАЛЮТЫ ==========
    
    # Команда банка
    if text == '?bank':
        bank_data = load_bank_data()
        user_id_str = str(user_id)
        
        if user_id_str not in bank_data:
            bank_data[user_id_str] = {
                'balance': 0,
                'transactions_count': 0,
                'frequent_transfers': {},
                'created_at': datetime.now().isoformat()
            }
            save_bank_data(bank_data)
        
        # Активируем сессию банка
        activate_bank_session(user_id, peer_id)
        
        # Очищаем ожидающую операцию (если есть)
        clear_waiting_operation(user_id)
        
        # Отправляем сообщение банка
        send_bank_message(peer_id, user_id, "main")
        return
    
    # Команда перевода валюты
    if text.startswith('?pay'):
        parts = event.text.split()
        if len(parts) < 3:
            vk.messages.send(
                peer_id=peer_id,
                message="❌ Использование: ?pay @username сумма\nПример: ?pay @id123456 100",
                random_id=random.randint(1, 2147483647)
            )
            return
        
        mention = parts[1]
        try:
            amount = int(parts[2])
        except:
            vk.messages.send(
                peer_id=peer_id,
                message="❌ Неверная сумма. Введите целое число.",
                random_id=random.randint(1, 2147483647)
            )
            return
        
        if amount <= 0:
            vk.messages.send(
                peer_id=peer_id,
                message="❌ Сумма должна быть положительной.",
                random_id=random.randint(1, 2147483647)
            )
            return
        
        # Определяем ID получателя
        recipient_id = None
        if mention.startswith('[id') and '|' in mention:
            recipient_id = int(mention.split('|')[0][3:])
        elif mention.startswith('@'):
            try:
                user_info = vk.users.get(user_ids=mention[1:])[0]
                recipient_id = user_info['id']
            except:
                vk.messages.send(
                    peer_id=peer_id,
                    message="❌ Пользователь не найден.",
                    random_id=random.randint(1, 2147483647)
                )
                return
        else:
            try:
                recipient_id = int(mention)
            except:
                vk.messages.send(
                    peer_id=peer_id,
                    message="❌ Неверный формат упоминания.",
                    random_id=random.randint(1, 2147483647)
                )
                return
        
        if recipient_id == user_id:
            vk.messages.send(
                peer_id=peer_id,
                message="❌ Нельзя перевести самому себе.",
                random_id=random.randint(1, 2147483647)
            )
            return
        
        # Проверяем баланс отправителя
        sender_balance = get_user_balance(user_id)
        if sender_balance < amount:
            vk.messages.send(
                peer_id=peer_id,
                message=f"❌ Недостаточно средств. У вас {sender_balance} Элитов.",
                random_id=random.randint(1, 2147483647)
            )
            return
        
        # Проверяем, находится ли получатель в чате
        try:
            chat_members = vk.messages.getConversationMembers(peer_id=peer_id)['items']
            in_chat = any(member['member_id'] == recipient_id for member in chat_members)
            if not in_chat:
                vk.messages.send(
                    peer_id=peer_id,
                    message="❌ Получатель не найден в чате.",
                    random_id=random.randint(1, 2147483647)
                )
                return
        except:
            pass
        
        # Выполняем перевод
        update_user_balance(user_id, -amount, is_bank=False)
        update_user_balance(recipient_id, amount, is_bank=False)
        add_transaction(user_id, recipient_id, amount, 'transfer')
        
        # Отправляем сообщение о переводе
        sender_name = get_display_name(user_id)
        recipient_name = get_display_name(recipient_id)
        
        message = f"💸 @id{user_id} ({sender_name}) перевел @id{recipient_id} ({recipient_name}) {amount} Элитов"
        vk.messages.send(
            peer_id=peer_id,
            message=message,
            random_id=random.randint(1, 2147483647)
        )
        return
    
    # Команда просмотра баланса (ИСПРАВЛЕНА - только наличные)
    if text.lower() == 'элиты':
        cash_balance = get_user_balance(user_id)
        display_name = get_display_name(user_id)
        
        message = f"💰 @id{user_id} ({display_name}), у тебя {cash_balance} Элитов"
        
        vk.messages.send(
            peer_id=peer_id,
            message=message,
            random_id=random.randint(1, 2147483647)
        )
        return
    
    # ========== КОМАНДЫ НИКНЕЙМОВ ==========
    
    # Установка никнейма
    if text.startswith('?nik '):
        parts = event.text.split(' ', 1)
        if len(parts) < 2:
            vk.messages.send(
                peer_id=peer_id,
                message="❌ Использование: ?nik ваш_никнейм",
                random_id=random.randint(1, 2147483647)
            )
            return
        
        nickname = parts[1].strip()
        if len(nickname) < 3:
            vk.messages.send(
                peer_id=peer_id,
                message="❌ Никнейм должен содержать минимум 3 символа.",
                random_id=random.randint(1, 2147483647)
            )
            return
        
        if len(nickname) > 20:
            vk.messages.send(
                peer_id=peer_id,
                message="❌ Никнейм не должен превышать 20 символов.",
                random_id=random.randint(1, 2147483647)
            )
            return
        
        success, old_nickname = set_nickname(user_id, nickname)
        if success:
            user_name = get_user_name(user_id)
            if old_nickname:
                message = f"✅ *{user_name}* ты теперь *{nickname}* (был {old_nickname})"
            else:
                message = f"✅ *{user_name}* ты теперь *{nickname}*"
        else:
            message = f"❌ {old_nickname}"  # old_nickname содержит сообщение об ошибке
        
        vk.messages.send(
            peer_id=peer_id,
            message=message,
            random_id=random.randint(1, 2147483647)
        )
        return
    
    # Просмотр текущего никнейма
    elif text == '?nik':
        nickname = get_nickname(user_id)
        user_name = get_user_name(user_id)
        
        if nickname:
            message = f"👤 Твой никнейм: *{nickname}*\n📝 Твое имя: {user_name}"
        else:
            message = f"📝 У тебя нет никнейма. Твое имя: {user_name}\nУстанови никнейм: ?nik ваш_никнейм"
        
        vk.messages.send(
            peer_id=peer_id,
            message=message,
            random_id=random.randint(1, 2147483647)
        )
        return
    
    # Сброс никнейма
    elif text == '?nik_reset':
        success, old_nickname = reset_nickname(user_id)
        user_name = get_user_name(user_id)
        
        if success:
            message = f"✅ *{old_nickname}* ты теперь *{user_name}*"
        else:
            message = f"ℹ️ У тебя не было установленного никнейма. Твое имя: {user_name}"
        
        vk.messages.send(
            peer_id=peer_id,
            message=message,
            random_id=random.randint(1, 2147483647)
        )
        return
    
    # Просмотр всех никнеймов
    elif text == '?niks':
        nicknames_list = get_all_nicknames()
        
        if nicknames_list:
            message = "📋 *Список никнеймов в чате:*\n\n"
            for item in nicknames_list:
                message += f"• {item}\n"
        else:
            message = "📭 В чате никто не установил никнеймы"
        
        vk.messages.send(
            peer_id=peer_id,
            message=message,
            random_id=random.randint(1, 2147483647)
        )
        return
    
    # ========== СТАРЫЕ КОМАНДЫ (ОСТАЮТСЯ БЕЗ ИЗМЕНЕНИЙ) ==========
    
    # Команда управления новогодними поздравлениями (ТОЛЬКО ДЛЯ АДМИНА)
    if text == '?ny_toggle' and user_id == DEVELOPER_ID:
        greetings = load_new_year_greetings()
        current_status = greetings.get('enabled', True)
        new_status = not current_status
        
        toggle_new_year_greetings(new_status)
        
        status_text = "включены" if new_status else "выключены"
        message = f"✅ Новогодние поздравления {status_text}!"
        
        if is_archive:
            user_session = vk_api.VkApi(token=os.getenv('VK_USER_TOKEN'))
            user_vk = user_session.get_api()
            user_vk.messages.send(peer_id=peer_id, message=message, random_id=random.randint(1, 2147483647))
        else:
            vk.messages.send(peer_id=peer_id, message=message, random_id=random.randint(1, 2147483647))
        return
    
    # Команда сброса новогодних поздравлений (ТОЛЬКО ДЛЯ АДМИНА)
    if text == '?ny_reset' and user_id == DEVELOPER_ID:
        greetings = load_new_year_greetings()
        greetings['last_greeting_date'] = None
        greetings['last_greeted_user'] = None
        save_new_year_greetings(greetings)
        
        message = "✅ Счетчик новогодних поздравлений сброшен! Теперь можно поздравлять пользователей заново."
        
        if is_archive:
            user_session = vk_api.VkApi(token=os.getenv('VK_USER_TOKEN'))
            user_vk = user_session.get_api()
            user_vk.messages.send(peer_id=peer_id, message=message, random_id=random.randint(1, 2147483647))
        else:
            vk.messages.send(peer_id=peer_id, message=message, random_id=random.randint(1, 2147483647))
        return
    
    # Команда проверки статуса новогодних поздравлений
    if text == '?ny_status':
        greetings = load_new_year_greetings()
        status = "включены" if greetings.get('enabled', True) else "выключены"
        last_date = greetings.get('last_greeting_date', 'никогда')
        last_user = greetings.get('last_greeted_user', 'никого')
        
        message = f"🎄 *Статус новогодних поздравлений*\n\n"
        message += f"📊 Статус: {status}\n"
        message += f"📅 Последнее поздравление: {last_date}\n"
        message += f"👤 Последний поздравленный: {last_user}\n"
        message += f"\n*Команды управления (только для админа):*\n"
        message += f"?ny_toggle - включить/выключить поздравления\n"
        message += f"?ny_reset - сбросить счетчик поздравлений"
        
        if is_archive:
            user_session = vk_api.VkApi(token=os.getenv('VK_USER_TOKEN'))
            user_vk = user_session.get_api()
            user_vk.messages.send(peer_id=peer_id, message=message, random_id=random.randint(1, 2147483647))
        else:
            vk.messages.send(peer_id=peer_id, message=message, random_id=random.randint(1, 2147483647))
        return
    
    # ?info
    if text == '?info':
        try:
            chat_info = vk.messages.getConversationsById(peer_ids=peer_id)['items'][0]['chat_settings']
            members_count = chat_info['members_count']
            title = chat_info['title']
            owner_id = chat_info.get('owner_id', 'Неизвестно')
            
            message = f"📊 *Информация о чате*\n\n📝 Название: {title}\n👥 Участников: {members_count}\n👑 Владелец: [id{owner_id}|@id{owner_id}]"
            
            if is_archive:
                user_session = vk_api.VkApi(token=os.getenv('VK_USER_TOKEN'))
                user_vk = user_session.get_api()
                user_vk.messages.send(peer_id=peer_id, message=message, random_id=random.randint(1, 2147483647))
            else:
                vk.messages.send(peer_id=peer_id, message=message, random_id=random.randint(1, 2147483647))
        except:
            pass
        return
    
    # ?chat_id
    if text == '?chat_id':
        message = f"🆔 *ID чата:* `{peer_id}`"
        
        if is_archive:
            user_session = vk_api.VkApi(token=os.getenv('VK_USER_TOKEN'))
            user_vk = user_session.get_api()
            user_vk.messages.send(peer_id=peer_id, message=message, random_id=random.randint(1, 2147483647))
        else:
            vk.messages.send(peer_id=peer_id, message=message, random_id=random.randint(1, 2147483647))
        return
    
    # ?profile
    if text.startswith('?profile'):
        parts = event.text.split()
        if len(parts) < 2:
            return
            
        mention = parts[1]
        target_id = None
        
        if mention.startswith('[id') and '|' in mention:
            target_id = int(mention.split('|')[0][3:])
        elif mention.startswith('@'):
            try:
                user_info = vk.users.get(user_ids=mention[1:])[0]
                target_id = user_info['id']
            except:
                return
        else:
            try:
                target_id = int(mention)
            except:
                return
        
        try:
            user_info = vk.users.get(
                user_ids=target_id,
                fields='screen_name,city,contacts,status,education,military,counters,last_seen'
            )[0]
            
            name = f"{user_info['first_name']} {user_info['last_name']}"
            username = user_info.get('screen_name', 'Нет')
            user_id_info = user_info['id']
            city = user_info.get('city', {}).get('title', 'Не указан') if isinstance(user_info.get('city'), dict) else 'Не указан'
            phone = user_info.get('mobile_phone', 'Скрыт')
            status = user_info.get('status', 'Нет статуса')
            
            education = 'Не указано'
            if 'education' in user_info and user_info['education'] and isinstance(user_info['education'], dict):
                edu = user_info['education']
                if 'university_name' in edu:
                    education = edu['university_name']
            
            military = 'Не указано'
            if 'military' in user_info and user_info['military'] and isinstance(user_info['military'], list):
                mil = user_info['military'][0] if user_info['military'] else {}
                if isinstance(mil, dict) and 'unit' in mil:
                    military = mil['unit']
            
            counters = user_info.get('counters', {})
            friends = counters.get('friends', 0) if isinstance(counters, dict) else 0
            followers = counters.get('followers', 0) if isinstance(counters, dict) else 0
            subscriptions = counters.get('subscriptions', 0) if isinstance(counters, dict) else 0
            groups = counters.get('groups', 0) if isinstance(counters, dict) else 0
            
            try:
                chat_members = vk.messages.getConversationMembers(peer_id=peer_id)['items']
                in_chat = any(member['member_id'] == target_id for member in chat_members)
                chat_status = "✅ В чате" if in_chat else "❌ Не в чате"
            except:
                chat_status = "❓ Неизвестно"
            
            message = f"""👤 *Профиль пользователя*

📝 Имя: {name}
🔗 Username: @{username}
🆔 ID: {user_id_info}
🏙 Город: {city}
📱 Номер: {phone}
💭 Статус: {status}
🎓 Образование: {education}
🪖 Военная служба: {military}
👥 Друзей: {friends}
👁 Подписчиков: {followers}
📺 Подписок: {subscriptions}
🏢 Сообществ: {groups}
💬 {chat_status}"""
            
            if is_archive:
                user_session = vk_api.VkApi(token=os.getenv('VK_USER_TOKEN'))
                user_vk = user_session.get_api()
                user_vk.messages.send(peer_id=peer_id, message=message, random_id=random.randint(1, 2147483647))
            else:
                vk.messages.send(peer_id=peer_id, message=message, random_id=random.randint(1, 2147483647))
        except:
            pass
        return
    
    # ?inv - инвентарь
    if text == '?inv':
        send_inventory_message(peer_id, user_id, "main")
        return
    
    # КОМАНДЫ ДЛЯ ВЫДАЧИ ПОДПИСОК
    if text.startswith('?vip') and user_id == DEVELOPER_ID:
        parts = event.text.split()
        if len(parts) < 2:
            return
            
        mention = parts[1]
        recipient_id = None
        
        if mention.startswith('[id') and '|' in mention:
            recipient_id = int(mention.split('|')[0][3:])
        elif mention.startswith('@'):
            try:
                user_info = vk.users.get(user_ids=mention[1:])[0]
                recipient_id = user_info['id']
            except:
                return
        else:
            try:
                recipient_id = int(mention)
            except:
                return
        
        duration = get_random_subscription_duration()
        subscription = create_subscription('vip', user_id, recipient_id, duration, from_admin=True)
        
        try:
            sender_name = get_user_name(user_id)
            recipient_name = get_user_name(recipient_id)
            
            message = f"[id{user_id}|Администратор] подарил подписку V.I.P [id{recipient_id}|{recipient_name}]\n⏰ Срок: {duration}"
            
            keyboard = create_case_keyboard(subscription['id'], 'subscription')
            
            response = vk.messages.send(
                peer_id=peer_id,
                message=message,
                keyboard=json.dumps(keyboard),
                random_id=random.randint(1, 2147483647)
            )
            
            subscription['message_id'] = response
            subscription['peer_id'] = peer_id
            subscription['conversation_message_id'] = response
            
            cases = load_cases()
            cases[str(subscription['id'])] = subscription
            save_cases(cases)
            
            print(f"✓ Создана подписка V.I.P ID {subscription['id']} от админа {user_id} для пользователя {recipient_id} на срок {duration}")
        except Exception as e:
            print(f"✗ Ошибка создания подписки: {e}")
        return
    
    if text.startswith('?premium') and user_id == DEVELOPER_ID:
        parts = event.text.split()
        if len(parts) < 2:
            return
            
        mention = parts[1]
        recipient_id = None
        
        if mention.startswith('[id') and '|' in mention:
            recipient_id = int(mention.split('|')[0][3:])
        elif mention.startswith('@'):
            try:
                user_info = vk.users.get(user_ids=mention[1:])[0]
                recipient_id = user_info['id']
            except:
                return
        else:
            try:
                recipient_id = int(mention)
            except:
                return
        
        duration = get_random_subscription_duration()
        subscription = create_subscription('premium', user_id, recipient_id, duration, from_admin=True)
        
        try:
            sender_name = get_user_name(user_id)
            recipient_name = get_user_name(recipient_id)
            
            message = f"[id{user_id}|Администратор] подарил подписку PREMIUM [id{recipient_id}|{recipient_name}]\n⏰ Срок: {duration}"
            
            keyboard = create_case_keyboard(subscription['id'], 'subscription')
            
            response = vk.messages.send(
                peer_id=peer_id,
                message=message,
                keyboard=json.dumps(keyboard),
                random_id=random.randint(1, 2147483647)
            )
            
            subscription['message_id'] = response
            subscription['peer_id'] = peer_id
            subscription['conversation_message_id'] = response
            
            cases = load_cases()
            cases[str(subscription['id'])] = subscription
            save_cases(cases)
            
            print(f"✓ Создана подписка PREMIUM ID {subscription['id']} от админа {user_id} для пользователя {recipient_id} на срок {duration}")
        except Exception as e:
            print(f"✗ Ошибка создания подписки: {e}")
        return
    
    if text.startswith('?deluxe') and user_id == DEVELOPER_ID:
        parts = event.text.split()
        if len(parts) < 2:
            return
            
        mention = parts[1]
        recipient_id = None
        
        if mention.startswith('[id') and '|' in mention:
            recipient_id = int(mention.split('|')[0][3:])
        elif mention.startswith('@'):
            try:
                user_info = vk.users.get(user_ids=mention[1:])[0]
                recipient_id = user_info['id']
            except:
                return
        else:
            try:
                recipient_id = int(mention)
            except:
                return
        
        duration = get_random_subscription_duration()
        subscription = create_subscription('deluxe', user_id, recipient_id, duration, from_admin=True)
        
        try:
            sender_name = get_user_name(user_id)
            recipient_name = get_user_name(recipient_id)
            
            message = f"[id{user_id}|Администратор] подарил подписку DELUXE [id{recipient_id}|{recipient_name}]\n⏰ Срок: {duration}"
            
            keyboard = create_case_keyboard(subscription['id'], 'subscription')
            
            response = vk.messages.send(
                peer_id=peer_id,
                message=message,
                keyboard=json.dumps(keyboard),
                random_id=random.randint(1, 2147483647)
            )
            
            subscription['message_id'] = response
            subscription['peer_id'] = peer_id
            subscription['conversation_message_id'] = response
            
            cases = load_cases()
            cases[str(subscription['id'])] = subscription
            save_cases(cases)
            
            print(f"✓ Создана подписка DELUXE ID {subscription['id']} от админа {user_id} для пользователя {recipient_id} на срок {duration}")
        except Exception as e:
            print(f"✗ Ошибка создания подписки: {e}")
        return
    
    if text.startswith('?luxe') and user_id == DEVELOPER_ID:
        parts = event.text.split()
        if len(parts) < 2:
            return
            
        mention = parts[1]
        recipient_id = None
        
        if mention.startswith('[id') and '|' in mention:
            recipient_id = int(mention.split('|')[0][3:])
        elif mention.startswith('@'):
            try:
                user_info = vk.users.get(user_ids=mention[1:])[0]
                recipient_id = user_info['id']
            except:
                return
        else:
            try:
                recipient_id = int(mention)
            except:
                return
        
        duration = get_random_subscription_duration()
        subscription = create_subscription('luxe', user_id, recipient_id, duration, from_admin=True)
        
        try:
            sender_name = get_user_name(user_id)
            recipient_name = get_user_name(recipient_id)
            
            message = f"[id{user_id}|Администратор] подарил подписку LUXE [id{recipient_id}|{recipient_name}]\n⏰ Срок: {duration}"
            
            keyboard = create_case_keyboard(subscription['id'], 'subscription')
            
            response = vk.messages.send(
                peer_id=peer_id,
                message=message,
                keyboard=json.dumps(keyboard),
                random_id=random.randint(1, 2147483647)
            )
            
            subscription['message_id'] = response
            subscription['peer_id'] = peer_id
            subscription['conversation_message_id'] = response
            
            cases = load_cases()
            cases[str(subscription['id'])] = subscription
            save_cases(cases)
            
            print(f"✓ Создана подписка LUXE ID {subscription['id']} от админа {user_id} для пользователя {recipient_id} на срок {duration}")
        except Exception as e:
            print(f"✗ Ошибка создания подписки: {e}")
        return
    
    # КОМАНДЫ ДЛЯ ВЫДАЧИ ПОДПИСОК НАВСЕГДА
    if text.startswith('?vip_perm') and user_id == DEVELOPER_ID:
        parts = event.text.split()
        if len(parts) < 2:
            return
            
        mention = parts[1]
        recipient_id = None
        
        if mention.startswith('[id') and '|' in mention:
            recipient_id = int(mention.split('|')[0][3:])
        elif mention.startswith('@'):
            try:
                user_info = vk.users.get(user_ids=mention[1:])[0]
                recipient_id = user_info['id']
            except:
                return
        else:
            try:
                recipient_id = int(mention)
            except:
                return
        
        subscription = create_subscription('vip', user_id, recipient_id, 'навсегда', from_admin=True)
        
        try:
            sender_name = get_user_name(user_id)
            recipient_name = get_user_name(recipient_id)
            
            message = f"[id{user_id}|Администратор] подарил подписку V.I.P [id{recipient_id}|{recipient_name}]\n⏰ Срок: навсегда"
            
            keyboard = create_case_keyboard(subscription['id'], 'subscription')
            
            response = vk.messages.send(
                peer_id=peer_id,
                message=message,
                keyboard=json.dumps(keyboard),
                random_id=random.randint(1, 2147483647)
            )
            
            subscription['message_id'] = response
            subscription['peer_id'] = peer_id
            subscription['conversation_message_id'] = response
            
            cases = load_cases()
            cases[str(subscription['id'])] = subscription
            save_cases(cases)
            
            print(f"✓ Создана подписка V.I.P навсегда ID {subscription['id']} от админа {user_id} для пользователя {recipient_id}")
        except Exception as e:
            print(f"✗ Ошибка создания подписки: {e}")
        return
    
    if text.startswith('?premium_perm') and user_id == DEVELOPER_ID:
        parts = event.text.split()
        if len(parts) < 2:
            return
            
        mention = parts[1]
        recipient_id = None
        
        if mention.startswith('[id') and '|' in mention:
            recipient_id = int(mention.split('|')[0][3:])
        elif mention.startswith('@'):
            try:
                user_info = vk.users.get(user_ids=mention[1:])[0]
                recipient_id = user_info['id']
            except:
                return
        else:
            try:
                recipient_id = int(mention)
            except:
                return
        
        subscription = create_subscription('premium', user_id, recipient_id, 'навсегда', from_admin=True)
        
        try:
            sender_name = get_user_name(user_id)
            recipient_name = get_user_name(recipient_id)
            
            message = f"[id{user_id}|Администратор] подарил подписку PREMIUM [id{recipient_id}|{recipient_name}]\n⏰ Срок: навсегда"
            
            keyboard = create_case_keyboard(subscription['id'], 'subscription')
            
            response = vk.messages.send(
                peer_id=peer_id,
                message=message,
                keyboard=json.dumps(keyboard),
                random_id=random.randint(1, 2147483647)
            )
            
            subscription['message_id'] = response
            subscription['peer_id'] = peer_id
            subscription['conversation_message_id'] = response
            
            cases = load_cases()
            cases[str(subscription['id'])] = subscription
            save_cases(cases)
            
            print(f"✓ Создана подписка PREMIUM навсегда ID {subscription['id']} от админа {user_id} для пользователя {recipient_id}")
        except Exception as e:
            print(f"✗ Ошибка создания подписки: {e}")
        return
    
    if text.startswith('?deluxe_perm') and user_id == DEVELOPER_ID:
        parts = event.text.split()
        if len(parts) < 2:
            return
            
        mention = parts[1]
        recipient_id = None
        
        if mention.startswith('[id') and '|' in mention:
            recipient_id = int(mention.split('|')[0][3:])
        elif mention.startswith('@'):
            try:
                user_info = vk.users.get(user_ids=mention[1:])[0]
                recipient_id = user_info['id']
            except:
                return
        else:
            try:
                recipient_id = int(mention)
            except:
                return
        
        subscription = create_subscription('deluxe', user_id, recipient_id, 'навсегда', from_admin=True)
        
        try:
            sender_name = get_user_name(user_id)
            recipient_name = get_user_name(recipient_id)
            
            message = f"[id{user_id}|Администратор] подарил подписку DELUXE [id{recipient_id}|{recipient_name}]\n⏰ Срок: навсегда"
            
            keyboard = create_case_keyboard(subscription['id'], 'subscription')
            
            response = vk.messages.send(
                peer_id=peer_id,
                message=message,
                keyboard=json.dumps(keyboard),
                random_id=random.randint(1, 2147483647)
            )
            
            subscription['message_id'] = response
            subscription['peer_id'] = peer_id
            subscription['conversation_message_id'] = response
            
            cases = load_cases()
            cases[str(subscription['id'])] = subscription
            save_cases(cases)
            
            print(f"✓ Создана подписка DELUXE навсегда ID {subscription['id']} от админа {user_id} для пользователя {recipient_id}")
        except Exception as e:
            print(f"✗ Ошибка создания подписки: {e}")
        return
    
    if text.startswith('?luxe_perm') and user_id == DEVELOPER_ID:
        parts = event.text.split()
        if len(parts) < 2:
            return
            
        mention = parts[1]
        recipient_id = None
        
        if mention.startswith('[id') and '|' in mention:
            recipient_id = int(mention.split('|')[0][3:])
        elif mention.startswith('@'):
            try:
                user_info = vk.users.get(user_ids=mention[1:])[0]
                recipient_id = user_info['id']
            except:
                return
        else:
            try:
                recipient_id = int(mention)
            except:
                return
        
        subscription = create_subscription('luxe', user_id, recipient_id, 'навсегда', from_admin=True)
        
        try:
            sender_name = get_user_name(user_id)
            recipient_name = get_user_name(recipient_id)
            
            message = f"[id{user_id}|Администратор] подарил подписку LUXE [id{recipient_id}|{recipient_name}]\n⏰ Срок: навсегда"
            
            keyboard = create_case_keyboard(subscription['id'], 'subscription')
            
            response = vk.messages.send(
                peer_id=peer_id,
                message=message,
                keyboard=json.dumps(keyboard),
                random_id=random.randint(1, 2147483647)
            )
            
            subscription['message_id'] = response
            subscription['peer_id'] = peer_id
            subscription['conversation_message_id'] = response
            
            cases = load_cases()
            cases[str(subscription['id'])] = subscription
            save_cases(cases)
            
            print(f"✓ Создана подписка LUXE навсегда ID {subscription['id']} от админа {user_id} для пользователя {recipient_id}")
        except Exception as e:
            print(f"✗ Ошибка создания подписки: {e}")
        return
    
    # ?case_ng (ТОЛЬКО ДЛЯ АДМИНА)
    if text.startswith('?case_ng') and user_id == DEVELOPER_ID:
        parts = event.text.split()
        if len(parts) < 2:
            return
            
        mention = parts[1]
        recipient_id = None
        
        if mention.startswith('[id') and '|' in mention:
            recipient_id = int(mention.split('|')[0][3:])
        elif mention.startswith('@'):
            try:
                user_info = vk.users.get(user_ids=mention[1:])[0]
                recipient_id = user_info['id']
            except:
                return
        else:
            try:
                recipient_id = int(mention)
            except:
                return
        
        case = create_case('ng', user_id, recipient_id, from_admin=True)
        
        try:
            sender_name = get_user_name(user_id)
            recipient_name = get_user_name(recipient_id)
            case_type_name = get_case_type_name(case['type'])
            
            if case['from_admin']:
                message = f"[id{user_id}|Администратор] подарил {case_type_name} кейс [id{recipient_id}|{recipient_name}]"
            else:
                message = f"[id{user_id}|{sender_name}] подарил {case_type_name} кейс [id{recipient_id}|{recipient_name}]"
            
            keyboard = create_case_keyboard(case['id'])
            
            response = vk.messages.send(
                peer_id=peer_id,
                message=message,
                keyboard=json.dumps(keyboard),
                random_id=random.randint(1, 2147483647)
            )
            
            case['message_id'] = response
            case['peer_id'] = peer_id
            case['current_sender_id'] = user_id
            case['conversation_message_id'] = response
            
            cases = load_cases()
            cases[str(case['id'])] = case
            save_cases(cases)
            
            print(f"✓ Создан кейс ID {case['id']} от админа {user_id} для пользователя {recipient_id} ({recipient_name})")
        except Exception as e:
            print(f"✗ Ошибка создания кейса: {e}")
        return
    
    # ?case_random (ТОЛЬКО ДЛЯ АДМИНА) - создает кейс для случайного пользователя в чате
    if text == '?case_random' and user_id == DEVELOPER_ID:
        try:
            chat_members = vk.messages.getConversationMembers(peer_id=peer_id)['items']
            
            user_members = []
            for member in chat_members:
                member_id = member['member_id']
                if member_id > 0 and member_id != user_id:
                    user_members.append(member_id)
            
            if not user_members:
                vk.messages.send(
                    peer_id=peer_id,
                    message="❌ В чате нет других пользователей для отправки кейса.",
                    random_id=random.randint(1, 2147483647)
                )
                return
            
            recipient_id = random.choice(user_members)
            
            case = create_case('random', user_id, recipient_id, from_admin=True)
            
            sender_name = get_user_name(user_id)
            recipient_name = get_user_name(recipient_id)
            case_type_name = get_case_type_name(case['type'])
            
            if case['from_admin']:
                message = f"[id{user_id}|Администратор] подарил {case_type_name} кейс [id{recipient_id}|{recipient_name}]"
            else:
                message = f"[id{user_id}|{sender_name}] подарил {case_type_name} кейс [id{recipient_id}|{recipient_name}]"
            
            keyboard = create_case_keyboard(case['id'])
            
            response = vk.messages.send(
                peer_id=peer_id,
                message=message,
                keyboard=json.dumps(keyboard),
                random_id=random.randint(1, 2147483647)
            )
            
            case['message_id'] = response
            case['peer_id'] = peer_id
            case['current_sender_id'] = user_id
            case['conversation_message_id'] = response
            
            cases = load_cases()
            cases[str(case['id'])] = case
            save_cases(cases)
            
            print(f"✓ Создан РАНДОМНЫЙ кейс ID {case['id']} от админа {user_id} для случайного пользователя {recipient_id} ({recipient_name})")
        except Exception as e:
            print(f"✗ Ошибка создания рандомного кейса: {e}")
            vk.messages.send(
                peer_id=peer_id,
                message="❌ Произошла ошибка при создании кейса.",
                random_id=random.randint(1, 2147483647)
            )
        return
    
    # ?gift - передача кейса или подписки
    if text.startswith('?gift'):
        parts = event.text.split()
        if len(parts) < 2:
            return
            
        mention = parts[1]
        new_recipient_id = None
        
        if mention.startswith('[id') and '|' in mention:
            new_recipient_id = int(mention.split('|')[0][3:])
        elif mention.startswith('@'):
            try:
                user_info = vk.users.get(user_ids=mention[1:])[0]
                new_recipient_id = user_info['id']
            except:
                return
        else:
            try:
                new_recipient_id = int(mention)
            except:
                return
        
        cases = load_cases()
        inventory = load_inventory()
        
        # Проверяем активные кейсы
        for case_id, case in cases.items():
            if case.get('waiting_gift') and case['recipient_id'] == user_id and not case.get('opened', False):
                return process_case_gift(case, case_id, user_id, new_recipient_id, peer_id, event)
        
        # Проверяем активные подписки
        for sub_id, sub in cases.items():
            if sub.get('subscription_type') and sub.get('waiting_gift') and sub['recipient_id'] == user_id and not sub.get('opened', False):
                return process_subscription_gift(sub, sub_id, user_id, new_recipient_id, peer_id, event)
        
        # Проверяем кейсы в инвентаре
        user_inv = inventory.get(str(user_id), {})
        for case_item in user_inv.get('cases', []):
            if case_item.get('waiting_gift'):
                return process_inventory_case_gift(case_item, user_id, new_recipient_id, peer_id, event)
        
        # Проверяем подписки в инвентаре
        for sub_item in user_inv.get('subscriptions', []):
            if sub_item.get('waiting_gift'):
                return process_inventory_subscription_gift(sub_item, user_id, new_recipient_id, peer_id, event)
        
        vk.messages.send(
            peer_id=peer_id,
            message="❌ Нет активных кейсов или подписок для передачи.",
            random_id=random.randint(1, 2147483647)
        )

def process_case_gift(case, case_id, user_id, new_recipient_id, peer_id, event):
    try:
        chat_members = vk.messages.getConversationMembers(peer_id=event.peer_id)['items']
        in_chat = any(member['member_id'] == new_recipient_id for member in chat_members)
        
        if not in_chat:
            vk.messages.send(
                peer_id=event.peer_id,
                message="❌ Участник не найден в чате. Попробуйте снова или заберите кейс себе.",
                random_id=random.randint(1, 2147483647)
            )
            return True
        
        if case.get('message_id') and case.get('peer_id'):
            delete_message(case['peer_id'], case['message_id'])
        
        old_recipient_name = get_user_name(case['recipient_id'])
        case['recipient_id'] = new_recipient_id
        case['waiting_gift'] = False
        case['current_sender_id'] = user_id
        case['from_admin'] = False
        
        sender_name = get_user_name(user_id)
        new_recipient_name = get_user_name(new_recipient_id)
        case_type_name = get_case_type_name(case['type'])
        
        message = f"[id{user_id}|{sender_name}] подарил {case_type_name} кейс [id{new_recipient_id}|{new_recipient_name}]"
        
        keyboard = create_case_keyboard(case['id'])
        
        response = vk.messages.send(
            peer_id=case['peer_id'],
            message=message,
            keyboard=json.dumps(keyboard),
            random_id=random.randint(1, 2147483647)
        )
        
        case['message_id'] = response
        case['conversation_message_id'] = response
        
        cases = load_cases()
        cases[str(case['id'])] = case
        save_cases(cases)
        
        print(f"✓ Кейс {case['id']} передан от {old_recipient_name} к {new_recipient_name} пользователем {user_id}")
        
        return True
        
    except Exception as e:
        print(f"✗ Ошибка при передаче кейса: {e}")
        return False

def process_subscription_gift(subscription, sub_id, user_id, new_recipient_id, peer_id, event):
    try:
        chat_members = vk.messages.getConversationMembers(peer_id=event.peer_id)['items']
        in_chat = any(member['member_id'] == new_recipient_id for member in chat_members)
        
        if not in_chat:
            vk.messages.send(
                peer_id=event.peer_id,
                message="❌ Участник не найден в чате. Попробуйте снова или заберите подписку себе.",
                random_id=random.randint(1, 2147483647)
            )
            return True
        
        if subscription.get('message_id') and subscription.get('peer_id'):
            delete_message(subscription['peer_id'], subscription['message_id'])
        
        old_recipient_name = get_user_name(subscription['recipient_id'])
        subscription['recipient_id'] = new_recipient_id
        subscription['waiting_gift'] = False
        subscription['current_sender_id'] = user_id
        subscription['from_admin'] = False
        
        sender_name = get_user_name(user_id)
        new_recipient_name = get_user_name(new_recipient_id)
        sub_name = subscription.get('subscription_name', 'Подписка')
        duration = subscription.get('duration', 'Не указано')
        
        message = f"[id{user_id}|{sender_name}] подарил подписку {sub_name} [id{new_recipient_id}|{new_recipient_name}]\n⏰ Срок: {duration}"
        
        keyboard = create_case_keyboard(subscription['id'], 'subscription')
        
        response = vk.messages.send(
            peer_id=subscription['peer_id'],
            message=message,
            keyboard=json.dumps(keyboard),
            random_id=random.randint(1, 2147483647)
        )
        
        subscription['message_id'] = response
        subscription['conversation_message_id'] = response
        
        cases = load_cases()
        cases[str(subscription['id'])] = subscription
        save_cases(cases)
        
        print(f"✓ Подписка {subscription['id']} передан от {old_recipient_name} к {new_recipient_name} пользователем {user_id}")
        
        return True
        
    except Exception as e:
        print(f"✗ Ошибка при передаче подписки: {e}")
        return False

def process_inventory_case_gift(case_item, user_id, new_recipient_id, peer_id, event):
    try:
        chat_members = vk.messages.getConversationMembers(peer_id=event.peer_id)['items']
        in_chat = any(member['member_id'] == new_recipient_id for member in chat_members)
        
        if not in_chat:
            vk.messages.send(
                peer_id=event.peer_id,
                message="❌ Участник не найден в чате.",
                random_id=random.randint(1, 2147483647)
            )
            return True
        
        case_data = case_item.get('data', {})
        case = create_case(case_data.get('type', 'ng'), user_id, new_recipient_id, from_admin=False)
        
        sender_name = get_user_name(user_id)
        new_recipient_name = get_user_name(new_recipient_id)
        case_type_name = get_case_type_name(case['type'])
        
        message = f"[id{user_id}|{sender_name}] подарил {case_type_name} кейс [id{new_recipient_id}|{new_recipient_name}]"
        
        keyboard = create_case_keyboard(case['id'])
        
        response = vk.messages.send(
            peer_id=peer_id,
            message=message,
            keyboard=json.dumps(keyboard),
            random_id=random.randint(1, 2147483647)
        )
        
        case['message_id'] = response
        case['peer_id'] = peer_id
        case['conversation_message_id'] = response
        
        cases = load_cases()
        cases[str(case['id'])] = case
        save_cases(cases)
        
        remove_from_inventory(user_id, 'case', case_item['id'])
        
        print(f"✓ Кейс из инвентаря передан от {user_id} к {new_recipient_id}")
        
        return True
        
    except Exception as e:
        print(f"✗ Ошибка при передаче кейса из инвентаря: {e}")
        return False

def process_inventory_subscription_gift(sub_item, user_id, new_recipient_id, peer_id, event):
    try:
        chat_members = vk.messages.getConversationMembers(peer_id=event.peer_id)['items']
        in_chat = any(member['member_id'] == new_recipient_id for member in chat_members)
        
        if not in_chat:
            vk.messages.send(
                peer_id=event.peer_id,
                message="❌ Участник не найден в чате.",
                random_id=random.randint(1, 2147483647)
            )
            return True
        
        sub_data = sub_item.get('data', {})
        subscription = create_subscription(
            sub_data.get('subscription_type', 'vip'), 
            user_id, 
            new_recipient_id, 
            sub_data.get('duration', '1 день'), 
            from_admin=False
        )
        
        sender_name = get_user_name(user_id)
        new_recipient_name = get_user_name(new_recipient_id)
        sub_name = sub_data.get('subscription_name', 'Подписка')
        duration = sub_data.get('duration', 'Не указано')
        
        message = f"[id{user_id}|{sender_name}] подарил подписку {sub_name} [id{new_recipient_id}|{new_recipient_name}]\n⏰ Срок: {duration}"
        
        keyboard = create_case_keyboard(subscription['id'], 'subscription')
        
        response = vk.messages.send(
            peer_id=peer_id,
            message=message,
            keyboard=json.dumps(keyboard),
            random_id=random.randint(1, 2147483647)
        )
        
        subscription['message_id'] = response
        subscription['peer_id'] = peer_id
        subscription['conversation_message_id'] = response
        
        cases = load_cases()
        cases[str(subscription['id'])] = subscription
        save_cases(cases)
        
        remove_from_inventory(user_id, 'subscription', sub_item['id'])
        
        print(f"✓ Подписка из инвентаря передан от {user_id} к {new_recipient_id}")
        
        return True
        
    except Exception as e:
        print(f"✗ Ошибка при передаче подписки из инвентаря: {e}")
        return False

# ========== ОБРАБОТКА CALLBACK СОБЫТИЙ БАНКА ==========

def handle_bank_callback(event, payload):
    """Обрабатывает callback события банка"""
    user_id = event.object.user_id
    peer_id = event.object.peer_id
    conversation_message_id = event.object.conversation_message_id
    action = payload.get('action')
    target_user_id = payload.get('user_id')
    
    if user_id != target_user_id:
        vk.messages.sendMessageEventAnswer(
            event_id=event.object.event_id,
            user_id=user_id,
            peer_id=peer_id,
            event_data=json.dumps({'type': 'show_snackbar', 'text': 'Это не ваш банк!'})
        )
        return
    
    if action == 'bank_main':
        # Удаляем старое сообщение и отправляем новое с главной страницей банка
        try:
            vk.messages.delete(
                delete_for_all=1,
                peer_id=peer_id,
                cmids=conversation_message_id
            )
        except:
            pass
        
        # Очищаем ожидающую операцию (если есть)
        clear_waiting_operation(user_id)
        
        # Отправляем новое сообщение
        send_bank_message(peer_id, user_id, "main")
        
        vk.messages.sendMessageEventAnswer(
            event_id=event.object.event_id,
            user_id=user_id,
            peer_id=peer_id,
            event_data=json.dumps({'type': 'show_snackbar', 'text': '🏦 Главное меню банка'})
        )
    
    elif action == 'bank_storage':
        # Удаляем старое сообщение и отправляем новое с хранилищем
        try:
            vk.messages.delete(
                delete_for_all=1,
                peer_id=peer_id,
                cmids=conversation_message_id
            )
        except:
            pass
        
        # Очищаем ожидающую операцию (если есть)
        clear_waiting_operation(user_id)
        
        # Отправляем новое сообщение
        send_bank_message(peer_id, user_id, "storage")
        
        vk.messages.sendMessageEventAnswer(
            event_id=event.object.event_id,
            user_id=user_id,
            peer_id=peer_id,
            event_data=json.dumps({'type': 'show_snackbar', 'text': '💰 Личное хранилище'})
        )
    
    elif action == 'bank_transactions':
        page = payload.get('page', 1)
        # Удаляем старое сообщение и отправляем новое с транзакциями
        try:
            vk.messages.delete(
                delete_for_all=1,
                peer_id=peer_id,
                cmids=conversation_message_id
            )
        except:
            pass
        
        # Очищаем ожидающую операцию (если есть)
        clear_waiting_operation(user_id)
        
        # Отправляем новое сообщение
        send_bank_message(peer_id, user_id, "transactions", None, page)
        
        vk.messages.sendMessageEventAnswer(
            event_id=event.object.event_id,
            user_id=user_id,
            peer_id=peer_id,
            event_data=json.dumps({'type': 'show_snackbar', 'text': f'📊 Транзакции (стр. {page})'})
        )
    
    elif action == 'bank_withdraw':
        # Проверяем, что пользователь находится в разделе хранилища
        if not is_bank_session_active(user_id, peer_id):
            vk.messages.sendMessageEventAnswer(
                event_id=event.object.event_id,
                user_id=user_id,
                peer_id=peer_id,
                event_data=json.dumps({'type': 'show_snackbar', 'text': '❌ Откройте банк и хранилище сначала!'})
            )
            return
        
        # Устанавливаем ожидание операции снятия
        set_waiting_operation(user_id, peer_id, 'withdraw')
        
        message = f"💵 *Снятие средств*\n\n"
        message += f"Введите сумму для снятия из банка.\n"
        message += f"Пример: 100 (только число)\n\n"
        message += f"💰 В банке: {get_user_bank_balance(user_id)} Элитов\n"
        message += f"💵 Наличные: {get_user_balance(user_id)} Элитов\n\n"
        message += "⚠️ *После ввода суммы банк автоматически закроется!*"
        
        # Отправляем отдельное сообщение с инструкцией
        vk.messages.send(
            peer_id=peer_id,
            message=message,
            random_id=random.randint(1, 2147483647)
        )
        
        vk.messages.sendMessageEventAnswer(
            event_id=event.object.event_id,
            user_id=user_id,
            peer_id=peer_id,
            event_data=json.dumps({'type': 'show_snackbar', 'text': '💵 Введите сумму для снятия в чат'})
        )
    
    elif action == 'bank_deposit':
        # Проверяем, что пользователь находится в разделе хранилища
        if not is_bank_session_active(user_id, peer_id):
            vk.messages.sendMessageEventAnswer(
                event_id=event.object.event_id,
                user_id=user_id,
                peer_id=peer_id,
                event_data=json.dumps({'type': 'show_snackbar', 'text': '❌ Откройте банк и хранилище сначала!'})
            )
            return
        
        # Устанавливаем ожидание операции пополнения
        set_waiting_operation(user_id, peer_id, 'deposit')
        
        message = f"💳 *Пополнение счета*\n\n"
        message += f"Введите сумму для пополнения банка.\n"
        message += f"Пример: 100 (только число)\n\n"
        message += f"💰 В банке: {get_user_bank_balance(user_id)} Элитов\n"
        message += f"💵 Наличные: {get_user_balance(user_id)} Элитов\n\n"
        message += "⚠️ *После ввода суммы банк автоматически закроется!*"
        
        # Отправляем отдельное сообщение с инструкцией
        vk.messages.send(
            peer_id=peer_id,
            message=message,
            random_id=random.randint(1, 2147483647)
        )
        
        vk.messages.sendMessageEventAnswer(
            event_id=event.object.event_id,
            user_id=user_id,
            peer_id=peer_id,
            event_data=json.dumps({'type': 'show_snackbar', 'text': '💳 Введите сумму для пополнения в чат'})
        )
    
    elif action == 'close_bank':
        # Деактивируем сессию банка
        deactivate_bank_session(user_id)
        clear_waiting_operation(user_id)
        
        try:
            delete_message(peer_id, conversation_message_id)
        except:
            pass
        
        vk.messages.sendMessageEventAnswer(
            event_id=event.object.event_id,
            user_id=user_id,
            peer_id=peer_id,
            event_data=json.dumps({'type': 'show_snackbar', 'text': '🏦 Банк закрыт'})
        )

# ========== ОБРАБОТКА СООБЩЕНИЙ ДЛЯ ПОПОЛНЕНИЯ/СНЯТИЯ ==========

def handle_bank_operation(event):
    """Обрабатывает сообщения для пополнения/снятия из банка"""
    text = event.text
    user_id = event.from_id
    peer_id = event.peer_id
    
    # Проверяем, ожидает ли пользователь операции
    if not is_waiting_operation(user_id, peer_id):
        return False
    
    try:
        amount = int(text)
        if amount <= 0:
            return False
    except:
        return False
    
    # Получаем тип операции
    operations = load_waiting_operations()
    user_ops = operations.get(str(user_id), {})
    operation_type = user_ops.get('operation_type')
    
    if not operation_type:
        return False
    
    # Выполняем операцию и закрываем банк
    return complete_bank_operation(user_id, peer_id, amount, operation_type)

# ========== ОСНОВНАЯ ЛОГИКА БОТА ==========

def handle_callback(event):
    try:
        payload_str = event.object.payload
        if isinstance(payload_str, dict):
            payload = payload_str
        else:
            payload = json.loads(payload_str)
            
        action = payload.get('action')
        user_id = event.object.user_id
        peer_id = event.object.peer_id
        conversation_message_id = event.object.conversation_message_id
        
        # Обрабатываем новогодние поздравления
        send_new_year_greeting(user_id, peer_id, event_type='callback', callback_data={
            'event_id': event.object.event_id
        })
        
        # Проверяем, является ли callback для банка
        if action and action.startswith('bank_'):
            return handle_bank_callback(event, payload)
        
        # Для остальных callback (кейсы/инвентарь) - удаляем сообщение с кнопками
        try:
            print(f"🗑️ Удаляю сообщение с кнопками: peer_id={peer_id}, conversation_message_id={conversation_message_id}")
            vk.messages.delete(
                delete_for_all=1,
                peer_id=peer_id,
                cmids=conversation_message_id
            )
            print(f"✓ Сообщение удалено")
        except Exception as e:
            print(f"✗ Ошибка удаления сообщения: {e}")
        
        # Закрытие инвентаря
        if action == 'close_inventory':
            target_user_id = payload.get('user_id')
            
            if user_id != target_user_id:
                vk.messages.sendMessageEventAnswer(
                    event_id=event.object.event_id,
                    user_id=user_id,
                    peer_id=peer_id,
                    event_data=json.dumps({'type': 'show_snackbar', 'text': 'Это не ваш инвентарь!'})
                )
                return
            
            vk.messages.sendMessageEventAnswer(
                event_id=event.object.event_id,
                user_id=user_id,
                peer_id=peer_id,
                event_data=json.dumps({'type': 'show_snackbar', 'text': 'Инвентарь закрыт!'})
            )
            return
        
        # Навигация по инвентарю
        if action == 'inv_section':
            section = payload.get('section')
            target_user_id = payload.get('user_id')
            page = payload.get('page', 1)
            
            if user_id != target_user_id:
                vk.messages.sendMessageEventAnswer(
                    event_id=event.object.event_id,
                    user_id=user_id,
                    peer_id=peer_id,
                    event_data=json.dumps({'type': 'show_snackbar', 'text': 'Это не ваш инвентарь!'})
                )
                return
            
            send_inventory_message(peer_id, user_id, section, conversation_message_id, page)
            return
        
        # Использование кейса из инвентаря
        if action == 'use_case_from_inv':
            case_id = payload.get('case_id')
            target_user_id = payload.get('user_id')
            page = payload.get('page', 1)
            
            if user_id != target_user_id:
                vk.messages.sendMessageEventAnswer(
                    event_id=event.object.event_id,
                    user_id=user_id,
                    peer_id=peer_id,
                    event_data=json.dumps({'type': 'show_snackbar', 'text': 'Это не ваш кейс!'})
                )
                return
            
            inventory = load_inventory()
            user_inv = inventory.get(str(user_id), {})
            
            for case_item in user_inv.get('cases', []):
                if case_item['id'] == case_id:
                    prize, duration = get_random_prize()
                    
                    recipient_name = get_user_name(user_id)
                    message = f"[id{user_id}|{recipient_name}] Вы открыли кейс из инвентаря\n\n📦 Содержимое: {prize['name']}\n⏰ Срок: {duration}\n🔍 Проверить: !роль"
                    
                    vk.messages.send(
                        peer_id=peer_id,
                        message=message,
                        random_id=random.randint(1, 2147483647)
                    )
                    
                    try:
                        user_info = vk.users.get(user_ids=user_id, fields='screen_name')[0]
                        username = user_info.get('screen_name', f'id{user_id}')
                        send_to_archive(f"роль @{username} {prize['id']}")
                    except:
                        send_to_archive(f"роль @id{user_id} {prize['id']}")
                    
                    if duration != 'навсегда':
                        add_expiring_prize(user_id, prize['id'], duration)
                    
                    remove_from_inventory(user_id, 'case', case_id)
                    
                    send_inventory_message(peer_id, user_id, "cases", conversation_message_id, page)
                    
                    vk.messages.sendMessageEventAnswer(
                        event_id=event.object.event_id,
                        user_id=user_id,
                        peer_id=peer_id,
                        event_data=json.dumps({'type': 'show_snackbar', 'text': '🎁 Кейс открыт!'})
                    )
                    return
            
            vk.messages.sendMessageEventAnswer(
                event_id=event.object.event_id,
                user_id=user_id,
                peer_id=peer_id,
                event_data=json.dumps({'type': 'show_snackbar', 'text': 'Кейс не найден!'})
            )
            return
        
        # Передача кейса из инвентаря
        if action == 'gift_case_from_inv':
            case_id = payload.get('case_id')
            target_user_id = payload.get('user_id')
            page = payload.get('page', 1)
            
            if user_id != target_user_id:
                vk.messages.sendMessageEventAnswer(
                    event_id=event.object.event_id,
                    user_id=user_id,
                    peer_id=peer_id,
                    event_data=json.dumps({'type': 'show_snackbar', 'text': 'Это не ваш кейс!'})
                )
                return
            
            inventory = load_inventory()
            user_inv = inventory.get(str(user_id), {})
            
            for case_item in user_inv.get('cases', []):
                if case_item['id'] == case_id:
                    case_item['waiting_gift'] = True
                    save_inventory(inventory)
                    
                    send_inventory_message(peer_id, user_id, "cases", conversation_message_id, page)
                    
                    vk.messages.sendMessageEventAnswer(
                        event_id=event.object.event_id,
                        user_id=user_id,
                        peer_id=peer_id,
                        event_data=json.dumps({'type': 'show_snackbar', 'text': '🎀 Введите команду ?gift @username'})
                    )
                    
                    # Отправляем сообщение с инструкцией
                    vk.messages.send(
                        peer_id=peer_id,
                        message="🎀 Для передачи кейса введите команду:\n?gift @username",
                        random_id=random.randint(1, 2147483647)
                    )
                    return
            
            vk.messages.sendMessageEventAnswer(
                event_id=event.object.event_id,
                user_id=user_id,
                peer_id=peer_id,
                event_data=json.dumps({'type': 'show_snackbar', 'text': 'Кейс не найден!'})
            )
            return
        
        # Использование подписки из инвентаря
        if action == 'use_sub_from_inv':
            sub_id = payload.get('sub_id')
            target_user_id = payload.get('user_id')
            page = payload.get('page', 1)
            
            if user_id != target_user_id:
                vk.messages.sendMessageEventAnswer(
                    event_id=event.object.event_id,
                    user_id=user_id,
                    peer_id=peer_id,
                    event_data=json.dumps({'type': 'show_snackbar', 'text': 'Это не ваша подписка!'})
                )
                return
            
            inventory = load_inventory()
            user_inv = inventory.get(str(user_id), {})
            
            for sub_item in user_inv.get('subscriptions', []):
                if sub_item['id'] == sub_id:
                    sub_data = sub_item.get('data', {})
                    sub_name = sub_data.get('subscription_name', 'Подписка')
                    duration = sub_data.get('duration', '1 день')
                    prize_id = sub_data.get('subscription_id', 1)
                    
                    recipient_name = get_user_name(user_id)
                    message = f"[id{user_id}|{recipient_name}] Вы использовали подписку из инвентаря\n\n⭐ Подписка: {sub_name}\n⏰ Срок: {duration}\n🔍 Проверить: !роль"
                    
                    vk.messages.send(
                        peer_id=peer_id,
                        message=message,
                        random_id=random.randint(1, 2147483647)
                    )
                    
                    try:
                        user_info = vk.users.get(user_ids=user_id, fields='screen_name')[0]
                        username = user_info.get('screen_name', f'id{user_id}')
                        send_to_archive(f"роль @{username} {prize_id}")
                    except:
                        send_to_archive(f"роль @id{user_id} {prize_id}")
                    
                    if duration != 'навсегда':
                        add_expiring_prize(user_id, prize_id, duration)
                    
                    remove_from_inventory(user_id, 'subscription', sub_id)
                    
                    send_inventory_message(peer_id, user_id, "subscriptions", conversation_message_id, page)
                    
                    vk.messages.sendMessageEventAnswer(
                        event_id=event.object.event_id,
                        user_id=user_id,
                        peer_id=peer_id,
                        event_data=json.dumps({'type': 'show_snackbar', 'text': '⭐ Подписка активирована!'})
                    )
                    return
            
            vk.messages.sendMessageEventAnswer(
                event_id=event.object.event_id,
                user_id=user_id,
                peer_id=peer_id,
                event_data=json.dumps({'type': 'show_snackbar', 'text': 'Подписка не найдена!'})
            )
            return
        
        # Передача подписки из инвентаря
        if action == 'gift_sub_from_inv':
            sub_id = payload.get('sub_id')
            target_user_id = payload.get('user_id')
            page = payload.get('page', 1)
            
            if user_id != target_user_id:
                vk.messages.sendMessageEventAnswer(
                    event_id=event.object.event_id,
                    user_id=user_id,
                    peer_id=peer_id,
                    event_data=json.dumps({'type': 'show_snackbar', 'text': 'Это не ваша подписка!'})
                )
                return
            
            inventory = load_inventory()
            user_inv = inventory.get(str(user_id), {})
            
            for sub_item in user_inv.get('subscriptions', []):
                if sub_item['id'] == sub_id:
                    sub_item['waiting_gift'] = True
                    save_inventory(inventory)
                    
                    send_inventory_message(peer_id, user_id, "subscriptions", conversation_message_id, page)
                    
                    vk.messages.sendMessageEventAnswer(
                        event_id=event.object.event_id,
                        user_id=user_id,
                        peer_id=peer_id,
                        event_data=json.dumps({'type': 'show_snackbar', 'text': '🎀 Введите команду ?gift @username'})
                    )
                    
                    # Отправляем сообщение с инструкцией
                    vk.messages.send(
                        peer_id=peer_id,
                        message="🎀 Для передачи подписки введите команду:\n?gift @username",
                        random_id=random.randint(1, 2147483647)
                    )
                    return
            
            vk.messages.sendMessageEventAnswer(
                event_id=event.object.event_id,
                user_id=user_id,
                peer_id=peer_id,
                event_data=json.dumps({'type': 'show_snackbar', 'text': 'Подписка не найдена!'})
            )
            return
        
        # Использование других предметов
        if action == 'use_item':
            item_type = payload.get('item_type')
            item_id = payload.get('item_id')
            target_user_id = payload.get('user_id')
            
            if user_id != target_user_id:
                vk.messages.sendMessageEventAnswer(
                    event_id=event.object.event_id,
                    user_id=user_id,
                    peer_id=peer_id,
                    event_data=json.dumps({'type': 'show_snackbar', 'text': 'Это не ваш предмет!'})
                )
                return
            
            vk.messages.sendMessageEventAnswer(
                event_id=event.object.event_id,
                user_id=user_id,
                peer_id=peer_id,
                event_data=json.dumps({'type': 'show_snackbar', 'text': 'Предмет не найден!'})
            )
            return
        
        # ОБРАБОТКА ПОДПИСОК (ИСПОЛЬЗОВАТЬ/В ИНВЕНТАРЬ/ПОДАРИТЬ)
        if action in ['open_subscription', 'to_inventory_sub', 'gift_subscription']:
            sub_id = payload.get('sub_id')
            if not sub_id:
                return
            
            cases = load_cases()
            sub_data = cases.get(str(sub_id))
            
            if not sub_data or not sub_data.get('subscription_type'):
                vk.messages.sendMessageEventAnswer(
                    event_id=event.object.event_id,
                    user_id=user_id,
                    peer_id=peer_id,
                    event_data=json.dumps({'type': 'show_snackbar', 'text': 'Подписка не найдена!'})
                )
                return
            
            if user_id != sub_data['recipient_id']:
                vk.messages.sendMessageEventAnswer(
                    event_id=event.object.event_id,
                    user_id=user_id,
                    peer_id=peer_id,
                    event_data=json.dumps({'type': 'show_snackbar', 'text': 'Это не ваш подарок!'})
                )
                return
            
            # Проверяем, не активирована ли уже подписка
            if sub_data.get('opened'):
                vk.messages.sendMessageEventAnswer(
                    event_id=event.object.event_id,
                    user_id=user_id,
                    peer_id=peer_id,
                    event_data=json.dumps({'type': 'show_snackbar', 'text': 'Эта подписка уже активирована!'})
                )
                return
            
            # Проверяем, не в инвентаре ли уже подписка
            if sub_data.get('in_inventory'):
                vk.messages.sendMessageEventAnswer(
                    event_id=event.object.event_id,
                    user_id=user_id,
                    peer_id=peer_id,
                    event_data=json.dumps({'type': 'show_snackbar', 'text': 'Эта подписка уже в инвентаре!'})
                )
                return
            
            if action == 'open_subscription':
                sub_name = sub_data.get('subscription_name', 'Подписка')
                duration = sub_data.get('duration', '1 день')
                prize_id = sub_data.get('subscription_id', 1)
                
                prize = {'id': prize_id, 'name': sub_name}
                send_new_message_with_prize(peer_id, user_id, prize, duration, 'subscription')
                
                sub_data['opened'] = True
                sub_data['in_inventory'] = False
                sub_data['waiting_gift'] = False
                cases[str(sub_id)] = sub_data
                save_cases(cases)
                
                vk.messages.sendMessageEventAnswer(
                    event_id=event.object.event_id,
                    user_id=user_id,
                    peer_id=peer_id,
                    event_data=json.dumps({'type': 'show_snackbar', 'text': '⭐ Подписка активирована!'})
                )
                
                sender_name = get_user_name(sub_data['current_sender_id'])
                print(f"✓ Подписка {sub_id} (от {sender_name}) активирована пользователем {user_id}, подписка: {sub_name} ({duration})")
                
            elif action == 'to_inventory_sub':
                sub_data['in_inventory'] = True
                sub_data['opened'] = False
                sub_data['waiting_gift'] = False
                
                inventory_data = {
                    'subscription_type': sub_data.get('subscription_type', 'vip'),
                    'subscription_name': sub_data.get('subscription_name', 'Подписка'),
                    'subscription_id': sub_data.get('subscription_id', 1),
                    'duration': sub_data.get('duration', '1 день'),
                    'sender_id': sub_data['sender_id'],
                    'original_sub_id': sub_data['id'],
                    'added_to_inv': datetime.now().isoformat()
                }
                
                add_to_inventory(user_id, 'subscription', inventory_data)
                cases[str(sub_id)] = sub_data
                save_cases(cases)
                
                vk.messages.sendMessageEventAnswer(
                    event_id=event.object.event_id,
                    user_id=user_id,
                    peer_id=peer_id,
                    event_data=json.dumps({'type': 'show_snackbar', 'text': '📦 Подписка добавлена в инвентарь!'})
                )
                
                print(f"✓ Подписка {sub_id} добавлена в инвентарь пользователя {user_id}")
                
            elif action == 'gift_subscription':
                sub_data['waiting_gift'] = True
                cases[str(sub_id)] = sub_data
                save_cases(cases)
                
                vk.messages.sendMessageEventAnswer(
                    event_id=event.object.event_id,
                    user_id=user_id,
                    peer_id=peer_id,
                    event_data=json.dumps({'type': 'show_snackbar', 'text': '🎀 Введите команду ?gift @username'})
                )
                
                # Отправляем сообщение с инструкцией
                vk.messages.send(
                    peer_id=peer_id,
                    message="🎀 Для передачи подписки введите команду:\n?gift @username",
                    random_id=random.randint(1, 2147483647)
                )
                
                print(f"✓ Подписка {sub_id} ожидает передачи от пользователя {user_id}")
            return
        
        # ОБРАБОТКА КЕЙСОВ (ОТКРЫТЬ/В ИНВЕНТАРЬ/ПОДАРИТЬ)
        case_id = payload.get('case_id')
        if not case_id:
            return
        
        cases = load_cases()
        case_data = cases.get(str(case_id))
        
        if not case_data:
            vk.messages.sendMessageEventAnswer(
                event_id=event.object.event_id,
                user_id=user_id,
                peer_id=peer_id,
                event_data=json.dumps({'type': 'show_snackbar', 'text': 'Кейс не найден!'})
            )
            return
        
        if user_id != case_data['recipient_id']:
            vk.messages.sendMessageEventAnswer(
                event_id=event.object.event_id,
                user_id=user_id,
                peer_id=peer_id,
                event_data=json.dumps({'type': 'show_snackbar', 'text': 'Это не ваш подарок!'})
            )
            return
        
        # Проверяем, не открыт ли уже кейс
        if case_data.get('opened'):
            vk.messages.sendMessageEventAnswer(
                event_id=event.object.event_id,
                user_id=user_id,
                peer_id=peer_id,
                event_data=json.dumps({'type': 'show_snackbar', 'text': 'Этот кейс уже открыт!'})
            )
            return
        
        # Проверяем, не в инвентаре ли уже кейс
        if case_data.get('in_inventory'):
            vk.messages.sendMessageEventAnswer(
                event_id=event.object.event_id,
                user_id=user_id,
                peer_id=peer_id,
                event_data=json.dumps({'type': 'show_snackbar', 'text': 'Этот кейс уже в инвентаре!'})
            )
            return
        
        if action == 'open_case':
            prize, duration = get_random_prize()
            send_new_message_with_prize(peer_id, user_id, prize, duration)
            
            case_data['opened'] = True
            case_data['in_inventory'] = False
            case_data['waiting_gift'] = False
            case_data['prize_id'] = prize['id']
            case_data['duration'] = duration
            cases[str(case_id)] = case_data
            save_cases(cases)
            
            vk.messages.sendMessageEventAnswer(
                event_id=event.object.event_id,
                user_id=user_id,
                peer_id=peer_id,
                event_data=json.dumps({'type': 'show_snackbar', 'text': '🎁 Кейс открыт!'})
            )
            
            sender_name = get_user_name(case_data['current_sender_id'])
            print(f"✓ Кейс {case_id} (от {sender_name}) открыт пользователем {user_id}, приз: {prize['name']} ({duration})")
            
        elif action == 'to_inventory':
            case_data['in_inventory'] = True
            case_data['opened'] = False
            case_data['waiting_gift'] = False
            
            inventory_data = {
                'type': case_data['type'],
                'sender_id': case_data['sender_id'],
                'original_case_id': case_data['id'],
                'added_to_inv': datetime.now().isoformat()
            }
            
            add_to_inventory(user_id, 'case', inventory_data)
            cases[str(case_id)] = case_data
            save_cases(cases)
            
            vk.messages.sendMessageEventAnswer(
                event_id=event.object.event_id,
                user_id=user_id,
                peer_id=peer_id,
                event_data=json.dumps({'type': 'show_snackbar', 'text': '📦 Кейс добавлен в инвентарь!'})
            )
            
            print(f"✓ Кейс {case_id} добавлен в инвентарь пользователя {user_id}")
            
        elif action == 'gift_case':
            case_data['waiting_gift'] = True
            cases[str(case_id)] = case_data
            save_cases(cases)
            
            vk.messages.sendMessageEventAnswer(
                event_id=event.object.event_id,
                user_id=user_id,
                peer_id=peer_id,
                event_data=json.dumps({'type': 'show_snackbar', 'text': '🎀 Введите команду ?gift @username'})
            )
            
            # Отправляем сообщение с инструкцией
            vk.messages.send(
                peer_id=peer_id,
                message="🎀 Для передачи кейса введите команду:\n?gift @username",
                random_id=random.randint(1, 2147483647)
            )
            
            print(f"✓ Кейс {case_id} ожидает передачи от пользователя {user_id}")
            
    except Exception as e:
        print(f"✗ Ошибка обработки callback: {e}")
        try:
            vk.messages.sendMessageEventAnswer(
                event_id=event.object.event_id,
                user_id=event.object.user_id,
                peer_id=event.object.peer_id,
                event_data=json.dumps({'type': 'show_snackbar', 'text': 'Произошла ошибка!'})
            )
        except:
            pass

def start_expiry_checker():
    checker_thread = threading.Thread(target=check_expired_prizes, daemon=True)
    checker_thread.start()
    print("✓ Запущен поток проверки истекших призов")

print("=" * 60)
print("🏦 Elite Bank Бот с валютой 'Элит' запущен!")
print("=" * 60)
print("\n📋 Доступные команды:")
print("?bank - открыть Elite Bank")
print("?pay @username/id сумма - перевести Элиты")
print("Элиты - показать наличные (только наличные!)")
print("?nik ваш_ник - установить никнейм")
print("?nik - посмотреть свой ник")
print("?nik_reset - сбросить никнейм")
print("?niks - посмотреть все никнеймы в чате")
print("\n🎄 Новогодние команды:")
print("?ny_status - статус новогодних поздравлений")
print("\n🎁 Старые команды (остаются):")
print("?info - информация о чате")
print("?chat_id - ID чата")
print("?profile @username/id - профиль пользователя")
print("?inv - открыть инвентарь")
print("?case_ng @username/id - создать кейс (админ)")
print("?case_random - создать рандомный кейс (админ)")
print("?gift @username/id - передать кейс/подписку")
print("\n⭐ Команды подписок (админ):")
print("?vip @username/id - выдать подписку V.I.P")
print("?premium @username/id - выдать PREMIUM")
print("?deluxe @username/id - выдать DELUXE")
print("?luxe @username/id - выдать LUXE")
print("?vip_perm @username/id - V.I.P навсегда")
print("?premium_perm @username/id - PREMIUM навсегда")
print("?deluxe_perm @username/id - DELUXE навсегда")
print("?luxe_perm @username/id - LUXE навсегда")
print("\n💰 СИСТЕМА БАНКА (ВАЖНО!):")
print("• 1 сообщение в чате = 1 Элит (наличные)")
print("• Лимит банка: 10,000 Элитов")
print("• Переводы идут на наличные")
print("• Команда 'Элиты' показывает только НАЛИЧНЫЕ")
print("• ВАЖНО: Система работает ТОЛЬКО так:")
print("  1. ?bank - открыть банк")
print("  2. Нажать 'Личное хранилище'")
print("  3. Нажать 'Снять' или 'Положить'")
print("  4. Ввести сумму в чат")
print("  5. Банк АВТОМАТИЧЕСКИ закрывается после операции!")
print("  6. После этого цифры в чате НЕ начисляются!")
print("• Для повторного открытия нужно снова ввести ?bank")
print("=" * 60)

start_expiry_checker()

def main():
    retry_count = 0
    max_retries = 5
    
    while True:
        try:
            print("\n🔍 Слушаем события...")
            for event in longpoll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW:
                    msg = event.obj.message
                    
                    class Event:
                        def __init__(self, msg):
                            self.text = msg['text']
                            self.from_id = msg['from_id']
                            self.peer_id = msg['peer_id']
                    
                    event_obj = Event(msg)
                    
                    # Сначала проверяем, не является ли сообщение числом для операций с банком
                    if handle_bank_operation(event_obj):
                        pass  # Операция с банком обработана и банк закрыт
                    # Затем обрабатываем команды
                    elif event_obj.text.startswith('?'):
                        handle_command(event_obj)
                    # Затем проверяем команду "Элиты"
                    elif event_obj.text.lower() == 'элиты':
                        # Переотправляем команду для обработки
                        event_obj.text = 'Элиты'
                        handle_command(event_obj)
                    # Иначе начисляем валюту за сообщение (ТОЛЬКО если пользователь не в активной сессии банка)
                    else:
                        # Проверяем, не находится ли пользователь в активной сессии банка
                        # Если находится, НЕ начисляем валюту
                        if not is_bank_session_active(event_obj.from_id, event_obj.peer_id):
                            handle_currency_message(event_obj.from_id, event_obj.peer_id)
                    
                    # Проверка и отправка новогоднего поздравления
                    send_new_year_greeting(msg['from_id'], msg['peer_id'], event_type='message_new')
                    
                elif event.type == VkBotEventType.MESSAGE_EVENT:
                    print(f"📨 Получено callback событие")
                    handle_callback(event)
            
            retry_count = 0
            
        except KeyboardInterrupt:
            print("\n🛑 Бот остановлен пользователем")
            break
        except Exception as e:
            retry_count += 1
            print(f"⚠️ Ошибка: {e}")
            
            if retry_count > max_retries:
                print("🔄 Слишком много ошибок. Перезапуск через 60 секунд...")
                time.sleep(60)
                retry_count = 0
            
            time.sleep(5)

if __name__ == "__main__":
    main()