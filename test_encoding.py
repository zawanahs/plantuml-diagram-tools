#!/usr/bin/env python3
"""Test PlantUML encoding with ~1 prefix"""

import zlib
import base64

def encode_plantuml(text: str) -> str:
    """Encode PlantUML text using zlib and base64."""
    compressed = zlib.compress(text.encode("utf-8"))
    # Use full compressed data and add ~1 prefix for HUFFMAN encoding
    encoded = base64.urlsafe_b64encode(compressed[2:-4]).decode("utf-8").rstrip("=")
    return encoded

# Test code
test_uml = """@startuml
start
:Initialize System;
:Check Configuration;
if (Config Valid?) then (yes)
  :Process Data;
  :Generate Output;
else (no)
  :Log Error;
endif
stop
@enduml"""

encoded = encode_plantuml(test_uml)
print(f"Encoded (without ~1): {encoded}")
print(f"\nFull URL with ~1 prefix:")
print(f"http://www.plantuml.com/plantuml/svg/~1{encoded}")