import hou
import json

"""
Attachments Class for Houdini Nodes

The Attachments class enables nodes in Houdini to dynamically follow the movement 
and renaming of other nodes while maintaining a fixed positional offset within 
the node graph. When one node is attached to another, any positional or name change 
in the followed node automatically updates the attached node's position accordingly. 

This functionality is useful for organizing nodes that should maintain a spatial 
relationship with each other. The offset between nodes is stored in user data, 
and an event callback ensures the follower node updates whenever the followed 
node changes.

Methods:
- attach_node(node, node_to_follow): Attaches one node to follow another, storing
  the positional offset and setting up a callback for updates.
- detach_node(node, node_to_follow): Detaches a node from following another, 
  removing it from the list of followers and unregistering callbacks if necessary.
- iter_followers(node): Yields follower data for nodes attached to the specified 
  node, used for updating and managing followers.
- _update_attachments_callback(self, **kwargs): A callback function to update 
  follower positions when the followed node is modified, ensuring the follower 
  nodes remain correctly positioned.
"""

class Attachments:

    user_data_key = "attachednodes"

    @staticmethod
    def attach_node(node, node_to_follow):
        follow_event_types = (hou.nodeEventType.NameChanged,)
        assert node != node_to_follow, "Node cannot attach to itself"
        assert node.parent().path() == node_to_follow.parent().path(), \
            "Nodes must be siblings"

        followers_json = node.userData(Attachments.user_data_key)
        if followers_json:
            followers = json.loads(followers_json)
        else:
            followers = []

        offset = node.position() - node_to_follow.position()
        followers.append({
            "name": node.name(),
            "offset": [offset.x(), offset.y()]
        })

        node.setUserData(Attachments.user_data_key, json.dumps(followers))
        node_to_follow.addEventCallback(
            follow_event_types, Attachments._update_attachments_callback
        )

    @staticmethod
    def detach_node(node, node_to_follow):
        assert node != node_to_follow, "Node cannot detach itself"
        assert node.parent().path() == node_to_follow.parent().path(), \
            "Nodes must be siblings"

        followers = [
            follower for follower in Attachments.iter_followers(node_to_follow)
            if follower["name"] != node.name()
        ]

        if followers:
            node.setUserData(Attachments.user_data_key, json.dumps(followers))
        else:
            node.destroyUserData(Attachments.user_data_key, must_exist=False)

            for event_type, callback in node_to_follow.eventCallbacks():
                if callback is Attachments._update_attachments_callback:
                    node_to_follow.removeEventCallback(
                        (event_type,), callback
                    )

    @staticmethod
    def iter_followers(node):

        followers = node.userData(Attachments.user_data_key)
        if not followers:
            return

        followers = json.loads(followers)
        parent = node.parent()
        for follower_data in followers:

            follower_node_name = follower_data["name"]
            follower_node = parent.node(follower_node_name)
            if not follower_node:
                continue

            yield follower_data

    @staticmethod
    def _update_attachments_callback(self, **kwargs):
        node = kwargs["node"]
        follow_event_types = (hou.nodeEventType.NameChanged,)

        followers = list(Attachments.iter_followers(node))
        if followers:
            # Let's update the attached nodes
            position = node.position()
            parent = node.parent()
            for follower_data in followers:
                follower_node = parent.node(follower_data["name"])
                offset = hou.Vector2(*follower_data["offset"])
                follower_position = position + offset
                follower_node.setPosition(follower_position)

            # Let's remove any data that might have been present for a follower
            # that is not accurate currently now from the user data
            node.setUserData(Attachments.user_data_key, json.dumps(followers))

        else:
            # If nothing should follow the node, delete the callback and the
            # metadata key
            node.destroyUserData(Attachments.user_data_key, must_exist=False)
            node.removeEventCallback(
                follow_event_types, Attachments._update_attachments_callback