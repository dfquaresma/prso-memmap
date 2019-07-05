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
  linear = MMU("linear")
  mmu_output = linear.map(t1)
  print_mmu_output(mmu_output)
  assert (mmu_output[2] == 1)

  mmu_output = linear.map(t2)
  print_mmu_output(mmu_output)
  assert (mmu_output[2] == 1)

  mmu_output = linear.map(t3)
  print_mmu_output(mmu_output)
  assert (mmu_output[2] == 0)
  
  mmu_output = linear.map(t4)
  print_mmu_output(mmu_output)
  assert (mmu_output[2] == 1)
  
  mmu_output = linear.map(t5)
  print_mmu_output(mmu_output)
  assert (mmu_output[2] == 0)
  print()

def hierarchical_simple_page_fault_test():
  print("HIERARCHICAL")
  # Hierarchical
  t1 = 4294967295 # 1111111111 1111111111 111111111111 # 2 page faults
  t2 = 4294840256 # 1111111111 1111100000 111111000000 # 1 page faults
  t3 = 4294967232 # 1111111111 1111111111 111111000000 # 0 page faults
  t4 = 4164943808 # 1111100000 1111111111 111111000000 # 2 page faults
  t5 = 4164943871 # 1111100000 1111111111 111111111111 # 0 page faults
  hierarchical = MMU("hierarchical")
  mmu_output = hierarchical.map(t1)
  print_mmu_output(mmu_output)
  assert (mmu_output[2] == 2)

  mmu_output = hierarchical.map(t2)
  print_mmu_output(mmu_output)
  assert (mmu_output[2] == 1)
  
  mmu_output = hierarchical.map(t3)
  print_mmu_output(mmu_output)
  assert (mmu_output[2] == 0)
  
  mmu_output = hierarchical.map(t4)
  print_mmu_output(mmu_output)
  assert (mmu_output[2] == 2)
  
  mmu_output = hierarchical.map(t5)
  print_mmu_output(mmu_output)
  assert (mmu_output[2] == 0)
  print()

def inverted_simple_page_fault_test():
  print("INVERTED")
  # Interted
  t1 = 18446744073709551615 # 1111111111111111111111 111111111111111111111111111111 111111111111 # 1 page faults
  t2 = 18446744073709043711 # 1111111111111111111111 111111111111111111111110000011 111111111111 # 1 page faults
  t3 = 18446185521737629695 # 1111111111111110000000 111111111111111100000111111111 111111111111 # 1 page faults
  t4 = 18446185521737629695 # 1111111111111110000000 111111111111111100000111111111 111111111111 # 0 page faults
  t5 = 18446744073709551584 # 1111111111111111111111 111111111111111111111111111111 111111100000 # 0 page faults
  inverted = MMU("inverted")
  mmu_output = inverted.map(t1)
  print_mmu_output(mmu_output)
  assert (mmu_output[2] == 1)

  mmu_output = inverted.map(t2)
  print_mmu_output(mmu_output)
  assert (mmu_output[2] == 1)
  
  mmu_output = inverted.map(t3)
  print_mmu_output(mmu_output)
  assert (mmu_output[2] == 1)
  
  mmu_output = inverted.map(t4)
  print_mmu_output(mmu_output)
  assert (mmu_output[2] == 0)
  
  mmu_output = inverted.map(t5)
  print_mmu_output(mmu_output)
  assert (mmu_output[2] == 0)
  print()

if __name__ == '__main__':
  linear_simple_page_fault_test()
  hierarchical_simple_page_fault_test()
  inverted_simple_page_fault_test()
  