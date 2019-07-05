from mmu import *

def print_mmu_output(mmu_output):
    hw_address, frame_id, n_pagefaults = mmu_output
    print({"hw_address": hw_address, "frame_id": frame_id, "n_pagefaults": n_pagefaults})

def linear_simple_page_fault_test():
  print("LINEAR")
  # Linear
  t1 = 4294967295 # 11111111111111111111 111111111111 # 1 page faults
  t2 = 4294840256 # 11111111111111100000 111111000000 # 1 page faults
  t3 = 4294967232 # 11111111111111111111 111111000000 # 0 page faults
  t4 = 4164943808 # 11111000001111111111 111111000000 # 1 page faults
  t5 = 4164943871 # 11111000001111111111 111111111111 # 0 page faults
  l = MMU("linear")
  mmu_output = l.map(t1)
  assert (mmu_output[2] == 1)
  print_mmu_output(mmu_output)

  mmu_output = l.map(t2)
  assert (mmu_output[2] == 1)
  print_mmu_output(mmu_output)

  mmu_output = l.map(t3)
  assert (mmu_output[2] == 0)
  print_mmu_output(mmu_output)
  
  mmu_output = l.map(t4)
  assert (mmu_output[2] == 1)
  print_mmu_output(mmu_output)
  
  mmu_output = l.map(t5)
  assert (mmu_output[2] == 0)
  print_mmu_output(mmu_output)
  print()

def hierarchical_simple_page_fault_test():
  print("HIERARCHICAL")
  # Hierarchical
  t1 = 4294967295 # 1111111111 1111111111 111111111111 # 2 page faults
  t2 = 4294840256 # 1111111111 1111100000 111111000000 # 1 page faults
  t3 = 4294967232 # 1111111111 1111111111 111111000000 # 0 page faults
  t4 = 4164943808 # 1111100000 1111111111 111111000000 # 2 page faults
  t5 = 4164943871 # 1111100000 1111111111 111111111111 # 0 page faults
  h = MMU("hierarchical")
  mmu_output = h.map(t1)
  assert (mmu_output[2] == 2)
  print_mmu_output(mmu_output)

  mmu_output = h.map(t2)
  assert (mmu_output[2] == 1)
  print_mmu_output(mmu_output)
  
  mmu_output = h.map(t3)
  assert (mmu_output[2] == 0)
  print_mmu_output(mmu_output)
  
  mmu_output = h.map(t4)
  assert (mmu_output[2] == 2)
  print_mmu_output(mmu_output)
  
  mmu_output = h.map(t5)
  assert (mmu_output[2] == 0)
  print_mmu_output(mmu_output)
  print()

if __name__ == '__main__':
  linear_simple_page_fault_test()
  hierarchical_simple_page_fault_test()