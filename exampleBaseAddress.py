# noinspection PyUnresolvedReferences
import mach
import subprocess
import re

import psutil


def get_base_address(pid):
    try:
        output = subprocess.check_output(['vmmap', str(pid)])
        output = output.decode('utf-8')

        # Look for the stack region in the output
        for line in output.split('\n'):
            if '__TEXT' in line or '__DATA' in line:
                continue
            if 'stack' in line.lower():
                return int(line.replace("  ", "").split(" ")[2].split("-")[0], 16)
    except subprocess.CalledProcessError:
        print("Failed to run vmmap. Make sure the process exists and you have permissions.")
    except FileNotFoundError:
        print("vmmap command not found. It's part of macOS developer tools.")
    return None

def get_relative_address(pid, absolute_address):
    base = get_base_address(pid)
    return absolute_address - base


def get_absolute_address(pid, relative_address):
    base = get_base_address(pid)
    return base + relative_address

''' This is an example of getting a base address
pid = 44614
# Example usage
absolute_address = 0x200006A80350

try:
    # Get relative address
    relative_addr = get_relative_address(pid, absolute_address)

    # Read memory (using either address format)
    task = mach.task_for_pid(pid)

    # Method 1: Using original absolute address
    print("A " + str(absolute_address))
    data1 = mach.vm_read(task, absolute_address, 4)

    # Method 2: Using relative address (reconstruct absolute)
    reconstructed_addr = get_absolute_address(pid, relative_addr)
    print("B " + str(reconstructed_addr))
    data2 = mach.vm_read(task, reconstructed_addr, 4)

    print(f"Original absolute: 0x{absolute_address:x}")
    print(f"Relative offset: 0x{relative_addr:x}")
    print(f"Reconstructed absolute: 0x{reconstructed_addr:x}")
    print(f"Data verification: {data1.hex()} vs {data2.hex()}")

except mach.MachError as e:
    print(f"Mach error: {e}")
except Exception as e:
    print(f"General error: {e}")

'''
