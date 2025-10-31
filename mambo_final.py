"""
MAMBO CONTACT CLEANER - COMPLETE WORKING VERSION
All features with proper error handling
"""

import pandas as pd
import os
from datetime import datetime
import re

print("\n" + "="*70)
print("MAMBO COMPLETE VERSION - ALL FEATURES")
print("="*70 + "\n")

class MamboContactCleaner:
    def __init__(self):
        self.base_path = os.getcwd()
        self.inputs_path = os.path.join(self.base_path, 'inputs')
        self.lookups_path = os.path.join(self.base_path, 'lookups')
        
        # Lookup files in lookups folder
        self.lookup_file = os.path.join(self.lookups_path, 'column_map_lookup.csv')
        self.compound_names_file = os.path.join(self.lookups_path, 'compound_names.csv')
        self.prefixes_file = os.path.join(self.lookups_path, 'prefixes.csv')
        self.suffixes_file = os.path.join(self.lookups_path, 'suffixes.csv')
        
        self.output_excel = f'mambo_output_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        self.column_mappings = {}
        self.column_order = {}
        self.compound_names = set()
        self.prefixes = set()
        self.suffixes = set()
        
        # Track new learned patterns
        self.new_prefixes = set()
        self.new_suffixes = set()
        self.new_compound_names = set()
        
        self.log_messages = []
    
    def log(self, message):
        print(message)
        self.log_messages.append(message)
    
    def load_lookup_table(self):
        """Load column mapping lookup table"""
        if not os.path.exists(self.lookup_file):
            self.log(f"  No lookup file found: {self.lookup_file}")
            return False
        
        df = pd.read_csv(self.lookup_file)
        self.log(f"✓ Found lookup file: column_map_lookup.csv")
        self.log(f"✓ Loaded {len(df)} mapping rows")
        
        # Build mappings dictionary
        mappings_count = 0
        for _, row in df.iterrows():
            source_col = str(row.get('Source_Column_Name', '')).strip()
            target_col = str(row.get('Target_Column_Name', '')).strip()
            source = str(row.get('Source', '')).strip()
            
            if source_col and target_col and source:
                key = f"{source}::{source_col}"
                self.column_mappings[key] = target_col
                mappings_count += 1
        
        self.log(f"✓ Created {mappings_count} mappings")
        
        # Build column order dictionary
        order_count = 0
        for _, row in df.iterrows():
            source = str(row.get('Source', '')).strip()
            order = row.get('Target_Column_Order', None)
            target_col = str(row.get('Target_Column_Name', '')).strip()
            
            if source and pd.notna(order) and target_col:
                if source not in self.column_order:
                    self.column_order[source] = {}
                self.column_order[source][target_col] = int(order)
                order_count += 1
        
        self.log(f"✓ Stored {order_count} column orderings")
        return True
    
    def load_prefixes(self):
        """Load name prefixes from CSV"""
        if not os.path.exists(self.prefixes_file):
            self.log(f"  No prefixes file found - using defaults")
            # Default prefixes if file doesn't exist
            self.prefixes = {'mr', 'mrs', 'ms', 'miss', 'dr', 'prof', 'rev', 'fr', 'sr', 'sra', 'srta'}
            return False
        
        df = pd.read_csv(self.prefixes_file)
        # Assume first column contains prefixes
        self.prefixes = set(df.iloc[:, 0].str.lower().str.strip())
        self.log(f"✓ Loaded {len(self.prefixes)} prefixes from file")
        return True
    
    def load_suffixes(self):
        """Load name suffixes from CSV"""
        if not os.path.exists(self.suffixes_file):
            self.log(f"  No suffixes file found - using defaults")
            # Default suffixes if file doesn't exist
            self.suffixes = {'jr', 'sr', 'ii', 'iii', 'iv', 'v', 'esq', 'phd', 'md', 'dds', 'dvm'}
            return False
        
        df = pd.read_csv(self.suffixes_file)
        # Assume first column contains suffixes
        self.suffixes = set(df.iloc[:, 0].str.lower().str.strip())
        self.log(f"✓ Loaded {len(self.suffixes)} suffixes from file")
        return True
    
    def load_compound_names(self):
        """Load compound first names"""
        if not os.path.exists(self.compound_names_file):
            self.log(f"  No compound names file")
            return False
        
        df = pd.read_csv(self.compound_names_file)
        self.compound_names = set(df.iloc[:, 0].str.lower().str.strip())
        self.log(f"✓ Loaded {len(self.compound_names)} compound names")
        return True
    
    def save_learned_patterns(self):
        """Save newly learned prefixes, suffixes, and compound names back to CSV files"""
        self.log(f"\nSaving learned patterns...")
        
        saved_count = 0
        
        # Save new prefixes
        if self.new_prefixes:
            try:
                # Load existing prefixes
                if os.path.exists(self.prefixes_file):
                    existing = pd.read_csv(self.prefixes_file)
                    all_prefixes = set(existing.iloc[:, 0].str.lower().str.strip()) | self.new_prefixes
                else:
                    all_prefixes = self.prefixes | self.new_prefixes
                
                # Save back to file
                df = pd.DataFrame(sorted(all_prefixes), columns=['Prefix'])
                df.to_csv(self.prefixes_file, index=False)
                self.log(f"  Saved {len(self.new_prefixes)} new prefixes")
                saved_count += len(self.new_prefixes)
            except Exception as e:
                self.log(f"  Error saving prefixes: {e}")
        
        # Save new suffixes
        if self.new_suffixes:
            try:
                # Load existing suffixes
                if os.path.exists(self.suffixes_file):
                    existing = pd.read_csv(self.suffixes_file)
                    all_suffixes = set(existing.iloc[:, 0].str.lower().str.strip()) | self.new_suffixes
                else:
                    all_suffixes = self.suffixes | self.new_suffixes
                
                # Save back to file
                df = pd.DataFrame(sorted(all_suffixes), columns=['Suffix'])
                df.to_csv(self.suffixes_file, index=False)
                self.log(f"  Saved {len(self.new_suffixes)} new suffixes")
                saved_count += len(self.new_suffixes)
            except Exception as e:
                self.log(f"  Error saving suffixes: {e}")
        
        # Save new compound names
        if self.new_compound_names:
            try:
                # Load existing compound names
                if os.path.exists(self.compound_names_file):
                    existing = pd.read_csv(self.compound_names_file)
                    all_compounds = set(existing.iloc[:, 0].str.lower().str.strip()) | self.new_compound_names
                else:
                    all_compounds = self.compound_names | self.new_compound_names
                
                # Save back to file
                df = pd.DataFrame(sorted(all_compounds), columns=['Compound_Name'])
                df.to_csv(self.compound_names_file, index=False)
                self.log(f"  Saved {len(self.new_compound_names)} new compound names")
                saved_count += len(self.new_compound_names)
            except Exception as e:
                self.log(f"  Error saving compound names: {e}")
        
        if saved_count == 0:
            self.log(f"  No new patterns learned this run")
        
        return saved_count
    
    def load_csv_files(self):
        """Load all CSV files from inputs directory"""
        # Check if inputs folder exists
        if not os.path.exists(self.inputs_path):
            self.log(f"\nERROR: 'inputs' folder not found!")
            self.log(f"Expected location: {self.inputs_path}")
            self.log("Please create an 'inputs' folder and place your CSV files there.")
            raise FileNotFoundError("inputs folder not found")
        
        # Get all CSV files from inputs folder
        files = [f for f in os.listdir(self.inputs_path) 
                if f.endswith('.csv') and f != self.lookup_file and f != self.compound_names_file]
        
        self.log(f"\nFound {len(files)} CSV files in inputs folder")
        
        if len(files) == 0:
            self.log("\n" + "="*70)
            self.log("ERROR: No CSV files found in inputs folder!")
            self.log("="*70)
            self.log(f"\nLooking in: {self.inputs_path}")
            self.log("\nPlease ensure your CSV files are in the inputs folder.")
            self.log("Looking for files like:")
            self.log("  - Gmail - DDL.csv")
            self.log("  - iPhone - DDL.csv")
            self.log("  - LinkedIn - Connections.csv")
            self.log("  - etc.")
            self.log("\nFiles in inputs directory:")
            all_files = os.listdir(self.inputs_path)
            csv_files = [f for f in all_files if f.endswith('.csv')]
            if csv_files:
                for f in csv_files:
                    self.log(f"  {f}")
            else:
                self.log("  (no CSV files found)")
            raise FileNotFoundError("No CSV source files found in inputs directory")
        
        dataframes = []
        for i, file in enumerate(files, 1):
            try:
                filepath = os.path.join(self.inputs_path, file)
                df = pd.read_csv(filepath, encoding='utf-8', on_bad_lines='skip')
                df['Source'] = file
                self.log(f"[{i}] {file}")
                self.log(f"  {len(df)} rows")
                dataframes.append(df)
            except Exception as e:
                self.log(f"[{i}] {file} - ERROR: {e}")
        
        if len(dataframes) == 0:
            raise ValueError("No CSV files could be loaded successfully")
        
        return pd.concat(dataframes, ignore_index=True, sort=False)
    
    def apply_column_mapping(self, df):
        """Apply column mappings from lookup table"""
        mapped_df = df.copy()
        
        for col in mapped_df.columns:
            if col == 'Source':
                continue
            
            for idx, row in mapped_df.iterrows():
                source = row['Source']
                key = f"{source}::{col}"
                
                if key in self.column_mappings:
                    target_col = self.column_mappings[key]
                    
                    if target_col not in mapped_df.columns:
                        mapped_df[target_col] = None
                    
                    if pd.notna(row[col]):
                        mapped_df.at[idx, target_col] = row[col]
        
        return mapped_df
    
    def reorder_columns(self, df):
        """Reorder columns: Source first, then by Target_Column_Order from lookup"""
        source_col = ['Source']
        other_cols = [col for col in df.columns if col != 'Source']
        
        # Get all unique sources
        sources = df['Source'].unique()
        
        # Build comprehensive ordering
        all_orders = {}
        for source in sources:
            if source in self.column_order:
                for col, order in self.column_order[source].items():
                    if col in other_cols:
                        if col not in all_orders:
                            all_orders[col] = []
                        all_orders[col].append(order)
        
        # Average the orders for each column
        col_avg_order = {}
        for col, orders in all_orders.items():
            col_avg_order[col] = sum(orders) / len(orders)
        
        # Sort columns by average order
        ordered_cols = sorted([col for col in other_cols if col in col_avg_order],
                            key=lambda x: col_avg_order[x])
        
        # Add columns not in ordering at the end
        unordered_cols = [col for col in other_cols if col not in col_avg_order]
        
        final_order = source_col + ordered_cols + unordered_cols
        
        return df[final_order]
    
    def parse_name_field(self, name_str):
        """Parse a name string into components"""
        if pd.isna(name_str) or not str(name_str).strip():
            return {'first': '', 'middle': '', 'last': '', 'prefix': '', 'suffix': ''}
        
        name_str = str(name_str).strip()
        parts = name_str.split()
        
        if len(parts) == 0:
            return {'first': '', 'middle': '', 'last': '', 'prefix': '', 'suffix': ''}
        
        result = {'first': '', 'middle': '', 'last': '', 'prefix': '', 'suffix': ''}
        
        # Check for prefix
        if parts[0].lower().replace('.', '') in self.prefixes:
            result['prefix'] = parts[0]
            parts = parts[1:]
        
        # Check for suffix
        if len(parts) > 0 and parts[-1].lower().replace('.', '') in self.suffixes:
            result['suffix'] = parts[-1]
            parts = parts[:-1]
        
        # Assign remaining parts
        if len(parts) == 1:
            result['first'] = parts[0]
        elif len(parts) == 2:
            result['first'] = parts[0]
            result['last'] = parts[1]
        elif len(parts) >= 3:
            result['first'] = parts[0]
            result['middle'] = ' '.join(parts[1:-1])
            result['last'] = parts[-1]
        
        return result
    
    def clean_name_components(self, df):
        """Parse and clean all name fields"""
        self.log(f"\nParsing and cleaning names...")
        
        parsed_count = 0
        
        for idx, row in df.iterrows():
            name_value = row.get('Name', '')
            
            if pd.notna(name_value) and str(name_value).strip():
                parsed = self.parse_name_field(name_value)
                
                # Only populate if target fields are empty
                if not row.get('First Name') or pd.isna(row.get('First Name')):
                    df.at[idx, 'First Name'] = parsed['first']
                if not row.get('Middle Name') or pd.isna(row.get('Middle Name')):
                    df.at[idx, 'Middle Name'] = parsed['middle']
                if not row.get('Last Name') or pd.isna(row.get('Last Name')):
                    df.at[idx, 'Last Name'] = parsed['last']
                
                parsed_count += 1
        
        self.log(f"  Parsed {parsed_count} records")
        return df
    
    def remove_numbers_from_names(self, name_str):
        """Remove numbers from name strings (except valid suffixes)"""
        if not name_str or name_str == 'nan':
            return name_str
        
        # Valid numeric suffixes
        valid_suffixes = ['II', 'III', 'IV', 'V', '2nd', '3rd', '4th', '5th']
        
        # Check if entire string is a valid suffix
        if name_str.strip() in valid_suffixes:
            return name_str
        
        # Remove any digits
        cleaned = re.sub(r'\d+', '', name_str)
        return cleaned.strip()
    
    def clean_prefixes_suffixes(self, df):
        """Remove prefixes/suffixes, apply title casing, detect emails, extract middle initials, remove numbers"""
        self.log(f"\nCleaning prefixes and suffixes...")
        
        prefix_removed = 0
        suffix_removed = 0
        emails_moved = 0
        initials_extracted = 0
        numbers_removed = 0
        
        for idx, row in df.iterrows():
            # Process First Name
            first = str(row.get('First Name', '')).strip()
            if first and first != 'nan':
                # Check if it's an email
                if '@' in first:
                    df.at[idx, 'E-mail 1 - Value'] = first
                    df.at[idx, 'First Name'] = ''
                    emails_moved += 1
                    first = ''
                else:
                    # Remove prefix
                    parts = first.split()
                    if len(parts) > 1 and parts[0].lower().replace('.', '') in self.prefixes:
                        first = ' '.join(parts[1:])
                        prefix_removed += 1
                    
                    # Remove numbers
                    if re.search(r'\d', first):
                        first = self.remove_numbers_from_names(first)
                        numbers_removed += 1
                    
                    # Extract middle initial (e.g., "John M" or "Mary A.")
                    parts = first.split()
                    if len(parts) == 2 and len(parts[1]) <= 2 and parts[1].replace('.', '').isalpha():
                        middle = row.get('Middle Name', '')
                        if not middle or pd.isna(middle) or middle == 'nan':
                            df.at[idx, 'Middle Name'] = parts[1]
                            initials_extracted += 1
                        first = parts[0]
                    
                    # Apply title case
                    if first:
                        df.at[idx, 'First Name'] = first.title()
            
            # Process Last Name
            last = str(row.get('Last Name', '')).strip()
            if last and last != 'nan':
                # Check if it's an email
                if '@' in last:
                    if not df.at[idx, 'E-mail 1 - Value'] or pd.isna(df.at[idx, 'E-mail 1 - Value']):
                        df.at[idx, 'E-mail 1 - Value'] = last
                    df.at[idx, 'Last Name'] = ''
                    emails_moved += 1
                    last = ''
                else:
                    # Remove suffix
                    parts = last.split()
                    if len(parts) > 1 and parts[-1].lower().replace('.', '') in self.suffixes:
                        suffix_val = parts[-1]
                        last = ' '.join(parts[:-1])
                        df.at[idx, 'Suffix'] = suffix_val
                        suffix_removed += 1
                    
                    # Remove numbers
                    if re.search(r'\d', last):
                        last = self.remove_numbers_from_names(last)
                        numbers_removed += 1
                    
                    # Apply title case
                    if last:
                        df.at[idx, 'Last Name'] = last.title()
            
            # Process Middle Name (title case, remove numbers, fix semicolons)
            middle = str(row.get('Middle Name', '')).strip()
            if middle and middle != 'nan':
                # Fix semicolons - take first non-empty value
                if ';' in middle:
                    parts = [p.strip() for p in middle.split(';') if p.strip()]
                    middle = parts[0] if parts else ''
                
                # Remove numbers
                if middle and re.search(r'\d', middle):
                    middle = self.remove_numbers_from_names(middle)
                
                if middle:
                    df.at[idx, 'Middle Name'] = middle.title()
                else:
                    df.at[idx, 'Middle Name'] = ''
        
        self.log(f"  Removed {prefix_removed} prefixes")
        self.log(f"  Removed {suffix_removed} suffixes")
        self.log(f"  Moved {emails_moved} emails from name fields")
        self.log(f"  Extracted {initials_extracted} middle initials from first names")
        self.log(f"  Removed numbers from {numbers_removed} names")
        
        return df
    
    def clean_middle_names(self, df):
        """Clean middle names: fix semicolons, remove single letters, form compounds"""
        self.log(f"\nCleaning middle names...")
        
        single_removed = 0
        compounds_formed = 0
        
        for idx, row in df.iterrows():
            first = str(row.get('First Name', '')).strip()
            middle = str(row.get('Middle Name', '')).strip()
            
            if not middle or middle == 'nan':
                continue
            
            # Semicolons should already be handled, but double-check
            if ';' in middle:
                parts = [p.strip() for p in middle.split(';') if p.strip()]
                middle = parts[0] if parts else ''
                df.at[idx, 'Middle Name'] = middle
            
            if not middle:
                continue
            
            # Single letter middle name
            if len(middle) == 1 and middle.isalpha():
                # Check if First + Middle is a compound name
                if first and first != 'nan':
                    potential_compound = f"{first.lower()} {middle.lower()}"
                    if potential_compound in self.compound_names:
                        df.at[idx, 'First Name'] = f"{first} {middle}".title()
                        df.at[idx, 'Middle Name'] = ''
                        compounds_formed += 1
                    else:
                        # Just remove the single letter
                        df.at[idx, 'Middle Name'] = ''
                        single_removed += 1
                else:
                    df.at[idx, 'Middle Name'] = ''
                    single_removed += 1
        
        self.log(f"  Removed {single_removed} single letters")
        self.log(f"  Formed {compounds_formed} compounds")
        
        return df
    
    def extract_names_from_emails(self, df):
        """Extract names from emails when First/Last names are missing"""
        self.log(f"\nExtracting names from emails...")
        
        extracted = 0
        high_confidence = 0
        low_confidence = 0
        
        # Add confidence column if not exists
        if 'Name_Source_Confidence' not in df.columns:
            df['Name_Source_Confidence'] = ''
        
        for idx, row in df.iterrows():
            first = str(row.get('First Name', '')).strip()
            last = str(row.get('Last Name', '')).strip()
            email = str(row.get('E-mail 1 - Value', '')).strip()
            
            # Skip if names already exist
            if (first and first != 'nan') or (last and last != 'nan'):
                continue
            
            # Skip if no valid email
            if not email or email == 'nan' or '@' not in email:
                continue
            
            # Extract local part of email
            local = email.split('@')[0].lower()
            
            # Replace common separators with spaces
            local = local.replace('.', ' ').replace('_', ' ').replace('-', ' ')
            parts = local.split()
            
            # Extract names based on parts
            if len(parts) >= 2:
                # High confidence: first.last@domain.com
                df.at[idx, 'First Name'] = parts[0].title()
                df.at[idx, 'Last Name'] = parts[-1].title()
                df.at[idx, 'Name_Source_Confidence'] = 'HIGH (from email)'
                extracted += 1
                high_confidence += 1
            elif len(parts) == 1 and len(parts[0]) > 3:
                # Low confidence: single string, try to split
                name = parts[0]
                if len(name) > 8:
                    # Long enough to attempt split
                    mid = len(name) // 2
                    df.at[idx, 'First Name'] = name[:mid].title()
                    df.at[idx, 'Last Name'] = name[mid:].title()
                    df.at[idx, 'Name_Source_Confidence'] = 'LOW (guessed from email)'
                else:
                    # Too short to split, just use as first name
                    df.at[idx, 'First Name'] = name.title()
                    df.at[idx, 'Name_Source_Confidence'] = 'LOW (partial from email)'
                extracted += 1
                low_confidence += 1
        
        self.log(f"  Extracted {extracted} names from emails")
        self.log(f"    {high_confidence} high confidence")
        self.log(f"    {low_confidence} low confidence")
        
        return df
    
    def add_quality_markers(self, df):
        """Add data quality marker flags"""
        self.log(f"\nAdding data quality markers...")
        
        # Initialize flag columns
        df['FLAG_Missing_First_Name'] = False
        df['FLAG_Missing_Last_Name'] = False
        df['FLAG_Single_Name_Only'] = False
        df['FLAG_Middle_Only'] = False
        df['FLAG_Has_Numbers'] = False
        df['FLAG_Possible_Company_Name'] = False
        
        # Add Organization Name column for company names
        if 'Organization Name' not in df.columns:
            df['Organization Name'] = ''
        
        missing_first = 0
        missing_last = 0
        single_name = 0
        middle_only = 0
        has_numbers = 0
        company_names = 0
        
        # Expanded company keywords
        company_keywords = ['inc', 'llc', 'corp', 'ltd', 'company', 'co', 'corporation', 
                           'incorporated', 'limited', 'group', 'associates', 'partners',
                           'foundation', 'institute', 'organization', 'association', 'trust',
                           'holdings', 'ventures', 'capital', 'consulting', 'solutions',
                           'services', 'systems', 'technologies', 'enterprises']
        
        for idx, row in df.iterrows():
            first = str(row.get('First Name', '')).strip()
            last = str(row.get('Last Name', '')).strip()
            middle = str(row.get('Middle Name', '')).strip()
            
            # Check for company names first and move them
            full_name = f"{first} {middle} {last}".lower()
            if any(keyword in full_name for keyword in company_keywords):
                df.at[idx, 'FLAG_Possible_Company_Name'] = True
                # Move to Organization Name and clear name fields
                org_name = f"{first} {middle} {last}".strip()
                df.at[idx, 'Organization Name'] = org_name
                df.at[idx, 'First Name'] = ''
                df.at[idx, 'Middle Name'] = ''
                df.at[idx, 'Last Name'] = ''
                company_names += 1
                continue  # Skip other checks for this record
            
            # Check for missing names
            has_first = first and first != 'nan'
            has_last = last and last != 'nan'
            
            if not has_first:
                df.at[idx, 'FLAG_Missing_First_Name'] = True
                missing_first += 1
            
            if not has_last:
                df.at[idx, 'FLAG_Missing_Last_Name'] = True
                missing_last += 1
            
            # Check for single name only (has ONLY first OR ONLY last, not both)
            if (has_first and not has_last) or (has_last and not has_first):
                df.at[idx, 'FLAG_Single_Name_Only'] = True
                single_name += 1
            
            # Check for middle only (has middle but missing first OR last)
            if middle and middle != 'nan':
                if not has_first or not has_last:
                    df.at[idx, 'FLAG_Middle_Only'] = True
                    middle_only += 1
            
            # Check for numbers in names
            for name_field in ['First Name', 'Last Name', 'Middle Name']:
                name_val = str(row.get(name_field, '')).strip()
                if name_val and name_val != 'nan':
                    if re.search(r'\d', name_val):
                        # Check if NOT a valid suffix
                        valid_pattern = r'^(II|III|IV|V|2nd|3rd|4th|5th)$'
                        if not re.match(valid_pattern, name_val, re.IGNORECASE):
                            df.at[idx, 'FLAG_Has_Numbers'] = True
                            has_numbers += 1
                            break
        
        self.log(f"  Flagged {missing_first} missing first names")
        self.log(f"  Flagged {missing_last} missing last names")
        self.log(f"  Flagged {single_name} single name only records")
        self.log(f"  Flagged {middle_only} middle-only records")
        self.log(f"  Flagged {has_numbers} names with numbers")
        self.log(f"  Moved {company_names} company names to Organization Name field")
        
        return df
    
    def string_similarity(self, s1, s2):
        """Calculate similarity between two strings (0-1, where 1 is identical)"""
        if not s1 or not s2 or s1 == 'nan' or s2 == 'nan':
            return 0
        
        s1 = str(s1).lower().strip()
        s2 = str(s2).lower().strip()
        
        if s1 == s2:
            return 1.0
        
        # Simple Levenshtein-like distance
        len1, len2 = len(s1), len(s2)
        if len1 == 0 or len2 == 0:
            return 0
        
        # Create distance matrix
        matrix = [[0] * (len2 + 1) for _ in range(len1 + 1)]
        
        for i in range(len1 + 1):
            matrix[i][0] = i
        for j in range(len2 + 1):
            matrix[0][j] = j
        
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                cost = 0 if s1[i-1] == s2[j-1] else 1
                matrix[i][j] = min(
                    matrix[i-1][j] + 1,      # deletion
                    matrix[i][j-1] + 1,      # insertion
                    matrix[i-1][j-1] + cost  # substitution
                )
        
        distance = matrix[len1][len2]
        max_len = max(len1, len2)
        similarity = 1 - (distance / max_len)
        
        return similarity
    
    def merge_duplicates(self, df):
        """Merge duplicate contacts with fuzzy matching"""
        self.log(f"\nMerging duplicates...")
        
        # Sort by Source and all columns
        df_sorted = df.sort_values(by=list(df.columns)).reset_index(drop=True)
        
        merged_rows = []
        processed_indices = set()
        
        # First pass: exact email matches
        if 'E-mail 1 - Value' in df.columns:
            email_groups = df_sorted.groupby('E-mail 1 - Value', dropna=True)
            
            for email, group in email_groups:
                if len(group) > 1:
                    # Mark all indices as processed
                    for idx in group.index:
                        processed_indices.add(idx)
                    
                    # Merge the group
                    merged = group.iloc[0].copy()
                    for col in group.columns:
                        if col == 'Source':
                            # Concatenate sources with semicolon
                            sources = group[col].unique()
                            merged[col] = '; '.join(sources)
                        else:
                            # Take first non-null value
                            non_null = group[col].dropna()
                            if len(non_null) > 0:
                                merged[col] = non_null.iloc[0]
                    merged_rows.append(merged)
        
        # Second pass: fuzzy name matching for remaining records
        unprocessed = df_sorted[~df_sorted.index.isin(processed_indices)]
        
        fuzzy_threshold = 0.85  # 85% similarity required
        fuzzy_merged = 0
        
        for idx1, row1 in unprocessed.iterrows():
            if idx1 in processed_indices:
                continue
            
            first1 = str(row1.get('First Name', '')).strip()
            last1 = str(row1.get('Last Name', '')).strip()
            
            if not first1 or first1 == 'nan' or not last1 or last1 == 'nan':
                merged_rows.append(row1)
                processed_indices.add(idx1)
                continue
            
            # Look for similar names
            matches = [idx1]
            for idx2, row2 in unprocessed.iterrows():
                if idx2 <= idx1 or idx2 in processed_indices:
                    continue
                
                first2 = str(row2.get('First Name', '')).strip()
                last2 = str(row2.get('Last Name', '')).strip()
                
                if not first2 or first2 == 'nan' or not last2 or last2 == 'nan':
                    continue
                
                # Calculate similarity
                first_sim = self.string_similarity(first1, first2)
                last_sim = self.string_similarity(last1, last2)
                
                # Both names must be similar
                if first_sim >= fuzzy_threshold and last_sim >= fuzzy_threshold:
                    matches.append(idx2)
            
            # Merge matches
            if len(matches) > 1:
                fuzzy_merged += len(matches) - 1
                group = unprocessed.loc[matches]
                
                # Mark all as processed
                for idx in matches:
                    processed_indices.add(idx)
                
                # Merge
                merged = group.iloc[0].copy()
                for col in group.columns:
                    if col == 'Source':
                        sources = group[col].unique()
                        merged[col] = '; '.join(sources)
                    else:
                        non_null = group[col].dropna()
                        if len(non_null) > 0:
                            merged[col] = non_null.iloc[0]
                merged_rows.append(merged)
            else:
                merged_rows.append(row1)
                processed_indices.add(idx1)
        
        result = pd.DataFrame(merged_rows).reset_index(drop=True)
        self.log(f"  Merged from {len(df)} to {len(result)} records")
        self.log(f"  Fuzzy matched {fuzzy_merged} similar name pairs")
        
        return result
    
    def calculate_quality_score(self, df):
        """Calculate quality score and classify records as OK or Questionable"""
        self.log(f"\nCalculating quality scores...")
        
        df['Quality_Score'] = 0
        df['Record_Status'] = ''
        
        ok_count = 0
        questionable_count = 0
        
        for idx, row in df.iterrows():
            score = 0
            
            # Points for having data
            if row.get('First Name') and str(row.get('First Name')).strip() and str(row.get('First Name')) != 'nan':
                score += 25
            if row.get('Last Name') and str(row.get('Last Name')).strip() and str(row.get('Last Name')) != 'nan':
                score += 25
            if row.get('E-mail 1 - Value') and str(row.get('E-mail 1 - Value')).strip() and str(row.get('E-mail 1 - Value')) != 'nan':
                score += 30
            if row.get('Phone 1 - Value') and str(row.get('Phone 1 - Value')).strip() and str(row.get('Phone 1 - Value')) != 'nan':
                score += 20
            
            # Deduct for quality flags
            if row.get('FLAG_Missing_First_Name'):
                score -= 15
            if row.get('FLAG_Missing_Last_Name'):
                score -= 15
            if row.get('FLAG_Single_Name_Only'):
                score -= 10
            if row.get('FLAG_Has_Numbers'):
                score -= 10
            if row.get('FLAG_Possible_Company_Name'):
                score -= 5
            
            # Bonus for high confidence name extraction
            if row.get('Name_Source_Confidence') == 'HIGH (from email)':
                score += 5
            
            # Ensure score is between 0 and 100
            score = max(0, min(100, score))
            df.at[idx, 'Quality_Score'] = score
            
            # Classify as OK or Questionable
            has_first = row.get('First Name') and str(row.get('First Name')).strip() and str(row.get('First Name')) != 'nan'
            has_last = row.get('Last Name') and str(row.get('Last Name')).strip() and str(row.get('Last Name')) != 'nan'
            has_email = row.get('E-mail 1 - Value') and str(row.get('E-mail 1 - Value')).strip() and str(row.get('E-mail 1 - Value')) != 'nan'
            has_phone = row.get('Phone 1 - Value') and str(row.get('Phone 1 - Value')).strip() and str(row.get('Phone 1 - Value')) != 'nan'
            
            is_ok = (
                has_first and 
                has_last and 
                (has_email or has_phone) and 
                score >= 60 and 
                not row.get('FLAG_Has_Numbers') and
                not row.get('FLAG_Single_Name_Only')
            )
            
            if is_ok:
                df.at[idx, 'Record_Status'] = 'OK'
                ok_count += 1
            else:
                df.at[idx, 'Record_Status'] = 'QUESTIONABLE'
                questionable_count += 1
        
        self.log(f"  Calculated quality scores")
        self.log(f"  {ok_count} OK records ({ok_count/len(df)*100:.1f}%)")
        self.log(f"  {questionable_count} QUESTIONABLE records ({questionable_count/len(df)*100:.1f}%)")
        
        return df
    
    def get_column_letter(self, col_num):
        """Convert column number to Excel column letter (1=A, 27=AA, etc.)"""
        letter = ''
        while col_num > 0:
            col_num -= 1
            letter = chr(65 + (col_num % 26)) + letter
            col_num //= 26
        return letter
    
    def create_excel_output(self, intake_df, mapped_df, cleaned_df, final_df):
        """Create Excel file with tabs ordered Summary/Final first, M-numbered by stage"""
        self.log(f"\nCreating Excel output...")
        
        sources = cleaned_df['Source'].unique()
        
        with pd.ExcelWriter(self.output_excel, engine='openpyxl') as writer:
            
            # SUMMARY (first tab)
            summary_data = {
                'Metric': ['Total Records Processed', 'Final Records', 'Duplicate Records Merged', 
                          'Sources Processed', 'OK Records', 'Questionable Records',
                          'High Quality Records (Score >= 80)', 
                          'Medium Quality Records (Score 50-79)', 
                          'Low Quality Records (Score < 50)'],
                'Value': [
                    len(intake_df),
                    len(final_df),
                    len(intake_df) - len(final_df),
                    len(sources),
                    len(final_df[final_df['Record_Status'] == 'OK']),
                    len(final_df[final_df['Record_Status'] == 'QUESTIONABLE']),
                    len(final_df[final_df['Quality_Score'] >= 80]),
                    len(final_df[(final_df['Quality_Score'] >= 50) & (final_df['Quality_Score'] < 80)]),
                    len(final_df[final_df['Quality_Score'] < 50])
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='SUMMARY', index=False, startrow=1)
            ws = writer.sheets['SUMMARY']
            ws['A1'] = 'MAMBO CONTACT PROCESSING SUMMARY'
            for i, col in enumerate(summary_df.columns, 1):
                letter = self.get_column_letter(i)
                ws.column_dimensions[letter].width = 40
            
            # M4: Final (Stage 4 - second tab)
            final_df.to_excel(writer, sheet_name='M4_FINAL', index=False, startrow=1)
            ws = writer.sheets['M4_FINAL']
            for i, col in enumerate(final_df.columns, 1):
                letter = self.get_column_letter(i)
                ws.column_dimensions[letter].width = 20
            ws['A1'] = f'M4: FINAL MERGED ({len(final_df)} records)'
            
            # M3: Cleaned (Stage 3)
            for i, source in enumerate(sources, 1):
                data = cleaned_df[cleaned_df['Source'] == source].copy()
                short_name = source[:12].replace('.csv', '')
                sheet_name = f"M3_{i}_{short_name}"[:31]
                
                data.to_excel(writer, sheet_name=sheet_name, index=False, startrow=1)
                ws = writer.sheets[sheet_name]
                for j, col in enumerate(data.columns, 1):
                    letter = self.get_column_letter(j)
                    ws.column_dimensions[letter].width = 20
                ws['A1'] = f'M3: CLEANED - {source} ({len(data)} records)'
            
            # M2: Mapped (Stage 2)
            for i, source in enumerate(sources, 1):
                data = mapped_df[mapped_df['Source'] == source].copy()
                short_name = source[:12].replace('.csv', '')
                sheet_name = f"M2_{i}_{short_name}"[:31]
                
                data.to_excel(writer, sheet_name=sheet_name, index=False, startrow=1)
                ws = writer.sheets[sheet_name]
                for j, col in enumerate(data.columns, 1):
                    letter = self.get_column_letter(j)
                    ws.column_dimensions[letter].width = 20
                ws['A1'] = f'M2: MAPPED - {source} ({len(data)} records)'
            
            # M1: Intake (Stage 1)
            for i, source in enumerate(sources, 1):
                data = intake_df[intake_df['Source'] == source].copy()
                short_name = source[:12].replace('.csv', '')
                sheet_name = f"M1_{i}_{short_name}"[:31]
                
                data.to_excel(writer, sheet_name=sheet_name, index=False, startrow=1)
                ws = writer.sheets[sheet_name]
                for j, col in enumerate(data.columns, 1):
                    letter = self.get_column_letter(j)
                    ws.column_dimensions[letter].width = 20
                ws['A1'] = f'M1: INTAKE - {source} ({len(data)} records)'
        
        self.log(f"✓ Excel file created: {self.output_excel}")
        self.log(f"  Tab naming: M1=Intake, M2=Mapped, M3=Cleaned, M4=Final")
    
    def run(self):
        """Run the complete cleaning pipeline"""
        print("="*70)
        print("MAMBO PROCESSING")
        print("="*70)
        
        # Load configuration
        self.load_lookup_table()
        self.load_compound_names()
        
        # Stage 1: Intake
        intake_df = self.load_csv_files()
        print("="*70)
        print(f"Stage 1: INTAKE")
        print(f"  {len(intake_df):,} rows")
        print("="*70)
        
        # Stage 2: Column Mapping
        mapped_df = self.apply_column_mapping(intake_df)
        mapped_df = self.reorder_columns(mapped_df)
        print(f"Stage 2: COLUMN MAPPING")
        print(f"  {len(mapped_df):,} rows")
        print("="*70)
        
        # Stage 3: Name Cleaning
        print(f"Stage 3: NAME CLEANING")
        cleaned_df = self.clean_name_components(mapped_df)
        cleaned_df = self.clean_prefixes_suffixes(cleaned_df)
        cleaned_df = self.clean_middle_names(cleaned_df)
        cleaned_df = self.extract_names_from_emails(cleaned_df)
        cleaned_df = self.add_quality_markers(cleaned_df)
        
        # Stage 4: Merge and Score
        print(f"\n" + "="*70)
        print(f"Stage 4: MERGE & SCORE")
        print("="*70)
        final_df = self.merge_duplicates(cleaned_df)
        final_df = self.calculate_quality_score(final_df)
        
        # Create output
        self.create_excel_output(intake_df, mapped_df, cleaned_df, final_df)
        
        print("\n" + "="*70)
        print("PROCESSING COMPLETE")
        print("="*70)
        print(f"\nOutput file: {self.output_excel}")
        print(f"Final records: {len(final_df):,}")
        print(f"Average quality score: {final_df['Quality_Score'].mean():.1f}")

if __name__ == "__main__":
    try:
        cleaner = MamboContactCleaner()
        cleaner.run()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        input("\nPress Enter...")