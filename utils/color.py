class ColorGradient:
    class ColorPoint:
        def __init__(self, red, green, blue, value):
            self.r = red
            self.g = green
            self.b = blue
            self.val = value

    def __init__(self):
        self._color = []
        self.create_default_heatmap_gradient()

    def add_color_point(self, red, green, blue, value):
        new_point = self.ColorPoint(red, green, blue, value)
        inserted = False
        for i, point in enumerate(self._color):
            if value < point.val:
                self._color.insert(i, new_point)
                inserted = True
                break
        if not inserted:
            self._color.append(new_point)

    def clear_gradient(self):
        self._color.clear()

    def create_default_heatmap_gradient(self):
        self._color.clear()
        self._color.append(self.ColorPoint(0, 0, 255, 0.0))  # Blue
        self._color.append(self.ColorPoint(0, 255, 255, 0.15))  # Cyan
        self._color.append(self.ColorPoint(0, 255, 0, 0.50))  # Green
        self._color.append(self.ColorPoint(255, 255, 0, 0.45))  # Yellow
        self._color.append(self.ColorPoint(255, 0, 0, 1.0))  # Red

    def get_color_at_value(self, value):
        if not self._color:
            return 0.0, 0.0, 0.0

        for i in range(len(self._color)):
            curr_c = self._color[i]
            if value < curr_c.val:
                prev_c = self._color[max(0, i - 1)]
                value_diff = prev_c.val - curr_c.val
                fract_between = 0 if value_diff == 0 else (value - curr_c.val) / value_diff
                red = (prev_c.r - curr_c.r) * fract_between + curr_c.r
                green = (prev_c.g - curr_c.g) * fract_between + curr_c.g
                blue = (prev_c.b - curr_c.b) * fract_between + curr_c.b
                return red, green, blue

        # If the value is beyond the last point
        last_point = self._color[-1]
        return last_point.r, last_point.g, last_point.b
