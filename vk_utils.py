import vk_api
import os

# Получаем токен из переменных окружения
VK_TOKEN = os.environ.get('VK_TOKEN')

def send_message(peer_id, text):
    """Отправляет сообщение через VK API"""
    try:
        vk_session = vk_api.VkApi(token=VK_TOKEN)
        vk = vk_session.get_api()
        vk.messages.send(
            peer_id=peer_id,
            message=text,
            random_id=0
        )
        return True
    except Exception as e:
        print(f"Ошибка отправки: {e}")
        return False

def get_user_name(user_id):
    """Получает имя пользователя по ID"""
    try:
        vk_session = vk_api.VkApi(token=VK_TOKEN)
        vk = vk_session.get_api()
        user_info = vk.users.get(user_ids=user_id)
        return f"{user_info[0]['first_name']} {user_info[0]['last_name']}"
    except:
        return f'Пользователь {user_id}'