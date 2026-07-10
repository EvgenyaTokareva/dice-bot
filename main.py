import json
import os
from vk_utils import send_message, get_user_name
from dice_parser import DiceParser

# Создаем экземпляр парсера
parser = DiceParser()

def handler(event, context):
    """
    Главная функция для Yandex Cloud Functions / Netlify Functions
    """
    try:
        # 1. Получаем данные от VK (Callback API)
        body = json.loads(event['body'])
        
        # Проверяем секретный ключ (если настроен)
        # secret = event.get('headers', {}).get('x-secret-key')
        # if secret != os.environ.get('VK_SECRET_KEY'):
        #     return {'statusCode': 403, 'body': 'Forbidden'}
        
        # 2. Проверяем тип события
        if body.get('type') == 'confirmation':
            # Для VK Callback API нужно вернуть confirmation code
            return {
                'statusCode': 200,
                'body': os.environ.get('VK_CONFIRMATION_CODE', 'confirmation_code_here')
            }
        
        if body.get('type') == 'message_new':
            # 3. Обрабатываем новое сообщение
            message_data = body.get('object', {}).get('message', {})
            user_id = message_data.get('from_id')
            peer_id = message_data.get('peer_id')
            text = message_data.get('text', '').lower()
            
            if not user_id or not peer_id:
                return {'statusCode': 200, 'body': 'ok'}
            
            # Получаем имя пользователя
            user_name = get_user_name(user_id)
            
            # 4. Обрабатываем команды
            if text.startswith('/'):
                try:
                    result = parser.parse_expression(text)
                    response = f"{user_name}, {result}"
                    send_message(peer_id, response)
                except Exception as e:
                    send_message(peer_id, f"Ошибка в команде: {e}")
            
            elif text == 'привет':
                send_message(peer_id, f'Привет, {user_name}! Я бот для игры в кубики!')
            
            elif text == 'помощь':
                help_text = (
                    '📚 Доступные команды:\n'
                    '/d или /к - бросок 20-гранника\n'
                    '/d% или /к% - бросок процентной кости\n'
                    '/XdY - бросок X кубиков с Y гранями\n'
                    '/XdY+M - бросок с модификатором\n'
                    '/dad или /dпре - преимущество\n'
                    '/dis или /dпом - помеха\n'
                    '/d! - взрывающийся кубик\n'
                    '/f или /fate - FATE кубики\n'
                    '/XdYdhN - отбросить N наибольших\n'
                    '/XdYdlN - отбросить N наименьших\n'
                    '/XdYkhN - сохранить N наибольших\n'
                    '/XdYklN - сохранить N наименьших\n'
                    '/XdYres - бросок с сопротивлением\n'
                    'Примеры: /4d6, /d20+5, /10d6kh4'
                )
                send_message(peer_id, help_text)
            
            elif text == 'пока':
                send_message(peer_id, f'Пока, {user_name}!')
        
        # 5. Возвращаем успешный ответ
        return {
            'statusCode': 200,
            'body': 'ok'
        }
    
    except Exception as e:
        print(f"Ошибка: {e}")
        return {
            'statusCode': 500,
            'body': f'Error: {str(e)}'
        }