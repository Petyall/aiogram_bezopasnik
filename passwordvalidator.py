import re

async def is_strong_password(password):
    # проверка длины пароля (не менее 8 символов)
    if len(password) < 8:
        context = f'Ваш пароль слишком короткий! Рекомендуем добавить минимум {12 - len(password)} символов!'
        return context

    # проверка наличия букв в верхнем и нижнем регистре
    if not re.search(r'[a-z]', password) or not re.search(r'[A-Z]', password):
        context = 'В вашем пароле нет букв верхнего или нижнего регистра, рекомендуем добавить их!'
        return context

    # проверка наличия цифр
    if not re.search(r'\d', password):
        context = f'В вашем пароле нет цифр, рекомендуем добавить их!'
        return context

    # проверка наличия специальных символов
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        context = f'В вашем пароле нет специальных символов, рекомендуем добавить их!'
        return context
    
    context = 'Ваш пароль соответствует всем нормам!'
    return context
