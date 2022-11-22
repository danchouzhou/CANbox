import time
import json
import board
import neopixel
import canio
from pin import pin

# Load the config file
f = open ('config.json', "r")
config = json.loads(f.read())
f.close()

# Use this line if your board has dedicated CAN pins. (Feather M4 CAN and Feather STM32F405)
can = canio.CAN(rx=board.CAN_RX, tx=board.CAN_TX, baudrate=500_000, auto_restart=True)
listener = can.listen(timeout=.9)

def blink(pin):
    with neopixel.NeoPixel(pin, 1, brightness=0.5, auto_write=True, pixel_order=neopixel.GRB) as pixels:
        pixels.fill((255, 90, 0))
        #pixels.show()
        time.sleep(0.35)
        pixels.fill((0, 0, 0))
        #pixels.show()
        time.sleep(0.45)

old_bus_state = None
old_count = -1

while True:
    bus_state = can.state
    if bus_state != old_bus_state:
        print(f"Bus state changed to {bus_state}")
        old_bus_state = bus_state
        
    
    message = listener.receive()
    if message is None:
        print("No messsage received within timeout")
        continue
    else:
        for group in config['groups']:
            if message.id == group['id']:
                if message.data == bytearray(group['data']):
                    blink(pin("board.NEOPIXEL"))
    
