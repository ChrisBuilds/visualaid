from PIL import Image, ImageDraw
from math import ceil
from io import BytesIO

# TODO: add custom text to frame counter (such as iterations/steps that are actually accurate)
#      Re-align coordinates to fit within grid (no negative)
#      find grid size that fits all given coordinates (auto-size grid)


class Grid:
    """
    Grid with x,y coordinate cells that can be colored. Grid can save an individual image or
    a sequence of images as an APNG or GIF.

    Attributes
    ----------
    grid_x : int
        number of cells in a row
    grid_y : int
        number of cells in a column
    cell_width : int
        width of each cell in pixels
    cell_height : int
        height of each cell in pixels
    gridlines : bool
        whether gridlines should be drawn between cells
    gridline_width : int
        width of gridlines in pixels
    gridline_color : tuple(red: int, green:int, blue: int)
        rgb value 0-255 for the gridline color
    bg_color : tuple(red: int, green:int, blue: int)
        rgb value 0-255 for the background color
    frame_counter_text : bool
        whether a frame counter will be displayed at the bottom of an animation

    Methods
    -------
    fill_cell(coord, fill=(0,0,0))
        Fills the cell at the (x,y) coordinate with the given rgb color.
    show_image()
        Displays the grid image in the OS default image viewer.
    save_image(filename="out.png")
        Save the current grid image to a file with given format and filename.
    save_frame()
        Saves the current frame to the frame list for use as an image sequence for animated gif/png
    show_frame(frame_num)
        Show the given frame using the OS default image viewer.
    save_animation(filename="out.apng", loop=0, duration=100, holdresult=0)
        Save all frames out to an animated image, default apng
    """

    def __init__(
        self,
        grid_x,
        grid_y,
        cell_width,
        cell_height,
        gridlines=False,
        gridline_width=1,
        gridline_color=(0, 0, 0),
        bg_color=(255, 255, 255),
        frame_counter_text=True,
        flip_vertical=False,
    ):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.cell_width = cell_width
        self.cell_height = cell_height
        self._gridlines = gridlines
        self.gridline_width = gridline_width
        self.gridline_color = gridline_color
        self.bg_color = bg_color
        self._frame_counter_text = frame_counter_text
        self.flip_vertical = flip_vertical
        self.frame_counter_text_color = (0, 0, 0)
        self.holdresult = 0
        self.grid_image_height = (self.grid_y * self.cell_height) + (
            (self._gridlines * (self.grid_y + 1)) * self.gridline_width
        )
        self.grid_image_width = (self.grid_x * self.cell_width) + (
            (self._gridlines * (self.grid_x + 1)) * self.gridline_width
        )
        self.frame_counter_text_height = (
            max(15, int(0.025 * self.grid_image_height)) * self._frame_counter_text
        )
        self.image_width = (
            self.grid_image_width + 0
        )  # 0 placeholder for potential side text
        self.image_height = self.grid_image_height + self.frame_counter_text_height

        self.colors = {
            "red": (255, 255, 0),
            "orange": (255, 128, 0),
            "yellow": (255, 255, 0),
            "green": (0, 255, 0),
            "cyan": (0, 255, 255),
            "blue": (0, 0, 255),
            "purple": (127, 0, 255),
            "magenta": (255, 0, 127),
            "black": (0, 0, 0),
            "gray": (128, 128, 128),
            "white": (255, 255, 255),
        }

        self.formats = ("gif", "png")

        self.image = Image.new(
            mode="RGB",
            size=(self.image_width, self.image_height),
            color=self.bg_color,
        )
        self.draw = ImageDraw.Draw(self.image)
        self.frames = []
        self.unprocesssed_frames = 0

    def _draw_gridlines(self):
        gridline_width_expansion = 0
        if self.gridline_width >= 3:
            gridline_width_expansion = ceil(self.gridline_width / 2) - 1

        for x in range(
            0 + gridline_width_expansion,
            self.grid_image_width + 1,
            self.cell_width + self.gridline_width,
        ):
            self.draw.line(
                ((x, 0), (x, self.grid_image_height - 1)),
                width=self.gridline_width,
                fill=self.gridline_color,
            )
        for y in range(
            0 + gridline_width_expansion,
            self.grid_image_height + 1,
            self.cell_height + self.gridline_width,
        ):
            self.draw.line(
                ((0, y), (self.grid_image_width - 1, y)),
                width=self.gridline_width,
                fill=self.gridline_color,
            )

    def _draw_image(self):
        if self._gridlines:
            self._draw_gridlines()

    def _draw_frame_counter_text(self, frame, text, frame_pos, total_fames):
        frame_counter_text_pos = (3, self.grid_image_height + 3)
        ImageDraw.Draw(frame).text(
            frame_counter_text_pos,
            f"{text} {frame_pos} / {total_fames}",
            fill=self.frame_counter_text_color,
        )
        return frame

    def fill_cell(self, coord, fill=(0, 0, 0)):
        x, y = coord
        if self.flip_vertical:
            y = (self.grid_y - 1) - (abs(y))

        gridspace = self._gridlines * self.gridline_width
        x0 = (x * self.cell_width) + (x * gridspace) + gridspace
        y0 = (y * self.cell_height) + (y * gridspace) + gridspace
        x1 = x0 + self.cell_width - 1
        y1 = y0 + self.cell_height - 1
        bbox = ((x0, y0), (x1, y1))
        self.draw.rectangle(bbox, fill)

    def show_image(self):
        self._draw_image()
        self.image.show()

    def save_image(self, filename="out.png"):
        self._draw_image()
        self.image.save(filename)

    def _create_bytesio_object(self, image_obj):
        """Return image as BytesIO object in memory"""
        byte_img = BytesIO()
        image_obj.save(byte_img, "PNG")
        return byte_img

    def save_frame(self):
        self._draw_image()
        self.frames.append(self._create_bytesio_object(self.image))

    def show_frame(self, frame_num):
        i = Image.frombytes(
            mode="RGB",
            size=(self.image_width, self.image_height),
            data=self.frames[frame_num],
        )
        i.show()

    def _frames_gen(self, holdframe_count):
        """Perform final processing on each frame before yielding it to save_animation"""
        processed_frames = 1
        total_frames = len(self.frames)
        for frame in self.frames:
            print(f"\rProcessing Frame {processed_frames} / {total_frames}", end="")
            frame_image = Image.open(frame)
            if self._frame_counter_text:
                # do not increment frame_pos text for hold frames
                frame_pos = (
                    processed_frames
                    if processed_frames <= total_frames - holdframe_count
                    else total_frames - holdframe_count
                )
                frame_image = self._draw_frame_counter_text(
                    frame_image,
                    "Frame: ",
                    frame_pos,
                    total_frames - holdframe_count,
                )
            processed_frames += 1
            yield frame_image

    def save_animation(self, filename="out.apng", loop=0, duration=100):
        """
        Save all frames to a supported animated file with type based on
        filename extension (default .apng).

        Parameters
        ----------
        filename : str
            Filename or pathlib.path object to save the file. Extension
            determines filetype. Supports .apng and .gif

        loop : int
            Number of times to loop the animation. 0 (default) = endless

        duration : int
            Duration in milliseconds to display each frame. default = 100ms

        holdresult : int
            Duration in miliseconds to display the final frame before looping. default = 0ms
        """
        # duplicate the final frame to fill the holdresult duration
        holdframe_count = int(self.holdresult / duration)
        for _ in range(holdframe_count):
            self.save_frame()
        frame_gen = self._frames_gen(holdframe_count)
        self.base_grid = next(frame_gen)
        self.base_grid.save(
            filename,
            save_all=True,
            append_images=frame_gen,
            loop=loop,
            duration=duration,
        )


class Animator:
    def __init__(self):
        self.hold_duration = 0
        self.frame_counter_text = False

    def save_animation(
        self,
        visuals,
        filename="out.apng",
        loop=0,
        duration=100,
        holdresult=0,
        resize=None,
    ):
        self.resize = resize
        holdframe_count = int(holdresult / duration)
        frame_gen = self._frames_gen(visuals, duration, holdframe_count)
        base_grid = next(frame_gen)
        base_grid.save(
            filename,
            save_all=True,
            append_images=frame_gen,
            loop=loop,
            duration=duration,
        )

    def _frames_gen(self, visuals, duration, holdframe_count):
        processed_frames = 1
        total_frames = 0
        if holdframe_count:
            for _ in range(holdframe_count):
                visuals[-1].save_frame()
        for visual in visuals:
            if not holdframe_count:
                if visual.holdresult:
                    visual_holdframe_count = int(visual.holdresult / duration)
                    for _ in range(visual_holdframe_count):
                        visual.save_frame()
            total_frames += len(visual.frames)

        for visual in visuals:
            for frame in visual.frames:
                print(f"\rProcessing Frame {processed_frames} / {total_frames}", end="")
                frame_image = Image.open(frame)
                if visual._frame_counter_text:
                    # do not increment frame_pos text for hold frames
                    frame_pos = (
                        processed_frames
                        if processed_frames <= total_frames - holdframe_count
                        else total_frames - holdframe_count
                    )
                    frame_image = visual._draw_frame_counter_text(
                        frame_image,
                        "Frame: ",
                        frame_pos,
                        total_frames - holdframe_count,
                    )
                processed_frames += 1
                if self.resize:
                    frame_image = frame_image.resize(self.resize, Image.NEAREST)
                yield frame_image


def align_coords(coords):
    """Adjust all coordinates such that x >= 0 and y >= 0"""
    min_x = min([coord[0] for coord in coords])
    min_y = min([coord[1] for coord in coords])
    x_adjust = abs(0 - min_x) if min_x < 0 else 0
    y_adjust = abs(0 - min_y) if min_y < 0 else 0
    print(f"min_x: {min_x}\nmin_y: {min_y}")
    return (x_adjust, y_adjust)


def main():
    pass


if __name__ == "__main__":
    main()
