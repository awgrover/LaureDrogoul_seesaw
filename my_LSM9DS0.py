import time
import sys
def debug2(*msg):
    print " ".join((str(x) for x in msg) )

class LSM9DS0(object):
    class Gyro(object):
        address = 0x6b
        id_register = 0x0F
        i2c_id = 0xD4 # 0b11010100

    class Accel(object):
        # and compass
        address = 0x1D
        id_register = 0x0F
        i2c_id = 0x49 # 0b1001001
        class CTRL_REG1_XM:
            r = 0x20
            DRBaseHz = 3.125 # multiply by 1..1024 powers of 2 only
            @classmethod
            def DRBits(cls, hz_mult ): # mult is the power of 2, 1..10, e.g. 10=1024mult. 0 = powerdown
                return hz_mult << 4
            BDUContinous = 0 << 3
            BDUOnRead = 1 << 3
            AXEN = 0b001
            AYEN = 0b010
            AZEN = 0b100
            AEN = AXEN|AYEN|AZEN
        class CTRL_REG5_XM:
            r = 0x24
            DRBaseHz = 3.125 # mult by 1..64, powers of 2 only. 100hz requires accel >50hz
            @classmethod
            def DRBits(cls, hz_mult ): # mult is the power of 2, 1..6, e.g. 10=1024mult. no 0
                return (hz_mult - 1) << 2 # 0=3.125
            M_RESLo = 0b00 << 5 # ?
            M_RESHi = 0b11 << 5 # ?
        class CTRL_REG6_XM:
            r = 0x25
            MFS2gauss = 0b00 << 6
            MFS12gauss = 0b11 << 6 # others avail
        class CTRL_REG7_XM:
            r = 0x26
            MDContinous = 0b00
        class STATUS_REG_A:
            r = 0x27
            ZYXADA = 0b1000 # avail
            XADA = 0b001 # avail
            YADA = 0b010 # avail
            ZADA = 0b100 # avail
        class OUT_X_L_A:
            r = 0x28 # high byte is +1
        class OUT_Y_L_A:
            r = 0x2A # high byte is +1
        class OUT_Z_L_A:
            r = 0x2C # high byte is +1
        class STATUS_REG_M:
            r = 0x07
            ZYXMDA = 0b1000
            XMDA = 0b001
            YMDA = 0b010
            ZMDA = 0b100
        class OUT_X_L_M:
            r = 0x08 # high byte is +1
        class OUT_Y_L_M:
            r = 0x0A # high byte is +1
        class OUT_Z_L_M:
            r = 0x0C # high byte is +1

    def __init__(self, i2c):
        # x,y,z
        self.accel = [0,0,0]
        self.compass = [0,0,0]

        self.i2c=i2c
        self.check_ids()
        self.last_update_time=0

        # accel
        # leave CTRL_REG0_XM as default
        self.i2c.write_byte_data(
            LSM9DS0.Accel.address,
            LSM9DS0.Accel.CTRL_REG1_XM.r,
            LSM9DS0.Accel.CTRL_REG1_XM.DRBits(6) | # 100hz=6
            LSM9DS0.Accel.CTRL_REG1_XM.BDUContinous |
            LSM9DS0.Accel.CTRL_REG1_XM.AZEN | # Y is don't care
            LSM9DS0.Accel.CTRL_REG1_XM.AXEN 
            )

        # compass
        self.i2c.write_byte_data(
            LSM9DS0.Accel.address,
            LSM9DS0.Accel.CTRL_REG5_XM.r,
            LSM9DS0.Accel.CTRL_REG5_XM.DRBits(6) | # 100hz
            LSM9DS0.Accel.CTRL_REG5_XM.M_RESHi
            )
        self.i2c.write_byte_data(
            LSM9DS0.Accel.address,
            LSM9DS0.Accel.CTRL_REG6_XM.r,
            LSM9DS0.Accel.CTRL_REG6_XM.MFS2gauss
            )
        self.i2c.write_byte_data(
            LSM9DS0.Accel.address,
            LSM9DS0.Accel.CTRL_REG7_XM.r,
            LSM9DS0.Accel.CTRL_REG7_XM.MDContinous
            )


    def read_hilo(self, addr, reg):
        # the accel has Low byte at reg, and high byte at reg+1
        val = self.i2c.read_byte_data(addr, reg)
        val += self.i2c.read_byte_data(addr, reg+1) << 8
        # debug2( "read hilo: 0x%02x[0x%02x] = 0x%04x" % (addr,reg, val))
        # This is signed (2'scomp)
        if val & (1 <<15):
            val = val - 65536
        return val

    def update(self):
        # You should call this on a threading.Thread(this.update)
        # seem to be running at .0015/cycle
        self.last_update_time = time.clock()
        while(True):
            # throttle to about 100hz
            since = time.clock()-self.last_update_time
            # debug2("since update ",since)
            if since < 0.01:
                time.sleep(0.01 - since)
            self.last_update_time = time.clock()

            # accel
            ready = self.i2c.read_byte_data( LSM9DS0.Accel.address, LSM9DS0.Accel.STATUS_REG_A.r)
            # debug2("ready accel %s" % "{0:b}".format(ready))
            if ready & LSM9DS0.Accel.STATUS_REG_A.XADA:
                self.accel[0] = self.read_hilo(LSM9DS0.Accel.address, LSM9DS0.Accel.OUT_X_L_A.r)

            # only care about x accel for now
            """
            if ready & LSM9DS0.Accel.STATUS_REG_A.YADA:
                self.accel[1] = self.read_hilo(LSM9DS0.Accel.address, LSM9DS0.Accel.OUT_Y_L_A.r)
            if ready & LSM9DS0.Accel.STATUS_REG_A.ZADA:
                self.accel[2] = self.read_hilo(LSM9DS0.Accel.address, LSM9DS0.Accel.OUT_Z_L_A.r)
            
            # compass
            ready = self.i2c.read_byte_data( LSM9DS0.Accel.address, LSM9DS0.Accel.STATUS_REG_M.r)
            # debug2("ready compass %s" % "{0:b}".format(ready))
            if ready & LSM9DS0.Accel.STATUS_REG_M.XMDA:
                self.compass[0] = self.read_hilo(LSM9DS0.Accel.address, LSM9DS0.Accel.OUT_X_L_M.r)
            if ready & LSM9DS0.Accel.STATUS_REG_M.YMDA:
                self.compass[1] = self.read_hilo(LSM9DS0.Accel.address, LSM9DS0.Accel.OUT_Y_L_M.r)
            if ready & LSM9DS0.Accel.STATUS_REG_M.ZMDA:
                self.compass[2] = self.read_hilo(LSM9DS0.Accel.address, LSM9DS0.Accel.OUT_Z_L_M.r)
            """

    def check_ids(self):
        for cls in [LSM9DS0.Gyro,LSM9DS0.Accel]:
            addr = cls.address
            want = cls.i2c_id
            reg = cls.id_register
            rez = self.i2c.read_byte_data(addr, reg)
            if rez == want:
                print "Indeed the %s @%s is the expected id (0x%02X)" % (cls.__name__,addr,want)
            else:
                raise Exception( "Nope, the %s @%s was 0x%02X, expected 0x%02X" % (cls.__name__,addr,rez,want))

    
