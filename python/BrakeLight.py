from canlib import canlib, Frame
import time

ch = canlib.openChannel(channel=0, bitrate=canlib.Bitrate.BITRATE_500K)

ch.setBusOutputControl(canlib.canDRIVER_NORMAL)

ch.busOn()

frame = Frame(id_=513, data=[1, 0, 0, 0, 0, 0, 0, 0], dlc=8)

while True:
    try:
        ch.write(frame)
        time.sleep(0.1)
    except KeyboardInterrupt:
        ch.busOff()
        break
