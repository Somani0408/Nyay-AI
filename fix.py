# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the broken line
content = content.replace("app.run(host='192.168.1.6", "    app.run(debug=True)")

# Also remove any duplicate app.run lines
lines = content.split('\n')
fixed_lines = []
seen_app_run = False

for line in lines:
    if 'app.run' in line:
        if not seen_app_run:
            fixed_lines.append('    app.run(debug=True)')
            seen_app_run = True
    else:
        fixed_lines.append(line)

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(fixed_lines))

print("Fixed! Now run: python app.py")