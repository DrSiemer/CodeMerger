import re
import logging

log = logging.getLogger("CodeMerger")

class StarterApiParsing:
    """API methods for parsing segmented LLM output and assembling documents."""

    def parse_starter_segments(self, text):
        """Parses segmented XML-style output from LLM for the Project Starter."""
        pattern = re.compile(r'<SECTION name="([^"]+)">\s*(.*?)(?=</SECTION>|<SECTION name=|$)', re.DOTALL | re.IGNORECASE)
        matches = pattern.findall(text)
        segments = {}
        if not matches: return {}
        for name, content in matches: segments[name.strip()] = content.strip()
        return segments

    def map_parsed_segments_to_keys(self, parsed_data, friendly_names_map):
        """Maps friendly display names from LLM output to internal data keys."""
        def normalize(s): return re.sub(r'[^a-z0-9]', '', s.lower())
        norm_label_to_key = {normalize(v): k for k, v in friendly_names_map.items()}
        norm_key_to_key = {normalize(k): k for k in friendly_names_map.keys()}
        keyed_data = {}
        for name, content in parsed_data.items():
            norm_name = normalize(name)
            key = norm_label_to_key.get(norm_name)
            if not key: key = norm_key_to_key.get(norm_name)
            if key: keyed_data[key] = content
            else: keyed_data[name] = content
        return keyed_data

    def assemble_starter_document(self, segments_dict, order_keys, friendly_names_map):
        """Combines multiple segments into a single Markdown document."""
        doc_parts = []
        for key in order_keys:
            if key in segments_dict and segments_dict[key].strip():
                friendly_name = friendly_names_map.get(key, key)
                content = segments_dict[key].strip()
                doc_parts.append(f"## {friendly_name}\n\n{content}")
        return "\n\n".join(doc_parts)