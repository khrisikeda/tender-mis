import json
import sys
sys.path.insert(0, ".")

with open("scratch/all_market_tenders.json", "r", encoding="utf-8") as f:
    tenders_data = json.load(f)

from scratch.generate_all_tenders import sources_list

with open("frontend/app.js", "r", encoding="utf-8") as f:
    app_js = f.read()

# Locate tenders array start & end
start_marker_t = "let tenders = ["
end_marker_t = "];\n\n// ==========================================================================\n// 4. Most Recurring Products"

start_idx_t = app_js.find(start_marker_t)
end_idx_t = app_js.find(end_marker_t)

if start_idx_t != -1 and end_idx_t != -1:
    tenders_json_str = json.dumps(tenders_data, indent=2)
    app_js = app_js[:start_idx_t] + f"let tenders = {tenders_json_str}" + app_js[end_idx_t:]
    print("Replaced tenders successfully.")
else:
    print("WARNING: Could not find exact tender markers:", start_idx_t, end_idx_t)

# Locate sources array start & end
start_marker_s = "let sources = ["
end_marker_s = "];\n\n// Utility Helpers"

start_idx_s = app_js.find(start_marker_s)
end_idx_s = app_js.find(end_marker_s)

if start_idx_s != -1 and end_idx_s != -1:
    sources_json_str = json.dumps(sources_list, indent=2)
    app_js = app_js[:start_idx_s] + f"let sources = {sources_json_str}" + app_js[end_idx_s:]
    print("Replaced sources successfully.")
else:
    print("WARNING: Could not find exact sources markers:", start_idx_s, end_idx_s)

with open("frontend/app.js", "w", encoding="utf-8") as f:
    f.write(app_js)

print("Saved updated app.js.")
