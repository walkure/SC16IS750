import io
from . import SC16IS750

class Serial(io.RawIOBase):
    FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS = (5, 6, 7, 8)
    STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO = (1, 1.5, 2)
    PARITY_NONE, PARITY_EVEN, PARITY_ODD, PARITY_MARK, PARITY_SPACE = 'N', 'E', 'O', 'M', 'S'
    def __init__(self, crystalFrequency=14745600, deviceaddress=0x90,baudrate=9600,bytesize=EIGHTBITS,parity=PARITY_NONE,stopbits=STOPBITS_ONE,useFifo=True,**kwargs):
        self.impl = SC16IS750.SC16IS750()
        self.impl.init()
        self.impl.setBaudrate(baudrate)
        self.impl.setUARTAttributes(bytesize,parity,stopbits)
        if useFifo:
            self.impl.enableFifo()

    def write(self,b):
        bytesWritten = 0
        for byte in b :
            self.impl.writeInt(byte)
            bytesWritten += 1

        return bytesWritten

    def readall(self):
        if not self.impl.isDataWaiting():
            return None

        buffer = []
        while self.impl.dataWaiting() > 0:
             buffer.append(self.impl.readInt())

        return bytes(buffer)


    def readinto(self,b):
        if not self.impl.isDataWaiting():
            return None

        index = 0
        while self.impl.dataWaiting() > 0 and index < len(b):
            b[index] = self.impl.readInt()
            index+=1

        return index

