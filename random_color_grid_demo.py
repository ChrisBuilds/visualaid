import random
from visualaid import Grid

rows = 5
cols = 5
grid = Grid(
    grid_x=5,
    grid_y=5,
    cell_width=40,
    cell_height=40,
    gridlines=True,
    gridline_width=1,
    frame_counter_text=True,
    bg_color=(0, 0, 0),
)
grid.frame_counter_text_color = (255, 255, 255)
grid.holdresult = 1000
cells = [(x, y) for y in range(rows) for x in range(cols)]
while cells:
    color = tuple(random.randrange(0, 255) for _ in range(3))
    grid.fill_cell(cells.pop(random.randrange(len(cells))), color)
    grid.gridline_color = color
    grid.save_frame()

grid.save_animation(filename="random_color_grid_demo.gif", duration=100)
