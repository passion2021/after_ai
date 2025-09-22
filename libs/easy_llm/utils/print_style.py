import webcolors


class PrintStyle:
    def __init__(self, bold=False, italic=False, underline=False, font_color="default", background_color="default",
                 padding=False):
        self.bold = bold
        self.italic = italic
        self.underline = underline
        self.font_color = font_color
        self.background_color = background_color
        self.padding = padding

    def _get_rgb_color_code(self, color, is_background=False):
        try:
            if color.startswith("#") and len(color) == 7:
                r = int(color[1:3], 16)
                g = int(color[3:5], 16)
                b = int(color[5:7], 16)
            else:
                rgb_color = webcolors.name_to_rgb(color)
                r, g, b = rgb_color.red, rgb_color.green, rgb_color.blue

            if is_background:
                return f"\033[48;2;{r};{g};{b}m", f"background-color: rgb({r}, {g}, {b});"
            else:
                return f"\033[38;2;{r};{g};{b}m", f"color: rgb({r}, {g}, {b});"
        except ValueError:
            return "", ""

    def get_styled_text(self, text):
        start = ""
        end = "\033[0m"  # Reset ANSI code
        if self.bold:
            start += "\033[1m"
        if self.italic:
            start += "\033[3m"
        if self.underline:
            start += "\033[4m"
        font_color_code, _ = self._get_rgb_color_code(self.font_color)
        background_color_code, _ = self._get_rgb_color_code(self.background_color, True)
        start += font_color_code
        start += background_color_code
        return start + text + end

    def print(self, text):
        print(self.get_styled_text(text), end='')
        if self.padding:
            print()


prefix_font = PrintStyle(font_color="green")
ai_font = PrintStyle(italic=True, font_color="#b3ffd9", )
warning_font = PrintStyle(font_color="orange", padding=True)
error_font = PrintStyle(font_color="palevioletred", padding=True)
