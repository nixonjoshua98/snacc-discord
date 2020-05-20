import requests

from bs4 import BeautifulSoup

from bot.structures.wikipage import WikiPage


class Wiki:
    __cache = {}

    def __init__(self, path: str):
        self.path = path
        self.url = f"https://autobattlesonline.fandom.com/wiki/{path}"

    def get(self):
        def remove_junk(d):
            ls = []

            for e in d:
                if e.text.strip().lower() in {"\n", "contents", ""}:
                    continue

                ls.append(e)

            return ls

        content = self._get_page_content()

        soup = BeautifulSoup(content, "html.parser")

        data = soup.find_all(lambda tag: tag.name in {"p", "h1", "h2", "h3", "h4", "h5"})
        data = remove_junk(data[:-8])

        title, desc, start_index = self._get_title_desc(data)

        wiki_page = WikiPage(title, desc, self.url)

        for ele in data[start_index:]:
            text = ele.text.strip()
            text = text.replace("[edit | edit source]", "")

            if ele.name in {"h1", "h2", "h3", "h4", "h5"}:
                wiki_page.add_header(ele.name, text)

            elif ele.name == "p":
                wiki_page.add_text(text)

        return wiki_page.get_embeds()

    @staticmethod
    def _get_title_desc(data):
        title, desc, i = None, None, 0

        for i in range(len(data) - 1):
            title, desc = data[i], data[i + 1]

            if title.name == "h1" and desc.name == "p":
                title, desc = title.text, desc.text
                break

        return title, desc, i + 2

    def _get_page_content(self):
        if Wiki.__cache.get(self.path, None) is None:
            r = requests.get(self.url)

            Wiki.__cache[self.path] = r.content

        return Wiki.__cache[self.path]
