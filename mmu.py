
class Fifo(object):
    def __init__(self):
        self.queue = []
        
    def put(self, frameId):
        self.queue.append(frameId)

    def evict(self):
        return self.queue.pop(0)

class Frame:
    def __init__(self, frameId):
        self.frameId = frameId

class SecondChance(Fifo):

    def __init__(self):
      super(SecondChance, self).__init__()
      
    def put(self, frameId, bit=0):
        frame = Frame(frameId)
        frame.bit = bit
        super(SecondChance, self).put(frame)

    def evict(self):
        while self.queue:
            frame = super(SecondChance, self).evict()
            if frame.bit == 1:
                self.put(frame.frameId)
            else:
                return frame.frameId

    def access(self, frameId):
        for frame in self.queue:
            if frame.frameId == frameId:
                frame.bit =  1
                break

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

    def clear(self, mem_address):
        self.address_table[mem_address] = False

class LinearMapping(object):

    def __init__(self, memory_size=2147483648, page_size=4096, physicalMemory=None):
      super(LinearMapping, self).__init__()
      if not physicalMemory:
          physicalMemory = PhysicalMemory(memory_size, page_size)

      self.physicalMemory = physicalMemory
      self.page_table = {}
      self.swap = SecondChance()

    def map(self, virtual_address, frame_id=None, offset=None):
        if frame_id == None and offset == None:
          frame_id = virtual_address >> 12
          offset = int(bin(virtual_address)[2 + 20:], 2)

        hw_address, n_pagefaults = 0, 0 # tmp values
        if frame_id in self.page_table:
            if self.page_table[frame_id] == None:
                n_pagefaults += 1
                hw_begin = self.physicalMemory.get() # also known as frame
                if hw_begin == None:
                    frame_to_swap = self.swap.evict()
                    mem_to_use = self.page_table[frame_to_swap]
                    self.page_table[frame_to_swap] = None
                    self.page_table[frame_id] = mem_to_use

                else:
                  self.page_table[frame_id] = hw_begin 
                    
            hw_begin = self.page_table[frame_id]
            self.swap.access(frame_id)
    
        else:
            n_pagefaults = 1
            hw_begin = self.physicalMemory.get() # also known as frame
            if hw_begin == None:
                frame_to_swap = self.swap.evict()
                mem_to_erase = self.page_table[frame_to_swap]
                self.physicalMemory.clear(mem_to_erase)
                self.page_table[frame_to_swap] = None
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
        frame_id = virtual_address >> 12
        PT1 = virtual_address >> 22
        PT2 = int(bin(virtual_address >> 12)[2 + 10:], 2)
        offset = int(bin(virtual_address)[2 + 20:], 2)
        
        pagefault = 0
        if PT1 not in self.PT1_table:
            pagefault += 1
            self.PT1_table[PT1] = LinearMapping(physicalMemory=self.physicalMemory)

        PT2_table = self.PT1_table[PT1]
        hw_address, _ , n_pagefaults = PT2_table.map(virtual_address, frame_id=PT2, offset=offset)
        return hw_address + offset, frame_id, n_pagefaults + pagefault

class Page:
    def __init__(self, page_id, pid):
      self.page_id = page_id
      self.pid = pid 

class InvertedMapping(object):

    def __init__(self, memory_size=8589934592, page_size=4096):
      super(InvertedMapping, self).__init__()
      self.physicalMemory = PhysicalMemory(memory_size, page_size)
      self.swap = SecondChance()
      self.page_size = page_size
      self.page_table = []
    
    def map(self, virtual_address):
        pid = virtual_address >> 42
        page_id = int(bin(virtual_address >> 12)[2 + 22:], 2)
        offset = int(bin(virtual_address)[2 + 42:], 2)
        
        hw_begin, n_pagefaults = None, 0 # tmp values
        for i in range(len(self.page_table)):
            page = self.page_table[i]
            if page.pid == pid and page.page_id == page_id:
                hw_begin = i * self.page_size
                break
        
        if hw_begin == None:
            n_pagefaults += 1
            hw_begin = self.physicalMemory.get()
            page = Page(page_id, pid)
            if hw_begin == None:
                page_to_remove = self.swap.evict()
                index = self.page_table.index(page_to_remove)
                self.page_table[index] = page
            else:
                self.page_table.append(page)
                hw_begin = (len(self.page_table) - 1) * self.page_size
                self.physicalMemory.put(hw_begin)
        
        hw_address = hw_begin + offset
        frame_id = hw_begin
        return hw_address, frame_id, n_pagefaults

class MMU(object):

    def __init__(self, mapping_type):
      super(MMU, self).__init__()
      if mapping_type == "linear":
          self.mapping = LinearMapping()
      elif mapping_type == "hierarchical":
          self.mapping = HierarchicalMapping()
      elif mapping_type == "inverted":
          self.mapping = InvertedMapping()
      else:
          raise Exception("Not valid mapping")

    def map(self, virtual_address):
        return self.mapping.map(virtual_address)
