"""
make sure you have run these commands in the directory before hand
    cat requirements_*.txt > combined_requirements.txt
    sort -u combined_requirements.txt -o sorted_requirements.txt

and make sure the files are formatted to utf-8

"""

import re

# Function to parse the module name and version
def parse_line(line):
    match = re.match(r'(\S+)==(\S+)', line.strip())
    if match:
        return match.groups()
    return None, None

# Function to get the highest version for each module
def get_highest_versions(file_path):
    modules = {}
    with open(file_path, 'r') as f:
        for line in f:
            module, version = parse_line(line)
            if module:
                if module not in modules or version > modules[module]:
                    modules[module] = version
    return modules

# Function to write the unique modules with highest versions to a new file
def write_sorted_requirements(modules, output_path):
    with open(output_path, 'w') as f:
        for module, version in sorted(modules.items()):
            f.write(f'{module}=={version}\n')

# Main execution
input_file = 'sorted_requirements.txt'
output_file = 'unique_requirements.txt'

highest_versions = get_highest_versions(input_file)
write_sorted_requirements(highest_versions, output_file)

print(f"Processed modules written to {output_file}")
