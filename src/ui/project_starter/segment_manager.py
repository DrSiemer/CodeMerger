import re
from ...constants import DELIMITER_TEMPLATE

class SegmentManager:
    """
    Helper class for constructing segmented prompts, parsing LLM responses,
    and assembling the final document from segments.
    """

    @staticmethod
    def build_prompt_instructions(segment_keys, friendly_names_map):
        """
        Generates the system instructions enforcing the strict delimiter format.
        Args:
            segment_keys (list): List of keys to include in the prompt.
            friendly_names_map (dict): Mapping from key to display name.
        """
        instructions = [
            "You MUST structure your response using specific section separators.",
            "Do not add any text outside these sections.",
            "For each section, output the delimiter followed immediately by the content.",
            "\nREQUIRED FORMAT:"
        ]

        for key in segment_keys:
            name = friendly_names_map.get(key, key)
            delimiter = DELIMITER_TEMPLATE.format(name=name)
            instructions.append(f"{delimiter}\n... content for {name} ...")

        return "\n".join(instructions)

    @staticmethod
    def parse_segments(text):
        """
        Parses the LLM output into a dictionary { "Section Name": "Content" }.
        Uses regex to find <<SECTION: Name>> followed by content.
        """
        # Regex to find <<SECTION: Name>> followed by content until the next section or end of string
        # re.DOTALL allows . to match newlines
        pattern = re.compile(r'<<SECTION:\s*(.*?)>>\s*(.*?)(?=<<SECTION:|$)', re.DOTALL)

        matches = pattern.findall(text)
        segments = {}

        if not matches:
            return {}

        for name, content in matches:
            segments[name.strip()] = content.strip()

        return segments

    @staticmethod
    def map_parsed_segments_to_keys(parsed_data, friendly_names_map):
        """
        Converts the dict { "Friendly Name": "Content" } to { "key": "Content" }
        based on the provided mapping. Keys not in the map are kept as is.
        """
        # Invert map: Name -> Key
        name_to_key = {v: k for k, v in friendly_names_map.items()}

        keyed_data = {}
        for name, content in parsed_data.items():
            key = name_to_key.get(name)
            if key:
                keyed_data[key] = content
            else:
                # Fallback for hallucinated or mismatched section names
                keyed_data[name] = content
        return keyed_data

    @staticmethod
    def assemble_document(segments_dict, order_keys, friendly_names_map):
        """
        Joins segments into a single Markdown document with headers.
        Args:
            segments_dict (dict): The content { key: content }.
            order_keys (list): The order in which to assemble the keys.
            friendly_names_map (dict): Mapping to use for the Markdown headers.
        """
        doc_parts = []
        for key in order_keys:
            if key in segments_dict and segments_dict[key].strip():
                friendly_name = friendly_names_map.get(key, key)
                content = segments_dict[key].strip()
                doc_parts.append(f"## {friendly_name}\n\n{content}")

        return "\n\n".join(doc_parts)