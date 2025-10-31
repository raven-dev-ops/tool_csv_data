#!/usr/bin/env python3
"""
MAMBO PARSER PART 1 - Field Mapping & Column Detection
Handles file loading, column detection, and metadata row handling (LinkedIn)
"""

import pandas as pd
import re
import zipfile
import os
from pathlib import Path

class FieldMapper:
    """Map CSV columns to standard MAMBO fields"""
    
    def __init__(self, lookup_manager):
        """Initialize field mapper"""
        self.lookups = lookup_manager
        self.field_patterns = self._get_field_patterns()
        self.unmapped_columns = {}
    
    def _get_field_patterns(self):
        """Define field detection patterns"""
        return {
            'first_name': [r'first.*name', r'^fname$', r'given.*name', r'forename', r'^first$'],
            'last_name': [r'last.*name', r'^lname$', r'family.*name', r'surname', r'^last$'],
            'middle_name': [r'middle.*name', r'^mname$', r'^mi$', r'middle_initial'],
            'full_name': [r'^name$', r'full.*name', r'display.*name', r'complete.*name'],
            'nickname': [r'nick.*name', r'preferred.*name'],
            'prefix': [r'^prefix$', r'name.*prefix', r'^title$'],
            'suffix': [r'^suffix$', r'name.*suffix'],
            'primary_email': [r'^email$', r'^e-?mail$', r'email.*primary', r'email.*1$', r'email_address'],
            'secondary_email': [r'email.*2', r'secondary.*email'],
            'tertiary_email': [r'email.*3', r'tertiary.*email'],
            'primary_phone': [r'^phone$', r'phone.*1$', r'mobile', r'^cell$'],
            'work_phone': [r'work.*phone', r'business.*phone', r'office.*phone'],
            'home_phone': [r'home.*phone', r'^home$'],
            'company': [r'^company$', r'^organization$', r'^employer$', r'company_name'],
            'title': [r'^title$', r'job.*title', r'^position$', r'job_title'],
            'department': [r'department', r'^dept$', r'organization.*department'],
            'street_address': [r'address.*street', r'^street$', r'street_address', r'address_1'],
            'city': [r'^city$', r'address.*city'],
            'state': [r'^state$', r'region$', r'address.*state', r'province'],
            'postal_code': [r'^zip$', r'postal.*code', r'zip_code', r'postcode'],
            'country': [r'^country$', r'address.*country'],
            'birthday': [r'birth', r'bday', r'date.*birth'],
            'notes': [r'^notes$', r'^note$', r'comments'],
            'website': [r'website', r'homepage', r'^url$', r'web'],
            'labels': [r'^labels$', r'^tags$', r'groups'],
        }
    
    def load_file(self, filepath, skip_rows=None):
        """
        Load file (CSV, Excel, or ZIP)
        Handles LinkedIn exports with metadata rows
        """
        filepath = str(filepath)
        
        # Handle ZIP files (LinkedIn)
        if filepath.lower().endswith('.zip'):
            return self._load_zip_file(filepath)
        
        # Load CSV
        if filepath.lower().endswith('.csv'):
            try:
                if skip_rows:
                    df = pd.read_csv(filepath, skiprows=skip_rows, encoding='utf-8')
                else:
                    # Auto-detect header rows (LinkedIn fix)
                    df = self._load_csv_smart(filepath)
                return df
            except Exception as e:
                print(f"❌ Error loading CSV: {e}")
                raise
        
        # Load Excel
        if filepath.lower().endswith(('.xlsx', '.xls')):
            try:
                df = pd.read_excel(filepath)
                return df
            except Exception as e:
                print(f"❌ Error loading Excel: {e}")
                raise
        
        raise ValueError(f"Unsupported file format: {filepath}")
    
    def _load_csv_smart(self, filepath):
        """Smart CSV loading - detects LinkedIn metadata rows"""
        with open(filepath, 'r', encoding='utf-8') as f:
            first_lines = [f.readline() for _ in range(5)]
        
        # Check for metadata rows (LinkedIn exports have Notes in first rows)
        skip = 0
        for i, line in enumerate(first_lines):
            # If line doesn't look like data (too many empty cols), skip it
            if line.strip() and not self._is_header_row(line):
                skip = i
            else:
                break
        
        return pd.read_csv(filepath, skiprows=skip, encoding='utf-8')
    
    def _is_header_row(self, line):
        """Check if line is a proper CSV header"""
        # Headers typically have multiple commas and no numbers
        comma_count = line.count(',')
        return comma_count >= 2 and not any(c.isdigit() for c in line.split(',')[0])
    
    def _load_zip_file(self, filepath):
        """Extract and load CSV from ZIP (LinkedIn exports)"""
        with zipfile.ZipFile(filepath, 'r') as z:
            csv_files = [f for f in z.namelist() if f.endswith('.csv')]
            if not csv_files:
                raise ValueError(f"No CSV files found in {filepath}")
            
            # Load first CSV file
            csv_file = csv_files[0]
            with z.open(csv_file) as f:
                return pd.read_csv(f, encoding='utf-8')
    
    def map_columns(self, dataframe, source_file=""):
        """
        Map DataFrame columns to MAMBO standard fields
        Returns mapped DataFrame and mapping report
        """
        result_df = dataframe.copy()
        mapped_fields = {}
        unmapped = []
        
        for col in dataframe.columns:
            col_lower = col.lower().strip()
            best_match = None
            best_confidence = 0
            
            # Try to match against patterns
            for field_name, patterns in self.field_patterns.items():
                for pattern in patterns:
                    try:
                        if re.search(pattern, col_lower):
                            confidence = 80 if re.search('^' + pattern + '$', col_lower) else 70
                            if confidence > best_confidence:
                                best_match = field_name
                                best_confidence = confidence
                    except:
                        pass
            
            if best_match and best_confidence >= 70:
                mapped_fields[col] = best_match
                if best_match not in result_df.columns:
                    result_df[best_match] = dataframe[col]
            else:
                unmapped.append(col)
        
        # Add source tracking
        result_df['source_file'] = source_file
        
        # Track unmapped columns for learning
        self.unmapped_columns[source_file] = unmapped
        
        return result_df, {
            'mapped': len(mapped_fields),
            'unmapped': len(unmapped),
            'total': len(dataframe.columns),
            'mappings': mapped_fields,
            'unmapped_columns': unmapped
        }


class FileAssessment:
    """Assess data quality on intake"""
    
    @staticmethod
    def assess_dataframe(df):
        """Generate MAMBO-1 assessment report"""
        assessment = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'column_names': list(df.columns),
            'missing_values': df.isnull().sum().to_dict(),
            'empty_rows': df.isnull().all(axis=1).sum(),
            'duplicate_rows': df.duplicated().sum(),
            'data_types': df.dtypes.astype(str).to_dict(),
        }
        
        # Column quality
        assessment['column_quality'] = {}
        for col in df.columns:
            total = len(df)
            filled = total - df[col].isnull().sum()
            pct = (filled / total * 100) if total > 0 else 0
            assessment['column_quality'][col] = {
                'filled': filled,
                'empty': total - filled,
                'completeness': f"{pct:.1f}%"
            }
        
        return assessment

    @staticmethod
    def print_assessment(assessment):
        """Pretty print assessment"""
        print(f"\n{'='*70}")
        print(f"📋 MAMBO-1 INTAKE ASSESSMENT")
        print(f"{'='*70}")
        print(f"Total Rows: {assessment['total_rows']:,}")
        print(f"Total Columns: {assessment['total_columns']}")
        print(f"Empty Rows: {assessment['empty_rows']}")
        print(f"Duplicate Rows: {assessment['duplicate_rows']}")
        print(f"\n📊 Column Completeness:")
        for col, stats in assessment['column_quality'].items():
            print(f"  • {col}: {stats['completeness']} ({stats['filled']}/{assessment['total_rows']})")