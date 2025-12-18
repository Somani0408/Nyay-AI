#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script fixes the broken app.py file by removing all broken app.run lines
and adding the correct one at the end.
"""

# Read the entire file
with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find where the error handling ends (should be around line 76-78)
# We'll keep everything up to and including the closing quote and status code
fixed_lines = []
for i, line in enumerate(lines):
    # Stop before any broken app.run lines
    if 'app.run' in line.lower() or "', port=" in line:
        break
    fixed_lines.append(line)

# Make sure we end with the proper function
# Remove any trailing blank lines
while fixed_lines and fixed_lines[-1].strip() == '':
    fixed_lines.pop()

# Add the proper ending
fixed_lines.append('\n')
fixed_lines.append('# 6. Run the Flask App\n')
fixed_lines.append('if __name__ == "__main__":\n')
fixed_lines.append('    app.run(debug=True)\n')

# Write the fixed version
with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("✓ File fixed successfully!")
print("✓ Now run: python app.py")