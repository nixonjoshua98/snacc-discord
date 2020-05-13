import requests
import dataclasses

from bs4 import BeautifulSoup


@dataclasses.dataclass(frozen=True)
class WikiPage:
    title: str
    desc: str

    pages: list


class Wiki:
    __cache = {}

    def __init__(self, path: str):
        self.path = path
        self.url = f"https://autobattlesonline.fandom.com/wiki/{path}"

    def get(self) -> WikiPage:
        def generator(d):
            for ele in d:
                yield ele

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

        pages = [[]]

        prev_tag = None

        for ele in data[start_index:]:
            text = ele.text.strip()
            text = text.replace("[edit | edit source]", "")
            text = text.replace("Base Description:", "")

            page = pages[-1]

            if ele.name == "h2":
                page.append(f"\n\n**{text}**\n")

            elif ele.name == "h3":
                page.append(f"\n\n**{text}**")

            elif ele.name == "h4":
                if prev_tag == "p":
                    page.append(f"\n\n__{text}__\n")
                else:
                    page.append(f"\n__{text}__\n")

            elif ele.name == "p":
                # Join the new text with the old text
                if prev_tag == ele.name:
                    page[-1] = "\n".join([page[-1], text])
                else:
                    page.append(text)

            prev_tag = ele.name

        return WikiPage(title=title, desc=desc, pages=pages)

    @staticmethod
    def _get_title_desc(data):
        title, desc, i = None, None, 0

        for i in range(len(data) - 1):
            title, desc = data[i], data[i + 1]

            if title.name == "h1" and desc.name == "p":
                title, desc = title.text, desc.text
                break

        return title, desc, i

    def _get_page_content(self):
        if Wiki.__cache.get(self.path, None) is None:
            r = requests.get(self.url)

            Wiki.__cache[self.path] = r.content

        return Wiki.__cache[self.path]
