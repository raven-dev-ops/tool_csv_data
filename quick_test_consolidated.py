#!/usr/bin/env python3
"""
MAMBO LOOKUPS - Lookup Table Management
Handles creation, loading, and querying of CSV lookup tables
"""

import pandas as pd
import os
from pathlib import Path

class LookupManager:
    """Manage lookup tables for name standardization"""
    
    def __init__(self, lookups_dir="Mambo_Lookups"):
        """Initialize lookup manager"""
        self.lookups_dir = lookups_dir
        os.makedirs(lookups_dir, exist_ok=True)
        self.lookups = {}
        self.create_all_tables()
        self.load_all_tables()
    
    def create_all_tables(self):
        """Create all lookup CSV tables"""
        
        # PREFIXES
        prefixes = [
            {'Prefix': 'Dr.', 'Standard': 'Dr.', 'Remove': 'N'},
            {'Prefix': 'Dr', 'Standard': 'Dr.', 'Remove': 'N'},
            {'Prefix': 'Doctor', 'Standard': 'Dr.', 'Remove': 'N'},
            {'Prefix': 'Mr.', 'Standard': 'Mr.', 'Remove': 'Y'},
            {'Prefix': 'Mr', 'Standard': 'Mr.', 'Remove': 'Y'},
            {'Prefix': 'Mrs.', 'Standard': 'Mrs.', 'Remove': 'Y'},
            {'Prefix': 'Mrs', 'Standard': 'Mrs.', 'Remove': 'Y'},
            {'Prefix': 'Ms.', 'Standard': 'Ms.', 'Remove': 'Y'},
            {'Prefix': 'Ms', 'Standard': 'Ms.', 'Remove': 'Y'},
            {'Prefix': 'Miss', 'Standard': 'Miss', 'Remove': 'Y'},
            {'Prefix': 'Prof.', 'Standard': 'Prof.', 'Remove': 'N'},
            {'Prefix': 'Professor', 'Standard': 'Prof.', 'Remove': 'N'},
            {'Prefix': 'Rev.', 'Standard': 'Rev.', 'Remove': 'N'},
            {'Prefix': 'Reverend', 'Standard': 'Rev.', 'Remove': 'N'},
        ]
        pd.DataFrame(prefixes).to_csv(
            os.path.join(self.lookups_dir, 'Prefixes.csv'), 
            index=False
        )
        
        # SUFFIXES - USER REQUIREMENT: TITLE CASE (Jr., Sr., Ph.D., Esq.)
        suffixes = [
            {'Suffix': 'Jr.', 'Standard': 'Jr.', 'Order': 1},
            {'Suffix': 'Jr', 'Standard': 'Jr.', 'Order': 1},
            {'Suffix': 'Junior', 'Standard': 'Jr.', 'Order': 1},
            {'Suffix': 'Sr.', 'Standard': 'Sr.', 'Order': 2},
            {'Suffix': 'Sr', 'Standard': 'Sr.', 'Order': 2},
            {'Suffix': 'Senior', 'Standard': 'Sr.', 'Order': 2},
            {'Suffix': 'II', 'Standard': 'II', 'Order': 3},
            {'Suffix': '2nd', 'Standard': 'II', 'Order': 3},
            {'Suffix': 'III', 'Standard': 'III', 'Order': 4},
            {'Suffix': '3rd', 'Standard': 'III', 'Order': 4},
            {'Suffix': 'IV', 'Standard': 'IV', 'Order': 5},
            {'Suffix': 'Ph.D.', 'Standard': 'Ph.D.', 'Order': 10},
            {'Suffix': 'PhD', 'Standard': 'Ph.D.', 'Order': 10},
            {'Suffix': 'M.D.', 'Standard': 'M.D.', 'Order': 11},
            {'Suffix': 'MD', 'Standard': 'M.D.', 'Order': 11},
            {'Suffix': 'Esq.', 'Standard': 'Esq.', 'Order': 12},
            {'Suffix': 'Esquire', 'Standard': 'Esq.', 'Order': 12},
        ]
        pd.DataFrame(suffixes).to_csv(
            os.path.join(self.lookups_dir, 'Suffixes.csv'), 
            index=False
        )
        
        # NICKNAMES
        nicknames = [
            {'Nickname': 'Bob', 'Formal': 'Robert'}, {'Nickname': 'Bobby', 'Formal': 'Robert'},
            {'Nickname': 'Rob', 'Formal': 'Robert'}, {'Nickname': 'Bill', 'Formal': 'William'},
            {'Nickname': 'Billy', 'Formal': 'William'}, {'Nickname': 'Will', 'Formal': 'William'},
            {'Nickname': 'Mike', 'Formal': 'Michael'}, {'Nickname': 'Dave', 'Formal': 'David'},
            {'Nickname': 'Jim', 'Formal': 'James'}, {'Nickname': 'Jimmy', 'Formal': 'James'},
            {'Nickname': 'Tom', 'Formal': 'Thomas'}, {'Nickname': 'Tommy', 'Formal': 'Thomas'},
            {'Nickname': 'Joe', 'Formal': 'Joseph'}, {'Nickname': 'Steve', 'Formal': 'Steven'},
            {'Nickname': 'Chris', 'Formal': 'Christopher'}, {'Nickname': 'Rick', 'Formal': 'Richard'},
            {'Nickname': 'Dick', 'Formal': 'Richard'}, {'Nickname': 'Dan', 'Formal': 'Daniel'},
            {'Nickname': 'Danny', 'Formal': 'Daniel'}, {'Nickname': 'Matt', 'Formal': 'Matthew'},
            {'Nickname': 'Liz', 'Formal': 'Elizabeth'}, {'Nickname': 'Beth', 'Formal': 'Elizabeth'},
            {'Nickname': 'Betty', 'Formal': 'Elizabeth'}, {'Nickname': 'Sue', 'Formal': 'Susan'},
            {'Nickname': 'Susie', 'Formal': 'Susan'}, {'Nickname': 'Kate', 'Formal': 'Katherine'},
            {'Nickname': 'Katie', 'Formal': 'Katherine'}, {'Nickname': 'Kathy', 'Formal': 'Katherine'},
            {'Nickname': 'Cathy', 'Formal': 'Catherine'}, {'Nickname': 'Jen', 'Formal': 'Jennifer'},
            {'Nickname': 'Jenny', 'Formal': 'Jennifer'}, {'Nickname': 'Pam', 'Formal': 'Pamela'},
            {'Nickname': 'Cindy', 'Formal': 'Cynthia'}, {'Nickname': 'Mandy', 'Formal': 'Amanda'},
            {'Nickname': 'Sam', 'Formal': 'Samuel'}, {'Nickname': 'Alex', 'Formal': 'Alexander'},
        ]
        pd.DataFrame(nicknames).to_csv(
            os.path.join(self.lookups_dir, 'Nicknames.csv'), 
            index=False
        )
        
        # NAME VARIATIONS
        variations = [
            {'Variation': 'Jon', 'Standard': 'John'}, {'Variation': 'Johnathan', 'Standard': 'Jonathan'},
            {'Variation': 'Cathrine', 'Standard': 'Catherine'}, {'Variation': 'Kristina', 'Standard': 'Christina'},
            {'Variation': 'Jeffrey', 'Standard': 'Geoffrey'}, {'Variation': 'Phillip', 'Standard': 'Philip'},
            {'Variation': 'Stephen', 'Standard': 'Steven'}, {'Variation': 'Teresa', 'Standard': 'Theresa'},
            {'Variation': 'Sara', 'Standard': 'Sarah'}, {'Variation': 'Ann', 'Standard': 'Anne'},
        ]
        pd.DataFrame(variations).to_csv(
            os.path.join(self.lookups_dir, 'NameVariations.csv'), 
            index=False
        )
        
        # MISSPELLINGS
        misspellings = [
            {'Misspelling': 'Micheal', 'Correct': 'Michael'},
            {'Misspelling': 'Cristopher', 'Correct': 'Christopher'},
            {'Misspelling': 'Stephane', 'Correct': 'Stephanie'},
            {'Misspelling': 'Elizebeth', 'Correct': 'Elizabeth'},
            {'Misspelling': 'Rebeca', 'Correct': 'Rebecca'},
            {'Misspelling': 'Jennfer', 'Correct': 'Jennifer'},
            {'Misspelling': 'Nickolas', 'Correct': 'Nicholas'},
        ]
        pd.DataFrame(misspellings).to_csv(
            os.path.join(self.lookups_dir, 'Misspellings.csv'), 
            index=False
        )
        
        # BUSINESS INDICATORS
        business = [
            {'Indicator': 'LLC'}, {'Indicator': 'Inc.'}, {'Indicator': 'Corp.'},
            {'Indicator': 'Ltd.'}, {'Indicator': 'Company'}, {'Indicator': 'Associates'},
            {'Indicator': 'Consulting'}, {'Indicator': 'Solutions'}, {'Indicator': 'Services'},
            {'Indicator': 'Group'}, {'Indicator': 'Partners'}, {'Indicator': 'Enterprises'},
        ]
        pd.DataFrame(business).to_csv(
            os.path.join(self.lookups_dir, 'BusinessIndicators.csv'), 
            index=False
        )
        
        # COMPOUND NAMES
        compounds = [
            {'Type': 'traditional', 'Value': 'TJ'}, {'Type': 'traditional', 'Value': 'BJ'},
            {'Type': 'traditional', 'Value': 'DJ'}, {'Type': 'traditional', 'Value': 'CJ'},
            {'Type': 'ending', 'Value': 'ANN'}, {'Type': 'ending', 'Value': 'SUE'},
            {'Type': 'ending', 'Value': 'LYNN'}, {'Type': 'ending', 'Value': 'MARIE'},
            {'Type': 'beginning', 'Value': 'MARY'}, {'Type': 'beginning', 'Value': 'BETTY'},
        ]
        pd.DataFrame(compounds).to_csv(
            os.path.join(self.lookups_dir, 'CompoundNames.csv'), 
            index=False
        )
    
    def load_all_tables(self):
        """Load all CSV lookup tables"""
        tables = [
            'Prefixes', 'Suffixes', 'Nicknames', 'NameVariations',
            'Misspellings', 'BusinessIndicators', 'CompoundNames'
        ]
        
        for table_name in tables:
            path = os.path.join(self.lookups_dir, f'{table_name}.csv')
            self.lookups[table_name.lower()] = pd.read_csv(path)
    
    def get_prefix(self, name_part):
        """Get standardized prefix"""
        if not name_part or pd.isna(name_part):
            return None
        
        name_upper = str(name_part).strip().rstrip('.')
        df = self.lookups['prefixes']
        
        for _, row in df.iterrows():
            if row['Prefix'].upper().rstrip('.') == name_upper.upper():
                return row['Standard']
        return None
    
    def get_suffix(self, name_part):
        """Get standardized suffix (returns CAP CASE per user requirement)"""
        if not name_part or pd.isna(name_part):
            return None
        
        name_upper = str(name_part).strip().rstrip('.')
        df = self.lookups['suffixes']
        
        for _, row in df.iterrows():
            if row['Suffix'].upper().rstrip('.') == name_upper.upper():
                return row['Standard']  # Returns CAP CASE (e.g., "JR.", "PH.D.")
        return None
    
    def get_nickname(self, name):
        """Convert nickname to formal name"""
        if not name or pd.isna(name):
            return name
        
        name_clean = str(name).strip().title()
        df = self.lookups['nicknames']
        
        for _, row in df.iterrows():
            if row['Nickname'].lower() == name_clean.lower():
                return row['Formal']
        return name
    
    def get_variation(self, name):
        """Standardize name variations"""
        if not name or pd.isna(name):
            return name
        
        name_clean = str(name).strip().title()
        df = self.lookups['namevariations']
        
        for _, row in df.iterrows():
            if row['Variation'].lower() == name_clean.lower():
                return row['Standard']
        return name
    
    def get_misspelling_correction(self, name):
        """Fix common misspellings"""
        if not name or pd.isna(name):
            return name
        
        name_clean = str(name).strip().title()
        df = self.lookups['misspellings']
        
        for _, row in df.iterrows():
            if row['Misspelling'].lower() == name_clean.lower():
                return row['Correct']
        return name
    
    def is_business_indicator(self, text):
        """Check if text contains business indicators"""
        if not text or pd.isna(text):
            return False
        
        text_upper = str(text).upper()
        df = self.lookups['businessindicators']
        
        for _, row in df.iterrows():
            if row['Indicator'].upper() in text_upper:
                return True
        return False