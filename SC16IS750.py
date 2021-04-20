import smbus
from enum import IntEnum

class SC16IS750:
    class registers(IntEnum):
        RHR= 0x00       # Receive Holding Register (R)
        THR= 0x00       # Transmit Holding Register (W)
        IER= 0x01       # Interrupt Enable Register (R/W)
        FCR= 0x02       # FIFO Control Register (W)
        IIR= 0x02       # Interrupt Identification Register (R)
        LCR= 0x03       # Line Control Register (R/W)
        MCR= 0x04       # Modem Control Register (R/W)
        LSR= 0x05       # Line Status Register (R)
        MSR= 0x06       # Modem Status Register (R)
        SPR= 0x07       # Scratchpad Register (R/W)
        TCR= 0x06       # Transmission Control Register (R/W)
        TLR= 0x07       # Trigger Level Register (R/W)
        TXLVL = 0x08    # Transmit FIFO Level Register (R)
        RXLVL = 0x09    # Receive FIFO Level Register (R)
        IODIR= 0x0A     # I/O pin Direction Register (R/W)
        IOSTATE= 0x0B   # I/O pin States Register (R)
        IOINTENA= 0x0C  # I/O Interrupt Enable Register (R/W)
        IOCONTROL= 0x0E # I/O pins Control Register (R/W)
        EFCR= 0x0F      # Extra Features Register (R/W)

        # -- Special Register Set (Requires LCR[7] = 1 & LCR != 0xBF to use)
        DLL= 0x00       # Divisor Latch LSB (R/W)
        DLH= 0x01       # Divisor Latch MSB (R/W)

        # -- Enhanced Register Set (Requires LCR = 0xBF to use)
        EFR= 0x02       # Enhanced Feature Register (R/W)
        XON1= 0x04      # XOn1 (R/W)
        XON2= 0x05      # XOn2 (R/W)
        XOFF1= 0x06     # XOff1 (R/W)
        XOFF2= 0x07     # XOff2 (R/W)

    def init(self, crystalFrequency=14745600, deviceaddress=0x90):
        self.DEVICE_ADDRESS = deviceaddress
        self.bus = smbus.SMBus(1)
        self.crystalFrequency = crystalFrequency

    def readRegister(self, registerAddress):
        shiftedDeviceAddress = self.DEVICE_ADDRESS >> 1
        shiftedRegisterAddress = registerAddress << 3
        registerReadValue = self.bus.read_byte_data(shiftedDeviceAddress, shiftedRegisterAddress)
        return registerReadValue

    def writeRegister(self, registerAddress, data):
        shiftedDeviceAddress = self.DEVICE_ADDRESS >> 1
        shiftedRegisterAddress = registerAddress << 3
        self.bus.write_byte_data(shiftedDeviceAddress, shiftedRegisterAddress, data)

    ##Set the desired baudrate of chips UART##
    def setBaudrate(self, baudrate):
        clockDivisor = (self.readRegister(self.registers.MCR) & 0b10000000) >> 7
        if(clockDivisor == 0):
            prescaler = 1
        elif(clockDivisor == 1):
            prescaler = 4
        divisor = int((self.crystalFrequency / prescaler) / (baudrate * 16))
        
        lowerDivisor = (divisor & 0xFF)
        higherDivisor = (divisor & 0xFF00) >> 8

        self.setRegisterBit(self.registers.LCR, 7)

        self.writeRegister(self.registers.DLL, lowerDivisor)
        self.writeRegister(self.registers.DLH, higherDivisor)

        self.unsetRegisterBit(self.registers.LCR, 7)

    ##Set the desired UART attributes##
    def setUARTAttributes(self, dataBits, parityType, stopBits):
        #Calculate bits for LCR register#

        if dataBits == 5:
            newLcr = 0b00
        elif dataBits == 6:
            newLcr = 0b01
        elif dataBits == 7:
            newLcr = 0b10
        elif dataBits == 8:
            newLcr = 0b11

        if stopBits > 1:
            newLcr |= (0b1 << 2)

        if parityType == 'N':
            pass
        elif parityType == 'O':
            newLcr |= (0b001 << 3)
        elif parityType == 'E':
            newLcr |= (0b011 << 3)
        elif parityType == 'M':
            newLcr |= (0b101 << 3)
        elif parityType == 'S':
            newLcr |= (0b111 << 3)

        self.writeRegister(self.registers.LCR,newLcr)


    ##Set the bit in position passed##
    def setRegisterBit(self, registerAddress, registerBit):
        current = self.readRegister(registerAddress)
        updated = current | (1 << registerBit)
        self.writeRegister(registerAddress, updated)

    ##Unset the bit in position passed##
    def unsetRegisterBit(self, registerAddress, registerBit):
        current = self.readRegister(registerAddress)
        updated = current & ~(1 << registerBit)
        self.writeRegister(registerAddress, updated)

    ##Peek Register Bit##
    def peekRegisterBit(self, registerAddress, registerBit):
        current = self.readRegister(registerAddress)
        return current & (1 << registerBit) != 0


    ##Checks if any data in FIFO buffer##
    def isDataWaiting(self):
        return self.peekRegisterBit(self.registers.LSR,0)

    ##Checks number of bytes waiting in FIFO buffer##
    def dataWaiting(self):
        return self.readRegister(self.registers.RXLVL)
        
    ##Writes to Scratch register and checks successful##
    def testChip(self):
        self.writeRegister(self.registers.SPR, 0xFF)
        if(self.readRegister(self.registers.SPR) != 0xFF):
            return False
        return True            


    ## Write a single byte##
    def writeInt(self,byte):
        while self.peekRegisterBit(self.registers.LSR,5):
                break

        self.writeRegister(self.registers.THR,byte)


    ##Read a single byte##
    def readInt(self):
        return self.readRegister(self.registers.RHR)


    ##Enable FIFO System##
    def enableFifo(self):
        self.setRegisterBit(self.registers.FCR,0)

    ##Clear RxD FIFO##
    def clearRxFifo(self):
        self.setRegisterBit(self.registers.FCR,1)

    ##Clear TxD FIFO##
    def clearTxFifo(self):
        self.setRegisterBit(self.registers.FCR,2)

