# This script is sent to Unreal Engine via Remote Execution.
# It uses the BPJsonExporter plugin to generate JSON.

GET_SELECTED_BLUEPRINTS_SCRIPT = """
import unreal
import json
import os

def get_selected_blueprints_json():
    # 1. Check if Plugin is available
    if not hasattr(unreal, 'BPJsonExporterBPLibrary'):
        return json.dumps({
            "error": "BPJsonExporter plugin not found. Please enable the plugin in Unreal."
        })

    exporter = unreal.BPJsonExporterBPLibrary
    selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
    
    blueprints_data = []

    for asset in selected_assets:
        # Filter for Blueprints
        if asset.get_class().get_name() != "Blueprint":
            continue

        try:
            graphs = exporter.get_blueprint_graphs(asset)
        except Exception:
            continue

        bp_entry = {
            "Name": asset.get_name(),
            "Path": asset.get_path_name(),
            "Graphs": {}
        }

        for graph in graphs:
            graph_name = graph.get_name()
            bp_entry["Graphs"][graph_name] = {}
            nodes = exporter.get_graph_nodes(graph)
            
            for node in nodes:
                node_name = node.get_name()
                clean_class = node.get_class().get_name().replace("K2Node_", "").replace("EdGraphNode_", "")
                
                node_info = {
                    "Title": exporter.get_node_title(node),
                    "Class": clean_class,
                    "In": {}, "Out": {}
                }

                pins = exporter.get_node_pins(node)
                for pin in pins:
                    # Skip dead pins (no connection, no default value)
                    if not pin.connected_to and (pin.default_value == "" or pin.default_value == "None"): 
                        continue

                    links = [f"{c.target_node_name}:{c.target_pin_name}" for c in pin.connected_to]
                    pin_data = {}
                    
                    # Smart Type Shortening
                    if "Object" in pin.pin_type or "Class" in pin.pin_type or "Interface" in pin.pin_type:
                        pin_data["T"] = pin.pin_type 
                    else:
                        pin_data["T"] = pin.pin_type.split('_')[0] 

                    if pin.default_value and pin.default_value != "None": 
                        pin_data["Val"] = pin.default_value
                    
                    if links: 
                        pin_data["Links"] = links

                    if pin.direction == "Input": 
                        node_info["In"][pin.pin_name] = pin_data
                    else: 
                        node_info["Out"][pin.pin_name] = pin_data

                bp_entry["Graphs"][graph_name][node_name] = node_info
        
        blueprints_data.append(bp_entry)

    if not blueprints_data:
        return json.dumps({"info": "No Blueprints selected."})

    return json.dumps(blueprints_data, indent=2)

# Execute and print to stdout for capture
print(get_selected_blueprints_json())
"""