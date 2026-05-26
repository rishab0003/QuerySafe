import os
import sys
import csv

def csv_to_postgres_sql(csv_filepath, table_name, output_sql_path):
    print(f"Reading CSV from {csv_filepath}...")
    
    if not os.path.exists(csv_filepath):
        print(f"Error: CSV file '{csv_filepath}' not found.")
        sys.exit(1)
        
    with open(csv_filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        try:
            headers = next(reader)
        except StopIteration:
            print("Error: The CSV file is empty.")
            sys.exit(1)
            
        # Clean column names to be Postgres-safe
        clean_headers = [
            h.strip().lower().replace(' ', '_').replace('-', '_').replace('.', '_').replace('/', '_') 
            for h in headers
        ]
        
        # Read all rows to analyze data types (best-effort mapping)
        rows = list(reader)
        
    print(f"Analyzing {len(rows)} rows to determine columns...")
    
    # Simple type inference
    col_types = [None] * len(clean_headers)
    for row in rows:
        for i, val in enumerate(row):
            if i >= len(col_types):
                continue
            val = val.strip()
            if not val:
                continue
            # If we already classified as TEXT, keep it
            if col_types[i] == 'TEXT':
                continue
                
            # Test boolean
            if val.lower() in ('true', 'false', 'yes', 'no'):
                if col_types[i] is None or col_types[i] == 'BOOLEAN':
                    col_types[i] = 'BOOLEAN'
                else:
                    col_types[i] = 'TEXT'
                continue
            
            # Test integer
            try:
                int(val)
                if col_types[i] is None or col_types[i] == 'INTEGER':
                    col_types[i] = 'INTEGER'
                else:
                    col_types[i] = 'TEXT'
                continue
            except ValueError:
                pass
                
            # Test numeric/float
            try:
                float(val)
                if col_types[i] is None or col_types[i] in ('INTEGER', 'NUMERIC'):
                    col_types[i] = 'NUMERIC'
                else:
                    col_types[i] = 'TEXT'
                continue
            except ValueError:
                pass
                
            col_types[i] = 'TEXT'
            
    # Default remaining None types to TEXT
    col_types = [t if t is not None else 'TEXT' for t in col_types]
    
    sql_lines = []
    sql_lines.append(f"-- Auto-generated migration from {os.path.basename(csv_filepath)}")
    sql_lines.append(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
    sql_lines.append(f"CREATE TABLE {table_name} (")
    
    col_defs = []
    for col, dtype in zip(clean_headers, col_types):
        col_defs.append(f"    {col} {dtype}")
        
    sql_lines.append(",\n".join(col_defs))
    sql_lines.append(");\n")
    
    print(f"Generating INSERT statements for {len(rows)} rows...")
    
    for row in rows:
        vals = []
        for i, val in enumerate(row):
            if i >= len(col_types):
                continue
            val = val.strip()
            dtype = col_types[i]
            
            if not val:
                vals.append("NULL")
            elif dtype == 'BOOLEAN':
                if val.lower() in ('true', 'yes'):
                    vals.append("TRUE")
                else:
                    vals.append("FALSE")
            elif dtype in ('INTEGER', 'NUMERIC'):
                vals.append(val)
            else:
                escaped_val = val.replace("'", "''")
                vals.append(f"'{escaped_val}'")
                
        # Fill in missing columns if the row had fewer elements
        while len(vals) < len(clean_headers):
            vals.append("NULL")
            
        sql_lines.append(f"INSERT INTO {table_name} ({', '.join(clean_headers)}) VALUES ({', '.join(vals)});")
        
    # Write to target migration file
    with open(output_sql_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(sql_lines))
        
    print(f"Success! Generated migration at {output_sql_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/csv_to_sql.py <path_to_csv> <table_name>")
        sys.exit(1)
        
    csv_file = sys.argv[1]
    tbl_name = sys.argv[2]
    out_file = os.path.join(os.path.dirname(__file__), "../migrations/002_dataset.sql")
    
    csv_to_postgres_sql(csv_file, tbl_name, out_file)
