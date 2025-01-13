import asyncio

from pyzbar.pyzbar import decode
from PIL import Image


async def decode_qr(image_path):
    def process_image():
        try:
            img = Image.open(image_path)

            return decode(img)
        except Exception as e:
            print(f"Ошибка при обработке изображения: {e}")
            return None

    return await asyncio.to_thread(process_image)

async def main():
    image_path = "qr-test.png"
    decoded_data = await decode_qr(image_path)

    if decoded_data:
        for obj in decoded_data:
            print(f"QR-код найден: {obj.data.decode()}")
    else:
        print("QR-код не найден.")

if __name__ == "__main__":
    asyncio.run(main())
