from micropython import const  
import framebuf  
SET_CONTRAST = const(0x81)  
SET_ENTIRE_ON = const(0xA4)  
SET_NORM_INV = const(0xA6)  
SET_DISP = const(0xAE)  
SET_MEM_ADDR = const(0x20)  
SET_COL_ADDR = const(0x21)  
SET_PAGE_ADDR = const(0xB0)  
SET_DISP_START_LINE = const(0x40)  
SET_SEG_REMAP = const(0xA0)  
SET_MUX_RATIO = const(0xA8)  
SET_COM_OUT_DIR = const(0xC0)  
SET_DISP_OFFSET = const(0xD3)  
SET_COM_PIN_CFG = const(0xDA)  
SET_DISP_CLK_DIV = const(0xD5)  
SET_PRECHARGE = const(0xD9)  
SET_VCOM_DESEL = const(0xDB)  
SET_CHARGE_PUMP = const(0x8D)
LOW_COLUMN_ADDRESS  = const(0x00)
HIGH_COLUMN_ADDRESS = const(0x10)
class SH1106(framebuf.FrameBuffer):  
  def __init__(self, width, height, external_vcc):  
    self.width = width  
    self.height = height  
    self.external_vcc = external_vcc  
    self.pages = self.height // 8  
    self.buffer = bytearray(self.pages * self.width)  
    super().__init__(self.buffer, self.width, self.height, framebuf.MONO_VLSB)  
    self.init_display()  
  def init_display(self):  
    for cmd in (  
      SET_DISP | 0x00, # off  
      # address setting  
      SET_MEM_ADDR,  
      0x00, # horizontal  
      # resolution and layout  
      SET_DISP_START_LINE | 0x00,  
      SET_SEG_REMAP | 0x01, # column addr 127 mapped to SEG0  
      SET_MUX_RATIO,  
      self.height - 1,  
      SET_COM_OUT_DIR | 0x08, # scan from COM[N] to COM0  
      SET_DISP_OFFSET,  
      0x00,  
      SET_COM_PIN_CFG,  
      0x02 if self.width > 2 * self.height else 0x12,  
      # timing and driving scheme  
      SET_DISP_CLK_DIV,  
      0x80,  
      SET_PRECHARGE,  
      0x22 if self.external_vcc else 0xF1,  
      SET_VCOM_DESEL,  
      0x30, # 0.83*Vcc  
      # display  
      SET_CONTRAST,  
      0xFF, # maximum  
      SET_ENTIRE_ON, # output follows RAM contents  
      SET_NORM_INV, # not inverted  
      # charge pump  
      SET_CHARGE_PUMP,  
      0x10 if self.external_vcc else 0x14,  
      SET_DISP | 0x01,  
    ): # on  
      self.write_cmd(cmd)  
    self.fill(0)  
    self.show()  
  def poweroff(self):  
    self.write_cmd(SET_DISP | 0x00)  
  def poweron(self):  
    self.write_cmd(SET_DISP | 0x01)  
  def contrast(self, contrast):  
    self.write_cmd(SET_CONTRAST)  
    self.write_cmd(contrast)  
  def invert(self, invert):  
    self.write_cmd(SET_NORM_INV | (invert & 1))  
  def show(self):  
    (w, p, db, rb) = (self.width, self.pages,
                          self.buffer, self.buffer)
                          
    for page in range(self.height // 8):
        self.write_cmd(SET_PAGE_ADDR | page)
        self.write_cmd(LOW_COLUMN_ADDRESS | 2)
        self.write_cmd(HIGH_COLUMN_ADDRESS | 0)
        self.write_data(db[(w*page):(w*page+w)])

class SH1106_SPI(SH1106):  
  def __init__(self, width, height, spi, dc, res, cs, external_vcc=False):  
    self.rate = 10 * 1024 * 1024  
    dc.init(dc.OUT, value=0)  
    res.init(res.OUT, value=0)  
    cs.init(cs.OUT, value=1)  
    self.spi = spi  
    self.dc = dc  
    self.res = res  
    self.cs = cs  
    import time  
    self.res(1)  
    time.sleep_ms(1)  
    self.res(0)  
    time.sleep_ms(10)  
    self.res(1)  
    super().__init__(width, height, external_vcc)  
  def write_cmd(self, cmd):  
    self.spi.init(baudrate=self.rate, polarity=0, phase=0)  
    self.cs(1)  
    self.dc(0)  
    self.cs(0)  
    self.spi.write(bytearray([cmd]))  
    self.cs(1)  
  def write_data(self, buf):  
    self.spi.init(baudrate=self.rate, polarity=0, phase=0)  
    self.cs(1)  
    self.dc(1)  
    self.cs(0)  
    self.spi.write(buf)  
    self.cs(1)  