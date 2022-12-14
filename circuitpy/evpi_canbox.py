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

async def blink(pin):
    try:
        with neopixel.NeoPixel(pin, 144, brightness=1.0, auto_write=True, pixel_order=neopixel.GRB) as pixels:
            pixels.fill((255, 75, 2))
            await asyncio.sleep(0.45)
            pixels.fill((0, 0, 0))
            await asyncio.sleep(0.45)
    except Exception as e:
        #print(e)
        return

async def blink_faded(pin):
    # Design Without Compromise: Signals from the Heart | Mazda Stories
    # https://mazdastories.com/en_us/innovate/design-without-compromise-signals-from-the-heart/
    try:
        with neopixel.NeoPixel(pin, 144, brightness=1.0, auto_write=True, pixel_order=neopixel.GRB) as pixels:
            # Fade in
            seq = [x/2 for x in range(0, 3)]
            for i in seq:
                pixels.fill((255*i, 75*i, 2*i))
                await asyncio.sleep(0.01)
            await asyncio.sleep(0.35)
            # Fade out
            seq = [x/10 for x in range(10, -1, -1)]
            for i in seq:
                pixels.fill((255*i, 75*i, 2*i))
                await asyncio.sleep(0.01)
            await asyncio.sleep(0.35)
    except Exception as e:
        #print(e)
        return

async def HazardWarningReq(group):
    for port_use in group['ports']:
        for port in config['ports']:
            if port_use == port['name']:
                 asyncio.create_task(blink(pin(port['pin1'])))
#     print('end time', time.monotonic())
#     print()

async def TurnLightReq(group):
    for port_use in group['ports']:
        for port in config['ports']:
            if port_use == port['name']:
                 asyncio.create_task(blink_faded(pin(port['pin1'])))
#     print('end time', time.monotonic())
#     print()

brake_task = None
brake_off_task = None

async def brake_off_timer():
    global brake_task
    try:
        await asyncio.sleep(0.2)
        brake_task.cancel()
        brake_task = None
    except asyncio.CancelledError:
        return
    except Exception as e:
        #print(e)
        return

async def brake_on(group):
    pixels_list = []
    color = (255, 18, 0)
    try:
        for port_use in group['ports']:
            for port in config['ports']:
                if port_use == port['name']:
                    pixels_list.append(neopixel.NeoPixel(pin(port['pin1']), 144, brightness=1.0, auto_write=True, pixel_order=neopixel.GRB))
                    pixels_list[len(pixels_list) - 1].fill(color)
        # Task never end, unless cancel by the brake off timer
        while True:
            await asyncio.sleep(0)
    except asyncio.CancelledError:
        for pixels in pixels_list:
            pixels.deinit() # This will also turn off the neopixels
        return
    except Exception as e:
        #print(e)
        return

async def BrakeLight(group):
    global brake_task
    global brake_off_task
    #print(brake_task)
    if brake_task is None:
        brake_task = asyncio.create_task(brake_on(group))
        brake_off_task = asyncio.create_task(brake_off_timer())
    else:
        # Reset brake off timer if the brake task present
        brake_off_task.cancel()
        brake_off_task = asyncio.create_task(brake_off_timer())

speed_pixels_up = []
speed_pixels_down = []
speed_off_task = None

async def speed_off_timer():
    global speed_off_task
    global speed_pixels_down
    global speed_pixels_up
    try:
        await asyncio.sleep(0.2)
        for pixels in speed_pixels_down:
            pixels.deinit()
        for pixels in speed_pixels_up:
            pixels.deinit()
        speed_pixels_down = []
        speed_pixels_up = []
        speed_off_task = None
    except asyncio.CancelledError:
        return
    except Exception as e:
        #print(e)
        return
    
async def SpeedBar(num):
    global speed_off_task
    global speed_pixels_down
    global speed_pixels_up
    
    color = (20, 255, 255)
    
    if speed_off_task is None:
        for group in config['groups']:
            if group['name'] == 'SpeedBarLeft' or group['name'] == 'SpeedBarRight':
                for port in config['ports']:
                    if port['name'] == group['ports'][0]:
                        speed_pixels_up.append(neopixel.NeoPixel(pin(port['pin1']), 144, brightness=1.0, auto_write=False, pixel_order=neopixel.GRB))
                    if port['name'] == group['ports'][1]:
                        speed_pixels_down.append(neopixel.NeoPixel(pin(port['pin1']), 144, brightness=1.0, auto_write=False, pixel_order=neopixel.GRB))
        speed_off_task = asyncio.create_task(speed_off_timer())
    else:
        speed_off_task.cancel()
        speed_off_task = asyncio.create_task(speed_off_timer())
    
    try:
        for pixels in speed_pixels_down:
            for i in range (0, 144):
                if i < num:
                    pixels[i] = color
                else:
                    pixels[i] = (0, 0, 0)
            pixels.show()
            
        if num > 144:
            for pixels in speed_pixels_up:
                for i in range (0, 144):
                    if i + 144 < num:
                        pixels[i] = color
                    else:
                        pixels[i] = (0, 0, 0)
                pixels.show()
    except Exception as e:
        #print(e)
        return

req_func_callback = {
    "HazardWarningReq" : HazardWarningReq,
    "RightTurnLightReq" : TurnLightReq,
    "LeftTurnLightReq" : TurnLightReq,
    "BrakeLight" : BrakeLight
}

async def CANListener(can):
    listener = can.listen(timeout=0)
    old_bus_state = None
    
    while True:
        #print(time.monotonic())
        bus_state = can.state
        if bus_state != old_bus_state:
            print(f"Bus state changed to {bus_state}")
            old_bus_state = bus_state
        
        message = listener.receive()
        if message is not None:
            # Scan for request
            for group in config['groups']:
                if message.id == group['id'] and message.data == bytearray(group['data']):
                    print(group['description'], time.monotonic())
                    await req_func_callback[group['name']](group)
        
            if message.id == 515:
                await SpeedBar(message.data[1]+message.data[2])
                print('Show the speed', time.monotonic())
        
        # Setting the delay to 0 provides an optimized path to allow other tasks to run. 
        await asyncio.sleep(0) # Free up the resource for a while. 

async def main():
    tasks = []
    
    # Initialize CAN bus
    can = canio.CAN(rx=board.CAN_RX, tx=board.CAN_TX, baudrate=500_000, auto_restart=True)

    tasks.append(asyncio.create_task(CANListener(can)))
    await asyncio.gather(*tasks)

asyncio.run(main())
