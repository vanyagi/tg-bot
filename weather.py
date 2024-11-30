import asyncio
from pyppeteer import launch

async def fetch_website_content(query):
    browser = None
    try:
        # Запуск браузера
        browser = await launch(headless=True, executablePath='C:/Program Files (x86)/chrome-win/chrome.exe')
        page = await browser.newPage()

        # Переход к Google
        await page.goto('https://cse.google.com/cse?cx=83834425a81e4459d')

        # Явное ожидание поля ввода
        search_input_selector = '#gsc-i-id1'  # Селектор для поля поиска
        await page.type(search_input_selector, query)

        # Нажатие кнопки поиска
        search_button_selector = '.gsc-search-button .gsc-search-button-v2'
        await page.click(search_button_selector)

        # Ожидание появления результатов
        await page.waitForSelector('.gsc-webResult .gs-title a')

        # Клик по первой ссылке
        first_link = await page.querySelector('.gsc-webResult .gs-title a')
        if first_link:
            await first_link.click()
        else:
            print("Не удалось найти первую ссылку.")

        # Ожидание загрузки страницы
        try:
            await page.waitForSelector('.s-prose.js-post-body', {'timeout': 60000})  # Ждать до 60 секунд
        except Exception as e:
            print("Элемент не найден, ошибка:", e)
        url = page.url
        print(url)
        # Извлечение содержимого страницы
        content = await page.evaluate('() => { const el = document.querySelector(".s-prose.js-post-body"); return el ? el.innerText : "Контент не найден"; }')

        return content  # Возврат извлеченного содержимого

    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        if browser:
            await browser.close()  # Закрытие браузера в блоке finally

# Пример использования
if __name__ == "__main__":
    query = "What does @ mean in python programming language?"  # Ваш запрос
    content = asyncio.run(fetch_website_content(query))
    if content:
        print(content)  # Вывод содержимого сайта
