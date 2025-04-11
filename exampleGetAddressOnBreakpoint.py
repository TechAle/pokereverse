import os
import threading
import time

import lldb

def on_breakpoint_hit(frame, bp_loc, internal_dict):
    print("Breakpoint colpito all'indirizzo:", hex(frame.GetPC()))
    print("Esecuzione della funzione prova()")
    return False  # Continua l'esecuzione

def continue_debugger(debugger):
    debugger.HandleCommand('process continue')

def __lldb_init_module(debugger, internal_dict):
    # 1. Attach al processo specificato
    error = lldb.SBError()
    target = debugger.CreateTarget("")
    process = target.AttachToProcessWithID(lldb.SBListener(), 27418, error)

    if not error.Success():
        print(f"Errore nell'attaccare al processo: {error}")
        return

    print(f"Attaccato al processo {process.GetProcessID()}")

    # 2. Configura gestione segnali
    debugger.HandleCommand('process handle SIGSEGV -n false -p false -s false')



    # 4. Aggiungi callback SENZA usare comandi manuali
    debugger.HandleCommand('command script import "scriptBreakpoint.py"')
    debugger.HandleCommand('breakpoint set --address 0x104CD9B84')
    debugger.HandleCommand('breakpoint command add -F testScript.on_breakpoint_hit 1')
    thread = threading.Thread(target=continue_debugger, args=(debugger,))
    thread.start()

    # Wait for the file x1.txt to appear, read it and delete it
    while not os.path.exists("x1.txt"):
        time.sleep(1)
    with open("x1.txt", "r") as f:
        x1_value = f.read().strip()

    # Delete the file
    os.remove("x1.txt")
    debugger.HandleCommand('breakpoint delete 1')

if __name__ == "__main__":
    print("Questo script deve essere eseguito all'interno di LLDB")
