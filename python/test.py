from canlib import canlib, Frame
import time

ch = canlib.openChannel(channel=0, bitrate=canlib.Bitrate.BITRATE_250K)

ch.setBusOutputControl(canlib.canDRIVER_NORMAL)

ch.busOn()

frame = Frame(id_=516, data=[0, 128, 0, 0, 0, 0, 0, 0], dlc=8)

while True:
    ch.write(frame)

    time.sleep(0.5)

ch.busOff()