from canlib import canlib, Frame
import time

ch = canlib.openChannel(channel=0, bitrate=canlib.Bitrate.BITRATE_500K)

ch.setBusOutputControl(canlib.canDRIVER_NORMAL)

ch.busOn()

frame = Frame(id_=515, data=[1, 0, 0, 0, 0, 0, 0, 0], dlc=8)

while True:
    try:
        for i in range(0, 289):
            if i <= 255:
                frame.data[1] = i
                frame.data[2] = 0
            else:
                frame.data[1] = 255
                frame.data[2] = i - 255
            ch.write(frame)
            time.sleep(0.01)
        for i in range(288, 0, -1):
            if i <= 255:
                frame.data[1] = i
                frame.data[2] = 0
            else:
                frame.data[1] = 255
                frame.data[2] = i - 255
            ch.write(frame)
            time.sleep(0.01)
    except KeyboardInterrupt:
        ch.busOff()
        break
