class Matrix8x8:
    ROWS = (7, 6, 1, 2, 0, 3, 4, 5)
    COLS = (0, 4, 1, 5, 7, 2, 6, 3)

    def __init__(self, i2c, address=0x60):
        self.i2c = i2c
        self.address = address
        self.buffer = bytearray(8)
        self._i2c_buffer = bytearray(1)
        self._effect_register = 0
        self._config_register = 0
        self._equalizer_register = 0

    def _register(self, register, value):
        self._i2c_buffer[0] = value
        self.i2c.writeto_mem(self.address, register, self._i2c_buffer)

    def fill(self, color=1):
        color = 0xff if color else 0x00
        for y in range(8):
            self.buffer[y] = color

    def pixel(self, x, y, color=None):
        if not (0 <= x <= 7 and 0 <= y <= 7):
            return
        if color is None:
            return bool(self.buffer[ROWS[y]] & (0x01 << COLS[x]))
        elif color:
            self.buffer[ROWS[y]] |= 0x01 << COLS[x]
        else:
            self.buffer[ROWS[y]] &= ~(0x01 << COLS[x])

    def show(self):
        for y, row in enumerate(self.buffer):
            self._register(0x01 + y, row)
        self._register(0x0c, 0xff)

    def brightness(self, value):
        if value is None:
            value = self._effect_register & 0x0f
            if value & 0b1000:
                value &= 0b0111
            else:
                value += 7
            return value
        elif (0 <= value <= 6):
            self._effect_register = (
                self._effect_register & ~0x0f | (0b1000 | value) & 0x0f)
        elif (7 <= value <= 14):
            self._effect_register = (
                self._effect_register & ~0x0f | (value - 7) & 0x0f)
        else:
            raise ValueError("out of range")
        self._register(0x0d, self._effect_register)

    def active(self, value=None):
        if value is None:
            return bool(self._config_register & 0x80)
        if value:
            self._config_register |= 0x80
        else:
            self._config_register &= ~0x80
        self._register(0x00, self._config_register)

    def equalizer_enabled(self, value=None):
        if value is None:
            return bool(self._equalizer_register & 0x40)
        if value:
            self._equalizer_register |= 0x40
        else:
            self._equalizer_register &= ~0x40
        self._register(0x0f, self._equalizer_register)

    def audio_enabled(self, value=None):
        if value is None:
            return bool(self._config_register & 0x04)
        if value:
            self._config_register |= 0x04
        else:
            self._config_register &= ~0x04
        self._register(0x00, self._config_register)

    def audio_gain(self, value=None):
        if value is None:
            return (self._effect_register & 0x70) >> 4
        elif not (0 <= value <= 7):
            raise ValueError("out of range")
        self._effect_register = (
            self._effect_register & ~0x70 | (value << 4) & 0x70)
        self._register(0x0d, self._effect_register)
