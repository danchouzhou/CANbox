import time
import json
import asyncio
import board
import neopixel
import canio
from pin import pin

# Load the config file
f = open ('config.json', "r")
config = json.loads(f.read())
f.close()

# Initialize CAN bus
can = canio.CAN(rx=board.CAN_RX, tx=board.CAN_TX, baudrate=500_000, auto_restart=True)
listener = can.listen(timeout=0)
old_bus_state = None
old_count = -1

async def blink(pin):
    try:
        with neopixel.NeoPixel(pin, 10, brightness=0.5, auto_write=True, pixel_order=neopixel.GRB) as pixels:
            pixels.fill((255, 90, 0))
            await asyncio.sleep(0.40)
            pixels.fill((0, 0, 0))
            await asyncio.sleep(0.45)
    except Exception as e:
        #print(e)
        return
            
        
async def TurnLightReq(group):
    tasks = []
    for port_use in group['ports']:
        for port in config['ports']:
            if port_use == port['name']:
                tasks.append(asyncio.create_task(blink(pin(port['pin1']))))
    await asyncio.gather(*tasks)
#     print('end time', time.monotonic())
#     print()

def flush_rx(listener):
    message = listener.receive()
    while(message is not None):
        message = listener.receive()

func_callback = {
    "HazardWarningReq" : TurnLightReq,
    "RightTurnLightReq" : TurnLightReq,
    "LeftTurnLightReq" : TurnLightReq
}

while True:
    try:
        #print(time.monotonic())
        bus_state = can.state
        if bus_state != old_bus_state:
            print(f"Bus state changed to {bus_state}")
            old_bus_state = bus_state
        
        message = listener.receive()
        if message is None:
    #         print("No messsage received within timeout")
            continue
        else:
            for group in config['groups']:
                if message.id == group['id'] and message.data == bytearray(group['data']):
                    asyncio.run(func_callback[group['name']](group))
        
        flush_rx(listener) # Clear RX buffer
    except KeyboardInterrupt:
        can.deinit()
        break
