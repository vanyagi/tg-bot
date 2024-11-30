import asyncio
from pyppeteer import launch


async def get_titles_from_google_custom_search(query):
    """
    Выполняет поиск по заданному запросу и возвращает заголовки первых 5 результатов.
    :param query: Строка с поисковым запросом.
    :return: Список заголовков результатов поиска.
    """
    browser = await launch(headless=True, executablePath='C:/Program Files (x86)/chrome-win/chrome.exe')
    page = await browser.newPage()
    await page.goto('https://cse.google.com/cse?cx=83834425a81e4459d')

    search_input_selector = '#gsc-i-id1'
    await page.type(search_input_selector, query)
    search_button_selector = '.gsc-search-button .gsc-search-button-v2'
    await page.click(search_button_selector)
    await page.waitForSelector('.gsc-webResult .gs-title a')

    titles = await page.evaluate('''() => {
        return Array.from(document.querySelectorAll('.gsc-webResult .gs-title a'))
            .map(title => title.innerText)
            .slice(0, 5);
    }''')

    await browser.close()
    return titles


async def fetch_website_content(title):
    """
    Выполняет переход по заголовку и возвращает URL и контент страницы.
    :param title: Заголовок выбранного результата.
    :return: Кортеж (url, content).
    """
    browser = None
    try:
        browser = await launch(headless=True, executablePath='C:/Program Files (x86)/chrome-win/chrome.exe')
        page = await browser.newPage()

        # Переход к Google Custom Search
        await page.goto('https://cse.google.com/cse?cx=83834425a81e4459d')

        # Ввод заголовка в поле поиска
        search_input_selector = '#gsc-i-id1'
        await page.type(search_input_selector, title)
        search_button_selector = '.gsc-search-button .gsc-search-button-v2'
        await page.click(search_button_selector)
        await page.waitForSelector('.gsc-webResult .gs-title a')

        # Клик по первой ссылке
        first_link = await page.querySelector('.gsc-webResult .gs-title a')
        if first_link:
            await first_link.click()
        else:
            return None, "Не удалось найти ссылку."

        # Ожидание загрузки страницы
        await page.waitForSelector('.s-prose.js-post-body', {'timeout': 60000})

        # Получение URL
        url = page.url

        # Извлечение содержимого страницы
        content = await page.evaluate(
            '() => { const el = document.querySelector(".s-prose.js-post-body"); return el ? el.innerText : "Контент не найден"; }')

        return url, content

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None, "Произошла ошибка при извлечении данных."
    finally:
        if browser:
            await browser.close()
