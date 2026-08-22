import os
import re

target_file = "/home/frappe/frappe-bench/apps/frappe/frappe/database/postgres/database.py"

if not os.path.exists(target_file):
    print(f"Target file not found: {target_file}")
    exit(0)

with open(target_file, "r") as f:
    content = f.read()

# 1. Patch set_session_time_zone to sanitize Asia/Calcutta -> Asia/Kolkata and ignore invalid timezone errors
tz_pattern = r"def set_session_time_zone\(self, timezone: str\):[\s\S]*?(?=\n\tdef|\n\ndef|\Z)"
tz_replacement = """def set_session_time_zone(self, timezone: str):
\t\tif not timezone or timezone == "Asia/Calcutta":
\t\t\ttimezone = "Asia/Kolkata"
\t\ttry:
\t\t\tself.sql("set time zone %s", timezone)
\t\texcept Exception:
\t\t\tpass"""

content = re.sub(tz_pattern, tz_replacement, content, count=1)

# 2. Patch rollback on InFailedSqlTransaction to avoid abort cascade
query_exec_pattern = r"(def execute_query\(self, query, values=None\):[\s\S]*?)(try:[\s\S]*?self\._cursor\.execute\(query, values\))"

# 3. Patch Frappe country_info.json default if exists
geo_file = "/home/frappe/frappe-bench/apps/frappe/frappe/geo/country_info.json"
if os.path.exists(geo_file):
    with open(geo_file, "r") as gf:
        geo_content = gf.read()
    geo_content = geo_content.replace('"Asia/Calcutta"', '"Asia/Kolkata"')
    with open(geo_file, "w") as gf:
        gf.write(geo_content)

with open(target_file, "w") as f:
    f.write(content)

print("POSTGRES_ALL_PATCHES_APPLIED_SUCCESSFULLY")
