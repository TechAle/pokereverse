# Mac Memory Utilities
This project contains all the utilities needed to read and write the memory of other processes.
## How to start
Lets first install the library needed
- pip install setuptools wheel
- python setup.py build

This is gonna isntall the library mach, a library that was created for python 2 that i updated to work with python 3.

This library is a must to read and write the memory of other processes in python.

Then, we need to be sure that the application we are trying to read the memory is not signed
- Due to the newest macos update, if we dont want to disable SIP, we must disable the signature of the application we are trying to read the memory.
- To do this, we need to open the terminal and run the following command:
```bash
sudo codesign --remove-signature /path/to/application
```

I suggest using Bit Slicer for getting the address that then we are gonna use in our code.

## Files
- exampleBaseAddress.py shows how to read the memory of other process, and then how to get the base address.
- exampleFindPattern.py shows how to find a pattern in the memory of other process. Why is it useful? So that we do not rely on the base address, that breaks every update
- exampleGetAddressOnBreakpoint.py shows how to read the memory of a running process on a breakpoint. 
- scriptBreakpoint.py is needed as an helper for exampleGetAddressOnBreakpoint.py

For some reasons mac has no resources about how to read and write other processes memory, hope this helps someone not waste 1-2 weeks of their life.