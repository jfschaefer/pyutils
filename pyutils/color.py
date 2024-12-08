from __future__ import annotations


def _hue(r: float, g: float, b: float) -> float:
    max_val = max(r, g, b)
    min_val = min(r, g, b)
    delta = max_val - min_val
    if delta == 0:
        h = 0.0
    elif max_val == r:
        h = (g - b) / delta
    elif max_val == g:
        h = 2 + (b - r) / delta
    else:  # b
        h = 4 + (r - g) / delta
    h *= 60
    if h < 0:
        h += 360
    return h


class Color:  # considered immutable
    __slots__ = ['_r', '_g', '_b', '_a']

    def __init__(self, r: float, g: float, b: float, a: float = 1.0):
        assert 0.0 <= r <= 1.0 and 0.0 <= g <= 1.0 and 0.0 <= b <= 1.0 and 0.0 <= a <= 1.0
        self._r = r
        self._g = g
        self._b = b
        self._a = a

    # ALTERNATIVE CONSTRUCTORS

    @classmethod
    def from_rbg256(cls, r: float, g: float, b: float, a: float = 1.0) -> Color:
        if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255 and 0.0 <= a <= 1.0):
            raise ValueError('r, g, b must be in the range [0, 255] and in the range [0, 1] for a')
        return cls(r / 255, g / 255, b / 255, a)

    @classmethod
    def from_hsv(cls, h: float, s: float, v: float, a: float = 1.0) -> Color:
        if not (0.0 <= s <= 1.0 and 0.0 <= v <= 1.0 and 0.0 <= a <= 1.0):
            raise ValueError('s, v and a must be in the range [0, 1]')

        def f(n):
            k = (n + h / 60) % 6
            return v - v * s * max(min(k, 4 - k, 1), 0)

        return cls(f(5), f(3), f(1))

    @classmethod
    def from_hsl(cls, h: float, s: float, l: float, a: float = 1.0) -> Color:
        if not (0.0 <= s <= 1.0 and 0.0 <= l <= 1.0 and 0.0 <= a <= 1.0):
            raise ValueError('s, l and a must be in the range [0, 1]')

        def f(n):
            k = (n + h / 30) % 12
            return l - (s * min(l, 1 - l)) * max(min(k - 3, 9 - k, 1), -1)

        return cls(f(0), f(8), f(4))

    # MODIFIERS

    def with_alpha(self, a: float) -> Color:
        if not 0.0 <= a <= 1.0:
            raise ValueError('a must be in the range [0, 1]')
        return Color(self._r, self._g, self._b, a)

    def with_r(self, r: float) -> Color:
        return Color(r, self._g, self._b, self._a)

    def with_g(self, g: float) -> Color:
        return Color(self._r, g, self._b, self._a)

    def with_b(self, b: float) -> Color:
        return Color(self._r, self._g, b, self._a)

    def with_r256(self, r: float) -> Color:
        return Color(r / 255, self._g, self._b, self._a)

    def with_g256(self, g: float) -> Color:
        return Color(self._r, g / 255, self._b, self._a)

    def with_b256(self, b: float) -> Color:
        return Color(self._r, self._g, b / 255, self._a)

    def with_hue(self, h: float) -> Color:
        hsv = self.hsv
        return Color.from_hsv(h, hsv[1], hsv[2], self._a)

    def with_hsv_saturation(self, s: float) -> Color:
        hsv = self.hsv
        return Color.from_hsv(hsv[0], s, hsv[2], self._a)

    def with_hsv_value(self, v: float) -> Color:
        hsv = self.hsv
        return Color.from_hsv(hsv[0], hsv[1], v, self._a)

    def with_hsl_saturation(self, s: float) -> Color:
        hsl = self.hsl
        return Color.from_hsl(hsl[0], s, hsl[2], self._a)

    def with_hsl_lightness(self, l: float) -> Color:
        hsl = self.hsl
        return Color.from_hsl(hsl[0], hsl[1], l, self._a)

    # PROPERTIES

    def approx_eq(self, other: Color, *, tolerance: float = 1e-6, ignore_alpha: bool = False) -> bool:
        if (
                abs(self._r - other._r) > tolerance
                or abs(self._g - other._g) > tolerance
                or abs(self._b - other._b) > tolerance
        ):
            return False
        if ignore_alpha:
            return True
        return abs(self._a - other._a) <= tolerance

    @property
    def r(self) -> float:
        return self._r

    @property
    def g(self) -> float:
        return self._g

    @property
    def b(self) -> float:
        return self._b

    @property
    def a(self) -> float:
        return self._a

    @property
    def r256i(self) -> int:
        return round(self._r * 255)

    @property
    def g256i(self) -> int:
        return round(self._g * 255)

    @property
    def b256i(self) -> int:
        return round(self._b * 255)

    @property
    def hue(self) -> float:
        return self.hsv[0]

    @property
    def hsv(self) -> tuple[float, float, float]:
        r, g, b = self._r, self._g, self._b
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        delta = max_val - min_val
        h = _hue(r, g, b)
        s = delta / max_val
        v = max_val
        return h, s, v

    @property
    def hsl(self) -> tuple[float, float, float]:
        r, g, b = self._r, self._g, self._b
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        delta = max_val - min_val
        h = _hue(r, g, b)
        l = (max_val + min_val) / 2
        if l == 0 or l == 1:
            s = 0.0
        else:
            s = delta / (1 - abs(2 * l - 1))
        return h, s, l
