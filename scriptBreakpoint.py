def on_breakpoint_hit(frame, bp_loc, internal_dict):
    # Write it into a file "x1 temp"
    with open("x1.txt", "w") as f:
        f.write(str(frame.GetRegisters()).split(" x1 = ")[1].split("\n")[0])

    print("[*] Breakpoint colpito. Detaching dal processo...")

    process = frame.GetThread().GetProcess()

    # Continua l'esecuzione
    process.Continue()

    return False  # Non fermare l'esecuzione al breakpoint

