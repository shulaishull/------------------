"""
Example Python script for comparing Excel reference settings with TXT config dumps.

This script demonstrates how to:
1. Read an Excel file and extract key-value pairs
2. Read a TXT config file and extract key-value pairs
3. Compare the two datasets using regex patterns
4. Generate a report of differences
"""

import pandas as pd
import re
import json

def extract_excel_data(file_path, sheet_name=0):
    """
    Extract key-value pairs from an Excel file.
    
    Args:
        file_path (str): Path to the Excel file
        sheet_name (int or str): Sheet name or index to read
        
    Returns:
        dict: Dictionary of key-value pairs
    """
    # Read the Excel file
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    
    # Assuming the first column contains keys and the second contains values
    if len(df.columns) >= 2:
        keys = df.iloc[:, 0].astype(str).tolist()
        values = df.iloc[:, 1].astype(str).tolist()
        return dict(zip(keys, values))
    else:
        raise ValueError("Excel file must have at least 2 columns for key-value pairs")

def extract_txt_config(file_path, pattern=r'^(\w+)=(.+)$'):
    """
    Extract key-value pairs from a TXT config file using regex.
    
    Args:
        file_path (str): Path to the TXT config file
        pattern (str): Regex pattern with two capturing groups for key and value
        
    Returns:
        dict: Dictionary of key-value pairs
    """
    config = {}
    with open(file_path, 'r') as f:
        for line in f:
            match = re.match(pattern, line.strip())
            if match:
                key, value = match.groups()
                config[key] = value
    return config

def compare_configs(excel_data, txt_config):
    """
    Compare two configuration dictionaries.
    
    Args:
        excel_data (dict): Reference data from Excel
        txt_config (dict): Configuration data from TXT
        
    Returns:
        dict: Comparison results with differences
    """
    results = {
        'only_in_excel': {},
        'only_in_txt': {},
        'different_values': {},
        'matching': {}
    }
    
    # Find keys in Excel but not in TXT
    for key, value in excel_data.items():
        if key not in txt_config:
            results['only_in_excel'][key] = value
        elif excel_data[key] != txt_config[key]:
            results['different_values'][key] = {
                'excel': value,
                'txt': txt_config[key]
            }
        else:
            results['matching'][key] = value
    
    # Find keys in TXT but not in Excel
    for key, value in txt_config.items():
        if key not in excel_data:
            results['only_in_txt'][key] = value
    
    return results

def generate_report(comparison_results, output_file=None):
    """
    Generate a human-readable report of the comparison.
    
    Args:
        comparison_results (dict): Results from compare_configs
        output_file (str): Optional file path to save the report
        
    Returns:
        str: Formatted report string
    """
    report = []
    report.append("Configuration Comparison Report")
    report.append("=" * 40)
    
    # Matching configurations
    if comparison_results['matching']:
        report.append(f"\nMatching configurations ({len(comparison_results['matching'])}):")
        for key, value in comparison_results['matching'].items():
            report.append(f"  {key} = {value}")
    
    # Different values
    if comparison_results['different_values']:
        report.append(f"\nDifferent values ({len(comparison_results['different_values'])}):")
        for key, values in comparison_results['different_values'].items():
            report.append(f"  {key}:")
            report.append(f"    Excel: {values['excel']}")
            report.append(f"    TXT:   {values['txt']}")
    
    # Only in Excel
    if comparison_results['only_in_excel']:
        report.append(f"\nOnly in Excel ({len(comparison_results['only_in_excel'])}):")
        for key, value in comparison_results['only_in_excel'].items():
            report.append(f"  {key} = {value}")
    
    # Only in TXT
    if comparison_results['only_in_txt']:
        report.append(f"\nOnly in TXT config ({len(comparison_results['only_in_txt'])}):")
        for key, value in comparison_results['only_in_txt'].items():
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
    # excel_data = extract_excel_data("reference_settings.xlsx")
    # txt_config = extract_txt_config("config_dump.txt")
    
    # For demonstration, using sample data
    excel_data = {
        "setting1": "value1",
        "setting2": "value2",
        "setting3": "value3",
        "setting4": "value4"
    }
    
    txt_config = {
        "setting1": "value1",      # Matching
        "setting2": "different",   # Different value
        "setting3": "value3",      # Matching
        "setting5": "value5"       # Only in TXT
    }
    
    # Compare the configurations
    results = compare_configs(excel_data, txt_config)
    
    # Generate and print the report
    report = generate_report(results)
    print(report)
    
    # Save to JSON for further processing
    with open("comparison_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nDetailed results saved to comparison_results.json")