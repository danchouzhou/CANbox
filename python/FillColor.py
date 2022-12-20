from canlib import canlib, Frame
import time

ch = canlib.openChannel(channel=0, bitrate=canlib.Bitrate.BITRATE_500K)

ch.setBusOutputControl(canlib.canDRIVER_NORMAL)

ch.busOn()

while True:
    try:
        frame = Frame(id_=514, data=[0, 0, 100, 20, 30, 0, 0, 0], dlc=8)
        ch.write(frame)
        time.sleep(0.1)
        frame = Frame(id_=514, data=[0, 0, 30, 20, 100, 0, 0, 0], dlc=8)
        ch.write(frame)
        time.sleep(0.1)
    except KeyboardInterrupt:
        ch.busOff()
        break
