#!/usr/bin/env python3
import csv, sys, json

def format_value(val):
    if val == '':
        return 'NULL'
    elif val.lower() in ['true', 'false']:
        return val.upper()
    elif val.replace('.','').replace('-','').isdigit():
        return val
    elif val.startswith('[') or val.startswith('{'):
        # JSON data - escape properly
        return "'" + val.replace("'", "''") + "'"
    else:
        return "'" + val.replace("'", "''") + "'"

if __name__ == "__main__":
    table = sys.argv[1] if len(sys.argv) > 1 else "unknown_table"
    reader = csv.reader(sys.stdin)
    for row in reader:
        values = [format_value(val) for val in row]
        print(f"INSERT INTO {table} VALUES ({', '.join(values)});")