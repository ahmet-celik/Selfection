class Section(object):

    def __init__(self, matched_line):
        self.__setfields__(int(matched_line.group("nr")), matched_line.group("name"), matched_line.group("type"),
                           int(matched_line.group("addr"), 16), int(matched_line.group("off"), 16),
                           int(matched_line.group("size"), 16))

    def __setfields__(self, nr, name, type, addr, off, size):
        self.nr = nr
        self.name = name
        self.type = type
        self.addr = addr
        self.off = off
        self.size = size

    def covers(self, addr):
        return self.addr <= addr < (self.addr + self.size)

    def addr2off(self, addr):
        return self.off + (addr - self.addr)

    def off2addr(self, off):
        return self.addr + (off - self.off)
