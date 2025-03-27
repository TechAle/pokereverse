#!/usr/bin/env python3
import subprocess
import tempfile
import os


def search_memory_range_with_lldb(pid, byte_pattern, start_addr, end_addr):
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as cmd_file:
        cmd_file.write(f"""\
process attach -p {pid}
script import lldb
script start_addr = {start_addr}
script end_addr = {end_addr}
script search_bytes = {byte_pattern}
script memory_data = lldb.process.ReadMemory(start_addr, end_addr - start_addr, lldb.SBError())
script offset = memory_data.find(search_bytes)
script print(f"OFFSET_RESULT:{{offset}}", flush=True)  # Marker per identificare l'offset
 quit
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

        print("LLDB Output:")
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)

        return offset  # Ritorna l'offset trovato (o None se non trovato)

    finally:
        os.unlink(cmd_path)


if __name__ == "__main__":
    print(search_memory_range_with_lldb(
        pid=54183,  # Replace with target PID
        byte_pattern=b"\x2c\x00",  # Bytes to find
        start_addr="0x2000012FFDD4",  # Your start address
        end_addr="0x2000012FFE24"  # Your end address
    ))