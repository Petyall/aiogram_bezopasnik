import cv2
from pyzbar import pyzbar


# ФУНКЦИЯ РАСШИФРОВКИ QR
async def qrreader(file):
    # ПОПЫТКА РАСШИФРОВКИ
    try:
        # ЧТЕНИЕ ФАЙЛА
        img = cv2.imread(file)
        # РАСШИФРОВКА
        barcodes = pyzbar.decode(img)
        # ЕСЛИ ЗНАЧЕНИЯ В QR СУЩЕСТВУЮТ, ТО В context ЗАНЕСЕТСЯ ТЕКСТ QR-КОДА
        if barcodes:
            for barcode in barcodes:
                context = barcode.data.decode('utf-8')
        # ИНАЧЕ ВЫВЕДЕТСЯ ОШИБКА
        else:
            context = 'Я не смог распознать qr код на вашей фотографии :('
    # ЕСЛИ ПО КАКОЙ-ТО ПРИЧИНЕ РАСШИФРОВАТЬ НЕ ПОЛУЧИЛОСЬ, ВЫВЕДЕТСЯ ОШИБКА
    except:
        context = 'Произошла непредвиденная ошибка, сообщите моему создателю @petyal :('
    # ВОЗВРАТ РЕЗУЛЬТАТА
    return(context)