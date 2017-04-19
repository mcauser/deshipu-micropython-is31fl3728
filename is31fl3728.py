class Matrix8x8:
    ROWS = (0, 1, 2, 3, 4, 5, 6, 7)
    COLS = (0, 1, 2, 3, 4, 5, 6, 7)

    def __init__(self, i2c, address=0x60):
        self.i2c = i2c
        self.address = address
        self.buffer = bytearray(8)

    def _register(self, register, value=None):
        if value is None:
            return self.i2c.readfrom_mem(self.address, register, 1)[0]
        self.i2c.writeto_mem(self.address, register, bytearray([value]))

    def fill(self, color=1):
        color = 0xff if color else 0x00
        for y in range(8):
            self.buffer[y] = color

    def pixel(self, x, y, color=1):
        if not (0 <= x <= 7 and 0 <= y <= 7):
            return
        if color:
            self.buffer[ROWS[y]] |= 0x01 << COLS[x]
        else:
            self.buffer[ROWS[y]] &= ~(0x01 << COLS[x])

    def show(self):
        for y, row in enumerate(self.buffer):
            self._register(0x01 + y, row)
        self._register(0x0c, 0xff)

    def brightness(self, value):
        if (0 <= value <= 6):
            self._register(0x0d, 0x1000 | value)
        elif (7 <= value <= 14):
            self._register(0x0f, value - 7)
        else:
            raise ValueError("out of range")
