from random import randrange
from visualaid import Grid, Animator

rows = 5
cols = 5
grid = Grid(
    cols,
    rows,
    40,
    40,
    gridlines=True,
    gridline_width=1,
    frame_counter_text=True,
    bg_color=(0, 0, 0),
)
grid.frame_counter_text_color = (255, 255, 255)
grid.holdresult = 1000
cells = [(x, y) for y in range(rows) for x in range(cols)]
while cells:
    color = tuple(randrange(0, 255) for _ in range(3))
    grid.fill_cell(cells.pop(randrange(len(cells))), color)
    grid.gridline_color = color
    grid.save_frame()


g2 = Grid(
    10,
    10,
    40,
    40,
    gridlines=True,
    gridline_width=1,
    frame_counter_text=True,
    bg_color=(0, 0, 0),
)
g2.frame_counter_text_color = (255, 255, 255)
g2.holdresult = 1000
cells = [(x, y) for y in range(rows) for x in range(cols)]
while cells:
    color = tuple(randrange(0, 255) for _ in range(3))
    g2.fill_cell(cells.pop(randrange(len(cells))), color)
    g2.gridline_color = color
    g2.save_frame()

grids = [grid, g2]
anim = Animator()
anim.save_animation(grids, filename="test.apng", duration=100, holdresult=500)

# grid.save_animation(filename="random_color_grid_demo.apng", duration=100)
