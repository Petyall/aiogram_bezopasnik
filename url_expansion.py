import asyncio
import urllib.request

from unshortenit import UnshortenIt

async def get_long_url_with_urllib(short_url):
    def resolve_url():
        try:
            response = urllib.request.urlopen(url=short_url, timeout=15)
            return response.geturl()
        except Exception as e:
            print(f'Ошибка при попытке раскрыть короткую ссылку через urllib: {e}')
            return None

    return await asyncio.to_thread(resolve_url)

async def get_long_url_with_unshortenit(short_url):
    try:
        unshortener = UnshortenIt()
        return unshortener.unshorten(short_url)
    except Exception as e:
        print(f'Ошибка при попытке раскрыть короткую ссылку через UnshortenIt: {e}')
        return None

async def get_long_url(short_url):
    long_url = await get_long_url_with_urllib(short_url)
    if long_url:
        return long_url

    long_url = await get_long_url_with_unshortenit(short_url)
    if long_url:
        return long_url

    raise ValueError("Не удалось дешифровать ссылку ни одним из методов.")

async def main():
    short_url = 'https://clck.ru/3Fg9Sn'
    try:
        long_url = await get_long_url(short_url)
        print(f'Длинный URL: {long_url}')
    except ValueError as e:
        print(e)

if __name__ == "__main__":
    asyncio.run(main())
