
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

    def get_free_address(self):
        for address, in_use in self.address_table.items():
            if not in_use: 
                return address
    
    def total_of_free_page(self):
        count = 0
        for _, in_use in self.address_table.items():
            if not in_use:
                count += 1
    
        return count

    def alloc_given_address(self, mem_address):
        self.address_table[mem_address] = True

    def deallocate_give_address(self, mem_address):
        self.address_table[mem_address] = False

class LinearMapping(object):

    def __init__(self, memory_size=2147483648, page_size=1024, physicalMemory=None, number_of_pages_to_page_table=None):
      super(LinearMapping, self).__init__()
      used_by_hierarchical_mapping = not physicalMemory and not number_of_pages_to_page_table
      if used_by_hierarchical_mapping:
          physicalMemory = PhysicalMemory(memory_size, page_size)
          bytes_required_for_mapping = 8 # 20 bits for key, 20 for value, 20 for second-chance table
          key_size = 2 ** 20
          number_of_pages_to_page_table = key_size // page_size * bytes_required_for_mapping

      self.physicalMemory = physicalMemory
      self.page_size = page_size
      self.page_table = {}
      self.swap = SecondChance()

      self.mem_allocated = []
      for i in range(number_of_pages_to_page_table): # fill memory with page table
          not_used_mem = self.physicalMemory.get_free_address()
          self.physicalMemory.alloc_given_address(not_used_mem)      
          self.mem_allocated.append(not_used_mem)

    def free_memory():
      for mem in self.mem_allocated: # erase used memory by page table
          self.physicalMemory.deallocate_give_address(mem)

    def map(self, virtual_address, page_id=None, offset=None):
        if page_id == None and offset == None:
            virtual_address = format(virtual_address, "032b")
            page_id = int(virtual_address[:32-12], 2)
            offset = int(virtual_address[20:], 2)

        hw_address, n_pagefaults = 0, 0 # tmp values
        if page_id in self.page_table:
            if self.page_table[page_id] == None:
                n_pagefaults += 1
                hw_begin = self.physicalMemory.get_free_address() # also known as frame
                if hw_begin == None:
                    frame_to_swap = self.swap.evict()
                    mem_to_use = self.page_table[frame_to_swap]
                    self.page_table[frame_to_swap] = None
                    self.page_table[page_id] = mem_to_use

                else:
                  self.page_table[page_id] = hw_begin 
                    
            hw_begin = self.page_table[page_id]
            self.swap.access(page_id)
    
        else:
            n_pagefaults = 1
            hw_begin = self.physicalMemory.get_free_address() # also known as frame
            if hw_begin == None:
                frame_to_swap = self.swap.evict()
                mem_to_erase = self.page_table[frame_to_swap]
                self.physicalMemory.deallocate_give_address(mem_to_erase)
                self.page_table[frame_to_swap] = None
                hw_begin = self.physicalMemory.get_free_address()

            self.physicalMemory.alloc_given_address(hw_begin)
            self.page_table[page_id] = hw_begin
            self.swap.put(page_id)
        
        hw_address = hw_begin + offset
        return hw_address, hw_begin // self.page_size, n_pagefaults

class HierarchicalMapping(object):

    def __init__(self, memory_size=2147483648, page_size=1024):
      super(HierarchicalMapping, self).__init__()
      self.physicalMemory = PhysicalMemory(memory_size, page_size)
      self.memory_size = memory_size
      self.page_size = page_size
      self.swap = SecondChance()
      self.PT1_table = {}

      bytes_required_for_mapping = 4 # 10 bits for key, 20 for value
      key_size = 2 ** 10 # 10 bits for PT1, only
      number_of_pages_to_PT1_table = key_size // page_size * bytes_required_for_mapping
      for i in range(number_of_pages_to_PT1_table): # fill memory with page table
          not_used_mem = self.physicalMemory.get_free_address()
          self.physicalMemory.alloc_given_address(not_used_mem)      

    def map(self, virtual_address):
        virtual_address = format(virtual_address, "032b")
        offset = int(virtual_address[20:], 2)
        PT1 = int(virtual_address[:32-22], 2)
        PT2 = int(virtual_address[32-22:32-12], 2)

        pagefault = 0
        if PT1 not in self.PT1_table:
            pagefault += 1
            total_of_free_page = self.physicalMemory.total_of_free_page()
            if total_of_free_page < 8: # our intern tables uses only 8 pages
                table_to_remove = self.swap.evict()
                for table_id, table in self.PT1_table.items():
                    if table == table_to_remove:
                        table_to_remove.free_memory()
                        del self.PT1_table[table_id]
                        break

            bytes_required_for_mapping = 5 # 10 bits for key, 20 for value, 10 for second-chance table
            key_size = 2 ** 10 # 10 bits for PT2, only
            number_of_pages_to_PT2_table = key_size // self.page_size * bytes_required_for_mapping
            self.PT1_table[PT1] = LinearMapping(physicalMemory=self.physicalMemory, number_of_pages_to_page_table=number_of_pages_to_PT2_table)
            self.swap.put( self.PT1_table[PT1])

        PT2_table = self.PT1_table[PT1]
        hw_address, frame_id , n_pagefaults = PT2_table.map(virtual_address, page_id=PT2, offset=offset)
        return hw_address, frame_id, n_pagefaults + pagefault

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
      number_of_pages = memory_size // page_size
      bytes_required_for_mapping = 7 # 22 bits for pid, 30 for pageId in table
      number_of_pages_to_page_table = number_of_pages // page_size * bytes_required_for_mapping
      for i in range(number_of_pages_to_page_table): # fill memory with page table
          not_used_mem = self.physicalMemory.get_free_address()
          self.physicalMemory.alloc_given_address(not_used_mem)
    
    def map(self, virtual_address):        
        virtual_address = format(virtual_address, "064b")
        pid = int(virtual_address[:22], 2)
        page_id = int(virtual_address[22:52], 2)
        offset = int(virtual_address[52:], 2)

        hw_begin, n_pagefaults = None, 0 # tmp values
        for i in range(len(self.page_table)):
            page = self.page_table[i]
            if page != None and page.pid == pid and page.page_id == page_id:
                hw_begin = i * self.page_size
                break
        
        if hw_begin == None:
            n_pagefaults += 1
            hw_begin = self.physicalMemory.get_free_address()
            page = Page(page_id, pid)
            if hw_begin == None:
                page_to_remove = self.swap.evict()
                index = self.page_table.index(page_to_remove)
                self.page_table[index] = page
                hw_begin = index
            else:
                self.page_table.append(page)
                hw_begin = (len(self.page_table) - 1) * self.page_size
                self.physicalMemory.alloc_given_address(hw_begin)

            self.swap.put(page)
        
        hw_address = hw_begin + offset
        frame_id = hw_begin
        return hw_address, frame_id // self.page_size, n_pagefaults

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
