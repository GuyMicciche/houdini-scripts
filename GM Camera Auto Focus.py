# Usage: Add this as a shelf tool. With a camera selected in the obj context, use this tool to generate a focus nul, and automatically sets the focus of the camera to the distance between the camera and the nul.
# Feature 1: Names the focus node based on the selected camera node
# Feature 2: Selects the focus node for user convenience

# set root
obj = hou.node("/obj")

# define nodes and create focus nul
selected_node = hou.selectedNodes()
cam_node = selected_node[0]
cam_node_name = str(cam_node) + "_focus"
focus_node = obj.createNode("null", cam_node_name)

# set camera focus code to focus nul
focus_code = "vlength(vtorigin(\".\",\"../" + cam_node_name + "\"))"
cam_node.parm("focus").setExpression(focus_code)

# layout nodes and select focus nul for user convenience
focus_node.setSelected(1)
obj.layoutChildren(items=[cam_node, focus_node], horizontal_spacing=1, vertical_spacing=1)