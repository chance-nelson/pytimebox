from io import BytesIO
from itertools import product

import bluetooth
from PIL import Image


class ConnectionFailed(Exception):
    pass


TIMEBOX_HELLO = b"\x00\x05HELLO\x00"

TIMEBOX_VIEWS = {
    'clock': 0x00,
    'image': 0x05
}


def find_timeboxes():
    nearby_devices = bluetooth.discover_devices(lookup_names=True)
    return [i for i in nearby_devices if 'timebox' in i[1].lower()]


class Timebox:
    def __init__(self, addr: str):
        self._sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self._addr = addr
        self._sock.connect((self._addr, 4))
        
        ret = self._sock.recv(256)
        if ret != TIMEBOX_HELLO:
            raise ConnectionFailed

    def __del__(self):
        self._sock.close()

    def send(self, msg):
        self._sock.send(bytes(msg))

        response = self._sock.recv(256)

    @staticmethod
    def _checksum(msg):
        return (msg & 0x00ff, msg >> 8)

    @staticmethod
    def _mask(msg):
        ret = []
        for i in msg:
            if i == 0x01:
                ret.extend([0x03, 0x04])

            elif i == 0x02:
                ret.extend([0x03, 0x05])

            elif i == 0x03:
                ret.extend([0x03, 0x06])

            else:
                ret.append(i)

        return ret

    def switch_clock(self):
        msg = [0x04, 0x00, 0x45, TIMEBOX_VIEWS['clock']]
        checks = self._checksum(sum(msg))
        self.send([0x01] + self._mask(msg) + self._mask(checks) + [0x02])

    def switch_image(self):
        msg = [0x04, 0x00, 0x45, TIMEBOX_VIEWS['image']]
        checks = self._checksum(sum(msg))
        self.send([0x01] + self._mask(msg) + self._mask(checks) + [0x02])

    def send_image(self, image):
        """Send an image to the timebox

        Args:
            image: byte string of raw image data. Can be any arbitrary size
        """
        msg = []
        img = Image.open(BytesIO(image))
        img = img.resize((11, 11))
        img = img.convert('RGB')

        overlap = True
        for i in product(range(11), range(11)):
            y, x = i
            r, g, b = img.getpixel((x, y))
            # RRRRGGGG BBBB____
            if overlap:
                msg.append(((g & 0xf0) >> 4) + (r & 0xf0))
                msg.append(b & 0xf0 >> 4)
                overlap = False
            
            # ____RRRR GGGGBBBB
            else:
                msg[-1] += (r & 0xf0)
                msg.append(((g & 0xf0) >> 4) + (b & 0xf0))
                #msg.append(0) # wtf why even do this stupid encoding then
                overlap = True
        
        head = [0xbd, 0x00, 0x44, 0x00, 0x0a, 0x0a, 0x04]
        checks = self._checksum(sum(head) + sum(msg))

        msg_encoded = [0x01] + head + self._mask(msg) + self._mask(checks) + [0x02]
        self.send(msg_encoded)
