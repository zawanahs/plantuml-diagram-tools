#!/usr/bin/env python3
"""
Test script to generate diagrams using the UML-MCP server functionality
"""

import os
import sys
import requests
from pathlib import Path

# Add the uml-mcp directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "uml-mcp"))

# Use local PlantUML server if available, otherwise remote
USE_LOCAL_PLANTUML = os.environ.get("USE_LOCAL_PLANTUML", "true").lower() == "true"
if USE_LOCAL_PLANTUML:
    PLANTUML_SERVER = os.environ.get("PLANTUML_SERVER", "http://localhost:8080")
else:
    PLANTUML_SERVER = os.environ.get("PLANTUML_SERVER", "http://www.plantuml.com/plantuml")

def generate_diagram_url(code: str, fmt: str = "svg") -> str:
    """Generate a diagram URL using the PlantUML server's proper encoding."""
    try:
        # Import the PlantUML class from the uml-mcp module
        from plantuml import PlantUML
        
        # Create PlantUML instance with appropriate server URL
        plantuml_url = f"{PLANTUML_SERVER}/{fmt}"
        server = PlantUML(plantuml_url)
        url, content, playground = server.generate_image_from_string(code)
        return url
    except ImportError:
        print("Warning: Could not import PlantUML module, falling back to basic encoding")
        # Fallback to PlantUML encoding similar to what the module uses
        import zlib
        
        # Use the same encoding method as in the PlantUML module
        zlibbed_str = zlib.compress(code.encode('utf-8'))
        compressed_string = zlibbed_str[2:-4]
        
        # Encode using PlantUML's custom base64 variant
        def encode_plantuml_chars(data: bytes) -> str:
            res = ""
            for i in range(0, len(data), 3):
                if i + 2 == len(data):
                    res += encode_3bytes(data[i], data[i + 1], 0)
                elif i + 1 == len(data):
                    res += encode_3bytes(data[i], 0, 0)
                else:
                    res += encode_3bytes(data[i], data[i + 1], data[i + 2])
            return res
        
        def encode_3bytes(b1: int, b2: int, b3: int) -> str:
            c1 = b1 >> 2
            c2 = ((b1 & 0x3) << 4) | (b2 >> 4)
            c3 = ((b2 & 0xF) << 2) | (b3 >> 6)
            c4 = b3 & 0x3F
            res = ""
            res += encode_6bit(c1 & 0x3F)
            res += encode_6bit(c2 & 0x3F)
            res += encode_6bit(c3 & 0x3F)
            res += encode_6bit(c4 & 0x3F)
            return res
        
        def encode_6bit(b: int) -> str:
            if b < 10:
                return chr(48 + b)
            b -= 10
            if b < 26:
                return chr(65 + b)
            b -= 26
            if b < 26:
                return chr(97 + b)
            b -= 26
            if b == 0:
                return '-'
            return '_' if b == 1 else '?'
        
        encoded = encode_plantuml_chars(compressed_string)
        return f"{PLANTUML_SERVER}/{fmt}/{encoded}"

def save_diagram(url: str, filename: str, fmt: str = "svg") -> bool:
    """Download and save a diagram from the given URL."""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            output_dir = Path(__file__).parent / "output"
            output_dir.mkdir(exist_ok=True)
            
            output_file = output_dir / f"{filename}.{fmt}"
            with open(output_file, 'wb') as f:
                f.write(response.content)
            print(f"  ✓ Saved: {output_file}")
            return True
        else:
            print(f"  ✗ Server returned status: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"  ✗ Error downloading diagram: {e}")
        return False

def test_diagrams():
    """Test diagram generation with the example files."""
    diagrams_dir = Path(__file__).parent / "diagrams"
    
    print(f"Testing PlantUML diagram generation...")
    print(f"Server: {PLANTUML_SERVER}")
    print(f"Local PlantUML: {'Yes' if USE_LOCAL_PLANTUML else 'No'}")
    print("-" * 50)
    
    if not diagrams_dir.exists():
        print(f"Error: Diagrams directory not found at {diagrams_dir}")
        return
    
    puml_files = list(diagrams_dir.glob("*.puml"))
    if not puml_files:
        print(f"No .puml files found in {diagrams_dir}")
        return
    
    for puml_file in puml_files:
        print(f"\nProcessing: {puml_file.name}")
        
        try:
            with open(puml_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"  ✗ Error reading file: {e}")
            continue
        
        # Generate URLs for different formats
        try:
            svg_url = generate_diagram_url(content, "svg")
            png_url = generate_diagram_url(content, "png")
            
            print(f"  SVG URL: {svg_url}")
            print(f"  PNG URL: {png_url}")
            
            # Test and save diagrams
            base_name = puml_file.stem
            svg_success = save_diagram(svg_url, base_name, "svg")
            png_success = save_diagram(png_url, base_name, "png")
            
            if svg_success or png_success:
                print(f"  ✓ Diagram generation successful!")
            else:
                print(f"  ✗ Failed to generate diagrams")
                
        except Exception as e:
            print(f"  ✗ Error generating diagram URLs: {e}")
    
    print("\n" + "-" * 50)
    print("Test complete!")
    print(f"Generated diagrams saved to: {Path(__file__).parent / 'output'}")

if __name__ == "__main__":
    test_diagrams()