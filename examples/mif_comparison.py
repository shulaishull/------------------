"""
Example Python script for comparing MIF files with configuration dumps.

This script demonstrates how to:
1. Parse MIF files as structured text
2. Extract key-value pairs using regex
3. Compare with other configuration formats
4. Generate difference reports
"""

import re
import json
from typing import Dict, List, Tuple

def parse_mif_file(file_path: str) -> Dict[str, str]:
    """
    Parse a MIF file and extract key-value pairs.
    
    Args:
        file_path (str): Path to the MIF file
        
    Returns:
        dict: Dictionary of key-value pairs extracted from the MIF file
    """
    data = {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # MIF files often have key-value pairs in format: <key> <value>
    # This is a simplified parser - real MIF parsing would be more complex
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines and comments (lines starting with #)
        if not line or line.startswith('#'):
            continue
            
        # Try to match key-value pairs
        # This pattern looks for: key value or key = value
        match = re.match(r'^([A-Za-z_]\w*)\s*=?\s*(.+)$', line)
        if match:
            key, value = match.groups()
            # Clean up the value (remove quotes if present)
            value = value.strip().strip('"\'')
            data[key] = value
    
    return data

def extract_key_value_pairs(text: str, pattern: str = r'^([A-Za-z_]\w*)\s*=\s*(.+)$') -> Dict[str, str]:
    """
    Extract key-value pairs from text using a regex pattern.
    
    Args:
        text (str): Text to parse
        pattern (str): Regex pattern with two capturing groups for key and value
        
    Returns:
        dict: Dictionary of key-value pairs
    """
    data = {}
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue
            
        match = re.match(pattern, line)
        if match:
            key, value = match.groups()
            # Clean up the value (remove quotes if present)
            value = value.strip().strip('"\'')
            data[key] = value
    
    return data

def compare_mif_with_config(mif_data: Dict[str, str], config_data: Dict[str, str]) -> Dict:
    """
    Compare MIF data with configuration data.
    
    Args:
        mif_data (dict): Data extracted from MIF file
        config_data (dict): Data from configuration file
        
    Returns:
        dict: Comparison results
    """
    results = {
        'only_in_mif': {},
        'only_in_config': {},
        'different_values': {},
        'matching': {}
    }
    
    # Find keys in MIF but not in config
    for key, value in mif_data.items():
        if key not in config_data:
            results['only_in_mif'][key] = value
        elif mif_data[key] != config_data[key]:
            results['different_values'][key] = {
                'mif': value,
                'config': config_data[key]
            }
        else:
            results['matching'][key] = value
    
    # Find keys in config but not in MIF
    for key, value in config_data.items():
        if key not in mif_data:
            results['only_in_config'][key] = value
    
    return results

def generate_mif_report(comparison_results: Dict, output_file: str = None) -> str:
    """
    Generate a human-readable report of the MIF comparison.
    
    Args:
        comparison_results (dict): Results from compare_mif_with_config
        output_file (str): Optional file path to save the report
        
    Returns:
        str: Formatted report string
    """
    report = []
    report.append("MIF File Comparison Report")
    report.append("=" * 35)
    
    # Matching configurations
    if comparison_results['matching']:
        report.append(f"\nMatching entries ({len(comparison_results['matching'])}):")
        for key, value in comparison_results['matching'].items():
            report.append(f"  {key} = {value}")
    
    # Different values
    if comparison_results['different_values']:
        report.append(f"\nDifferent values ({len(comparison_results['different_values'])}):")
        for key, values in comparison_results['different_values'].items():
            report.append(f"  {key}:")
            report.append(f"    MIF:     {values['mif']}")
            report.append(f"    Config:  {values['config']}")
    
    # Only in MIF
    if comparison_results['only_in_mif']:
        report.append(f"\nOnly in MIF file ({len(comparison_results['only_in_mif'])}):")
        for key, value in comparison_results['only_in_mif'].items():
            report.append(f"  {key} = {value}")
    
    # Only in config
    if comparison_results['only_in_config']:
        report.append(f"\nOnly in config file ({len(comparison_results['only_in_config'])}):")
        for key, value in comparison_results['only_in_config'].items():
            report.append(f"  {key} = {value}")
    
    report_str = "\n".join(report)
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(report_str)
        print(f"Report saved to {output_file}")
    
    return report_str

# Example usage
if __name__ == "__main__":
    # Example data - in a real scenario, you would read actual files
    # mif_data = parse_mif_file("reference.mif")
    # config_data = extract_key_value_pairs("config.txt")
    
    # For demonstration, using sample data
    mif_data = {
        "PageSize": "A4",
        "Orientation": "Portrait",
        "Font": "Times New Roman",
        "FontSize": "12"
    }
    
    config_data = {
        "PageSize": "A4",           # Matching
        "Orientation": "Landscape", # Different value
        "Font": "Times New Roman",  # Matching
        "Color": "Black"            # Only in config
    }
    
    # Compare the data
    results = compare_mif_with_config(mif_data, config_data)
    
    # Generate and print the report
    report = generate_mif_report(results)
    print(report)
    
    # Save to JSON for further processing
    with open("mif_comparison_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nDetailed results saved to mif_comparison_results.json")