import board

Pin = {
    "D13" : board.D13,
    "D12" : board.D12,
    "D11" : board.D11,
    "D10" : board.D10,
    "D9" : board.D9,
    "D6" : board.D6,
    "D5" : board.D5,
    "NEOPIXEL" : board.NEOPIXEL,
    "A5" : board.A5,
    "A4" : board.A4,
    "A3" : board.A3,
    "A2" : board.A2,
    "A1" : board.A1,
    "A0" : board.A0
}

def pin(p):
    return Pin[p]
