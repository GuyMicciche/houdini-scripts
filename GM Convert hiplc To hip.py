import os
import sys
import subprocess
import time
import hou

# Get the path to the Houdini root directory
houdini_root = os.getenv('HFS')

# Construct the path to the Houdini executable
# This might differ depending on your platform and Houdini version
houdini_executable_path = os.path.join(houdini_root, 'bin', 'houdinifx')

def convert_hiplc_to_hip():
    # Let the user select the .hiplc file
    hiplc_path = hou.ui.selectFile(title="Select .hiplc or .hipnc file", pattern="*.hip,*.hiplc,*.hipnc,*.hip*")
    
    if not hiplc_path:
        # The user cancelled the operation
        return

    # Open the .hiplc file
    hou.hipFile.load(hiplc_path)

    # Export the cmd file
    cmd_path = "$TEMP/temp.cmd"
    hou.hscript("opscript -G -r / > " + cmd_path)
   
    subprocess.Popen([houdini_executable_path, "-foreground"])

    hou.exit()

# Use the function
convert_hiplc_to_hip()