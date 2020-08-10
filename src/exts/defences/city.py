import enum

from PIL import Image, ImageFont, ImageDraw


CELL_SIZE = 120


class Buildings(enum.IntEnum):
	WALL = 0
	CASTLE = 1
	WATER = 2


def build_city_image(buildings: list):
	def enum_to_text(e):
		return e.name

	image = Image.new(mode='RGBA', size=(600, 600), color="#2f3136")

	draw = ImageDraw.Draw(image)

	for x in range(0, image.width, CELL_SIZE):
		line = ((x, 0), (x, image.height))
		draw.line(line, fill=128)

	for y in range(0, image.height, CELL_SIZE):
		line = ((0, y), (image.width, y))
		draw.line(line, fill=128)

	draw = ImageDraw.Draw(image)

	index = 0

	lbl_font = ImageFont.truetype("arial.ttf", 11)
	cell_font = ImageFont.truetype("arial.ttf", 16)

	for y in range(0, image.height, CELL_SIZE):
		for x in range(0, image.width, CELL_SIZE):
			# - Draw Label
			draw.text((x + 5, y + 5), str(index + 1), align="left", font=lbl_font)

			# - Draw Cell
			txt = enum_to_text(buildings[index])

			w, h = draw.textsize(txt, font=cell_font)

			center = (x + (CELL_SIZE // 2) - w // 2, y + (CELL_SIZE // 2) - h // 2)

			draw.text(center, txt, align="center", font=cell_font)

			index += 1

	return image
