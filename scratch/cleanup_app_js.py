"""
Clean up duplicate functions in frontend/app.js
"""
import re

with open("frontend/app.js", "r", encoding="utf-8") as f:
    code = f.read()

# Let's locate the duplicate renderSources block at lines 11932-12071
old_sources_block_start = "  // Sources Controller\n  function renderSources() {"
old_sources_block_end = "  // Add Source Modal Controller"

start_idx = code.find(old_sources_block_start)
end_idx = code.find(old_sources_block_end)

if start_idx != -1 and end_idx != -1:
    code = code[:start_idx] + code[end_idx:]
    print("Removed duplicate older sources controller block.")
else:
    print("Could not find exact older sources controller block:", start_idx, end_idx)

# Remove duplicate scanAllSourcesBtn and openAddSourceBtn at bottom if present
# Check if scanAllSourcesBtn is declared multiple times
btn_pattern = r"const scanAllSourcesBtn = document\.querySelector\('#scanAllSourcesBtn'\);"
matches = list(re.finditer(btn_pattern, code))
if len(matches) > 1:
    print(f"Found {len(matches)} declarations of scanAllSourcesBtn. Cleaning up.")

with open("frontend/app.js", "w", encoding="utf-8") as f:
    f.write(code)

print("Saved cleaned frontend/app.js.")
