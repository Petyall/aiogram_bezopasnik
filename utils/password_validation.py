import re
import math
import asyncio


async def calculate_entropy(password):
    """Расчет энтропии пароля"""
    unique_chars = len(set(password))
    length = len(password)
    entropy = length * math.log2(unique_chars) if unique_chars > 1 else 0
    return entropy

async def is_strong_password(password):
    messages = []
    
    if len(password) < 12:
        messages.append(f'Ваш пароль слишком короткий! Рекомендуем использовать минимум 12 символов.')
    
    if not re.search(r'[a-z]', password):
        messages.append('Ваш пароль не содержит строчных букв, рекомендуем добавить их!')
    if not re.search(r'[A-Z]', password):
        messages.append('Ваш пароль не содержит прописных букв, рекомендуем добавить их!')
    
    if not re.search(r'\d', password):
        messages.append('Ваш пароль не содержит цифр, рекомендуем добавить их!')
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        messages.append('Ваш пароль не содержит специальных символов, рекомендуем добавить их!')
    
    if re.search(r'(.)\1{2,}', password):
        messages.append('Ваш пароль содержит повторяющиеся символы, постарайтесь избегать этого!')
    if re.search(r'(123|abc|qwe|йцу)', password, re.IGNORECASE):
        messages.append('Ваш пароль содержит простые последовательности символов, избегайте их!')
    
    entropy = await calculate_entropy(password)
    if entropy < 50:
        messages.append(f'Энтропия вашего пароля ({int(entropy)}) низкая, рекомендуется повысить его сложность.')

    if messages:
        return '\n'.join(messages)
    return 'Ваш пароль соответствует всем нормам криптостойкости!'

test = asyncio.run(is_strong_password(""))
print(test)
