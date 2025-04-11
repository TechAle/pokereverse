#!/usr/bin/env python3
import subprocess
import tempfile
import os

# command script import "scriptBreakpoint.py"
# breakpoint set --address 0x104CD9B84
# breakpoint command add -F testScript.on_breakpoint_hit 1

def search_memory_range_with_lldb(pid, byte_pattern, start_addr, end_addr):
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as cmd_file:
        cmd_file.write(f"""\
            process attach -p {pid}
            process handle SIGSEGV -n false -p false -s false
            process continue
            script import lldb
            script start_addr = {start_addr}
            script end_addr = {end_addr}
            script search_bytes = {byte_pattern}
            script memory_data = lldb.process.ReadMemory(start_addr, end_addr - start_addr, lldb.SBError())
            script offset = memory_data.find(search_bytes)
            script hexToCheck = hex(int(start_addr, 16) + offset)
            ldb.target.SetMetadata("hexToCheck", hexToCheck)
            breakpoint set --address `$hexToCheck`
            breakpoint command add -s command -- "register read x1; quit"
            # Continue execution (will stop at breakpoint, then quit)
            process continue
        """)
        cmd_path = cmd_file.name

    try:
        result = subprocess.run(
            ["lldb", "-s", cmd_path],
            capture_output=True,
            text=True,
        )

        # Analisi dell'output per estrarre l'offset
        offset = None
        for line in result.stdout.splitlines():
            if "OFFSET_RESULT:" in line:
                offset_str = line.split("OFFSET_RESULT:")[1].strip()
                if not offset_str.startswith("{offset}"):
                    offset = int(offset_str)
                    break

        if offset is None:
            raise RuntimeError("Failed to find offset")
        hex_as_int = int(start_addr, 16)  # Convert hex to decimal
        sum_decimal = 21906052 + hex_as_int
        sum_hex = hex(sum_decimal)  # Convert sum back to hex

        return sum_hex

    finally:
        os.unlink(cmd_path)

def getKeyboardAddress(pid):
    try:
        output = subprocess.check_output(['vmmap', str(pid)])
        output = output.decode('utf-8')
        toFind = "/System/Library/Keyboard Layouts/AppleKeyboardLayouts.bundle/Contents/Resources/AppleKeyboardLayouts-L.dat"
        found = -1
        startingIndex = -1
        endingIndex = 1
        # Look for the stack region in the output
        for line in output.split('\n'):
            if line.__contains__(toFind):
                found = 0
            elif found == 1:
                if line.__contains__("mapped file"):
                    return [startingIndex, endingIndex]
                else:
                    endingIndex = line.split("-")[1].split(" ")[0]
            elif found == 0:
                found = 1
                startingIndex = (" ".join(line.split())).split(" ")[1].split("-")[0]



    except subprocess.CalledProcessError:
        print("Failed to run vmmap. Make sure the process exists and you have permissions.")
    except FileNotFoundError:
        print("vmmap command not found. It's part of macOS developer tools.")
    return None


if __name__ == "__main__":
    pin = 54183
    addresses = getKeyboardAddress(pin)
    print(search_memory_range_with_lldb(
        pid=pin,  # Replace with target PID
        byte_pattern=b"\x26\x60\x00\x79",  # Bytes to find
        start_addr="0x" + addresses[0],  # Your start address
        end_addr="0x" + addresses[1]  # Your end address
    ))
