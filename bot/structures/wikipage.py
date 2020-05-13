import enum
import discord


class SectionType(enum.IntEnum):
    HEADER = 0
    TEXT = 1


class WikiPage:
    def __init__(self, title: str, desc: str, url: str):
        self._title = title
        self._desc = desc
        self._url = url

        self._text = []
        self._tags = []

        self._prev_tag = None

    def add_header(self, header: str, text: str):
        if header == "h2":
            text = f"\n\n**{text}**\n"

        elif header == "h3":
            text = f"\n\n**{text}**"

        elif header == "h4":
            text = f"\n\n__{text}__\n" if self._prev_tag == "p" else f"\n__{text}__\n"

        self._text.append(text)
        self._tags.append(SectionType.HEADER)

        self._prev_tag = header

    def add_text(self, text: str):
        if self._prev_tag == "text":
            self._tags.pop(-1)

            text = "\n".join([self._text.pop(-1), text])

        self._text.append(text)
        self._tags.append(SectionType.TEXT)

        self._prev_tag = "text"

    def get_embeds(self):
        page_text = ""
        embeds = []
        length = 0

        sections = self._create_sections()

        num_sections = len(sections)

        for i, section in enumerate(sections):
            section_text = "".join(section)
            section_length = len(section_text)

            if length + section_length > 1024:
                embeds.append(self._create_embed(page_text))

                length = section_length
                page_text = section_text

            else:
                length += section_length
                page_text += section_text

                if i + 1 >= num_sections and page_text:
                    embeds.append(self._create_embed(page_text))

        return embeds

    def _create_sections(self):
        sections = [[]]

        for i, tag in enumerate(self._tags):
            text = self._text[i]

            if sections[-1] and tag == SectionType.HEADER:
                sections.append([])

            sections[-1].append(text)

        return sections

    def _create_embed(self, text):
        embed = discord.Embed(
            title=f"{self._title}",
            description=self._desc,
            url=self._url,
            color=0xff8000
        )

        embed.add_field(name=self._title, value=text)

        return embed

