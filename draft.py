
class PhysicalMemory(object):
    
    def __init__(self, memory_size, page_size):
        super(PhysicalMemory, self).__init__()
        self.memory_size = memory_size
        self.page_size = page_size
        self.address_table = {}
        for address in range(0, memory_size, page_size):
            self.address_table[address] = False

    def get(self):
        for address, in_use in  self.address_table.items():
            if not in_use: 
                return address
    
    def put(self, mem_address):
        self.address_table[mem_address] = True

class LinearMapping(object):

    def __init__(self, memory_size=2147483648, page_size=4096, physicalMemory=None):
      super(LinearMapping, self).__init__()
      if not physicalMemory:
          physicalMemory = PhysicalMemory(memory_size, page_size)

      self.physicalMemory = physicalMemory
      self.page_table = {}

    def map(self, virtual_address, frame_id=None, offset=None):
        if not frame_id and not offset:
          frame_id = virtual_address >> 12
          offset = int(bin(virtual_address)[2 + 20:], 2)

        hw_address, n_pagefaults = 0, 0 # tmp values
        if frame_id in self.page_table:
            hw_begin = self.page_table[frame_id]
            
        else:
            n_pagefaults = 1
            hw_begin = self.physicalMemory.get()
            self.physicalMemory.put(hw_begin)
            self.page_table[frame_id] = hw_begin
        
        hw_address = hw_begin + offset
        return hw_address, frame_id, n_pagefaults

class HierarchicalMapping(object):

    def __init__(self, memory_size=2147483648, page_size=4096):
      super(HierarchicalMapping, self).__init__()
      self.physicalMemory = PhysicalMemory(memory_size, page_size)
      self.PT1_table = {}

    def map(self, virtual_address):
        PT1 = virtual_address >> 22
        PT2 = int(bin(virtual_address >> 12)[2 + 10:], 2)
        offset = int(bin(virtual_address)[2 + 20:], 2)
        
        pagefault = 0
        if PT1 not in self.PT1_table:
            pagefault += 1
            self.PT1_table[PT1] = LinearMapping(physicalMemory=self.physicalMemory)

        PT2_table = self.PT1_table[PT1]
        hw_address, frame_id, n_pagefaults = PT2_table.map(virtual_address, frame_id=PT2, offset=offset)
        return hw_address + offset, frame_id, n_pagefaults + pagefault

class InvertedMapping(object):

    def __init__(self, memory_size=8589934592, page_size=4096):
      super(HierarchicalMapping, self).__init__()
      self.physicalMemory = PhysicalMemory(memory_size, page_size)
    
    def map(self, virtual_address):
        pass

def testL():
  print("LINEAR")
  # Linear
  t1 = 4294967295 # 11111111111111111111 111111111111 # 1 page faults
  t2 = 4294840256 # 11111111111111100000 111111000000 # 1 page faults
  t3 = 4294967232 # 11111111111111111111 111111000000 # 0 page faults
  t4 = 4164943808 # 11111000001111111111 111111000000 # 1 page faults
  t5 = 4164943871 # 11111000001111111111 111111111111 # 0 page faults
  l = LinearMapping()
  print(l.map(t1))
  print(l.map(t2))
  print(l.map(t3))
  print(l.map(t4))
  print(l.map(t5))
  print()

def testH():
  print("HIERARCHICAL")
  # Hierarchical
  t1 = 4294967295 # 1111111111 1111111111 111111111111 # 2 page faults
  t2 = 4294840256 # 1111111111 1111100000 111111000000 # 1 page faults
  t3 = 4294967232 # 1111111111 1111111111 111111000000 # 0 page faults
  t4 = 4164943808 # 1111100000 1111111111 111111000000 # 2 page faults
  t5 = 4164943871 # 1111100000 1111111111 111111111111 # 0 page faults
  h = HierarchicalMapping()
  print(h.map(t1))
  print(h.map(t2))
  print(h.map(t3))
  print(h.map(t4))
  print(h.map(t5))
  print()

testL()
testH()
