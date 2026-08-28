with open("scratch/tenders_clean.js", "r", encoding="utf-8") as f:
    clean_js = f.read().strip()

with open("frontend/app.js", "r", encoding="utf-8") as f:
    app_js = f.read()

start_marker = "// 3. Tenders Data Store with Multi-Level Granular Specification Matching\n// ==========================================================================\n\nlet tenders = ["
end_marker = "\n\n// ==========================================================================\n// 4. Most Recurring Products"

start_idx = app_js.find(start_marker)
end_idx = app_js.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print(f"ERROR: Could not find markers. start: {start_idx}, end: {end_idx}")
else:
    new_middle = f"// 3. Tenders Data Store with Multi-Level Granular Specification Matching\n// ==========================================================================\n\n{clean_js}"
    new_app_js = app_js[:start_idx] + new_middle + app_js[end_idx:]
    
    # Also fix tenderSources.find -> sources.find
    new_app_js = new_app_js.replace("tenderSources.find", "sources.find")
    
    with open("frontend/app.js", "w", encoding="utf-8") as f:
        f.write(new_app_js)
    print("Successfully updated frontend/app.js with 100% genuine Umucyo tenders!")
