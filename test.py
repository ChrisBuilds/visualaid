import visualaid, queue


grid = visualaid.Grid(
    20,
    20,
    40,
    40,
    frame_counter_text=True,
    bg_color=(255, 255, 255),
    gridlines=True,
    gridline_color=(0, 0, 0),
)
grid.holdresult = 1500

target = (12, 17)
start = (1, 1)
frontier = queue.PriorityQueue()
frontier.put((0, start))
path = {start: None}
grid.fill_cell(target, fill=(100, 0, 0))
grid.fill_cell(start, fill=(0, 100, 0))
grid.save_frame()
while not frontier.empty():
    next_pos = frontier.get()[1]
    if next_pos == target:
        break
    grid.fill_cell(next_pos, fill=(255, 0, 0))
    grid.save_frame()
    for cell in grid.neighbors(next_pos, diag=False):
        if cell not in path:
            distance = abs(cell[0] - target[0]) + abs(cell[1] - target[1])
            frontier.put((distance, cell))
            grid.fill_cell(cell, fill=(0, 0, 255))
            path[cell] = next_pos

final_path = []
cell = target
while cell != start:
    cell = path[cell]
    final_path.append(cell)
final_path.append(start)
for cell in final_path[::-1]:
    grid.fill_cell(cell, fill=(0, 255, 0))
    grid.save_frame()

grid.save_animation()
