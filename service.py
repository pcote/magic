"""
Service for Magic the Gathering Data
"""
import json
# ATTENTION: AllSets-x.json is a file resource that needs to be downloaded.
# Find it here: http://mtgjson.com/
json_data = json.load(open("AllSets-x.json", "rt", encoding="utf-8"))