#!/usr/bin/env python3
"""
MAMBO-2: PARSE & COMBINE
Parses names into 6 components and enriches data from email/sources
Combines: mambo_parser_part2.py (NameParser) + mambo_enricher.py (CompanyEnricher)
"""

import pandas as pd
import re

# ═══════════════════════════════════════════════════════════════════════
# NAME PARSER - Parse names into 6 components
# ═══════════════════════════════════════════════════════════════════════

class NameParser:
    """Parse and standardize full names"""
    
    def __init__(self, lookup_manager):
        """Initialize name parser"""
        self.lookups = lookup_manager
        self.stats = {
            'prefixes_found': 0,
            'suffixes_found': 0,
            'nicknames_converted': 0,
            'misspellings_fixed': 0,
            'variations_fixed': 0,
            'compound_names_detected': 0,
        }
    
    def parse_name(self, full_name=None, first_name=None, last_name=None, middle_name=None, prefix=None, suffix=None):
        """
        Parse name into components
        Returns dict with: prefix, first_name, middle_name, last_name, suffix, full_name_clean
        """
        parsed = {
            'prefix': None,
            'first_name': '',
            'middle_name': '',
            'last_name': '',
            'suffix': None,
            'full_name_clean': '',
            'parsing_source': None
        }
        
        # If already split components provided, use those
        if pd.notna(first_name) and pd.notna(last_name):
            parsed['first_name'] = str(first_name).strip()
            parsed['last_name'] = str(last_name).strip()
            parsed['middle_name'] = str(middle_name).strip() if pd.notna(middle_name) else ''
            parsed['prefix'] = str(prefix).strip() if pd.notna(prefix) else None
            parsed['suffix'] = str(suffix).strip() if pd.notna(suffix) else None
            parsed['parsing_source'] = 'split_components'
        
        # Otherwise parse from full name
        elif pd.notna(full_name):
            parsed = self._parse_from_full_name(full_name, parsed)
            parsed['parsing_source'] = 'full_name'
        
        else:
            return parsed
        
        # Apply standardization to all components
        parsed = self._standardize_components(parsed)
        
        # Build clean full name
        parsed['full_name_clean'] = self._build_full_name(parsed)
        
        return parsed
    
    def _parse_from_full_name(self, full_name, parsed):
        """Parse full name string into components"""
        if not full_name or pd.isna(full_name):
            return parsed
        
        name_str = str(full_name).strip()
        if not name_str:
            return parsed
        
        name_parts = name_str.split()
        if len(name_parts) == 0:
            return parsed
        
        idx = 0
        
        # Check for prefix at start (Dr., Mr., Ms., etc.)
        if idx < len(name_parts):
            potential_prefix = self.lookups.get_prefix(name_parts[idx])
            if potential_prefix:
                parsed['prefix'] = potential_prefix
                idx += 1
        
        # First name
        if idx < len(name_parts):
            parsed['first_name'] = name_parts[idx]
            idx += 1
        
        # Check for suffix in remaining parts
        for check_idx in range(idx, len(name_parts)):
            potential_suffix = self.lookups.get_suffix(name_parts[check_idx])
            if potential_suffix:
                parsed['suffix'] = potential_suffix
                # Everything between first name and suffix is middle + last
                remaining = name_parts[idx:check_idx]
                if len(remaining) > 0:
                    parsed['last_name'] = remaining[-1]
                    if len(remaining) > 1:
                        parsed['middle_name'] = ' '.join(remaining[:-1])
                return parsed
        
        # No suffix found, split remaining between middle and last
        remaining = name_parts[idx:]
        if len(remaining) == 0:
            pass  # Only first name
        elif len(remaining) == 1:
            parsed['last_name'] = remaining[0]
        else:
            parsed['last_name'] = remaining[-1]
            parsed['middle_name'] = ' '.join(remaining[:-1])
        
        return parsed
    
    def _standardize_components(self, parsed):
        """Apply lookup table standardizations to all name components"""
        
        # First name: nickname → formal, variation → standard, misspelling → correct
        if parsed['first_name']:
            first = str(parsed['first_name']).strip()
            formal = self.lookups.get_nickname(first)
            if formal != first:
                self.stats['nicknames_converted'] += 1
            
            formal = self.lookups.get_variation(formal)
            formal = self.lookups.get_misspelling_correction(formal)
            if formal != first:
                self.stats['misspellings_fixed'] += 1
            
            parsed['first_name'] = formal
        
        # Last name: variation → standard, misspelling → correct
        if parsed['last_name']:
            last = str(parsed['last_name']).strip()
            standard = self.lookups.get_variation(last)
            standard = self.lookups.get_misspelling_correction(standard)
            if standard != last:
                self.stats['variations_fixed'] += 1
            
            parsed['last_name'] = standard
        
        # Middle name: apply same standardizations
        if parsed['middle_name']:
            middle = str(parsed['middle_name']).strip()
            formal = self.lookups.get_nickname(middle)
            formal = self.lookups.get_variation(formal)
            formal = self.lookups.get_misspelling_correction(formal)
            parsed['middle_name'] = formal
        
        return parsed
    
    def _build_full_name(self, parsed):
        """Build clean full name in proper order"""
        parts = []
        
        if parsed['prefix']:
            parts.append(str(parsed['prefix']).strip())
        
        if parsed['first_name']:
            parts.append(str(parsed['first_name']).strip())
        
        if parsed['middle_name']:
            parts.append(str(parsed['middle_name']).strip())
        
        if parsed['last_name']:
            parts.append(str(parsed['last_name']).strip())
        
        if parsed['suffix']:
            # Suffix is already in Title Case format (Jr., Sr., Ph.D., Esq.)
            parts.append(str(parsed['suffix']).strip())
        
        return ' '.join(parts)
    
    def detect_compound_names(self, first_name, middle_name):
        """Detect compound names like TJ, BJ, DJ"""
        if not first_name or not middle_name:
            return None
        
        first_clean = str(first_name).strip().upper()
        middle_clean = str(middle_name).strip().upper()
        
        # Check if first + middle forms a compound
        compound = first_clean + middle_clean
        
        df = self.lookups.lookups.get('compoundnames', pd.DataFrame())
        if df.empty:
            return None
        
        for _, row in df.iterrows():
            if row['Compound'].upper() == compound:
                self.stats['compound_names_detected'] += 1
                return row['Compound']
        
        return None


# ═══════════════════════════════════════════════════════════════════════
# COMPANY ENRICHER - Extract and standardize company data
# ═══════════════════════════════════════════════════════════════════════

class CompanyEnricher:
    """Extract and standardize company information"""
    
    def __init__(self, lookup_manager):
        """Initialize company enricher"""
        self.lookups = lookup_manager
    
    def extract_company_from_email(self, email, provided_company=None):
        """
        Extract company name from email domain
        Returns dict with company_name, source (PROVIDED/EXTRACTED), confidence
        """
        result = {
            'company_name': '',
            'source': '',
            'confidence': 0,
            'domain': None
        }
        
        # If company provided, use it (higher priority)
        if provided_company and pd.notna(provided_company):
            result['company_name'] = self._standardize_company_name(str(provided_company).strip())
            result['source'] = 'PROVIDED'
            result['confidence'] = 95
            return result
        
        # Extract from email domain
        if not email or pd.isna(email):
            return result
        
        email_str = str(email).strip().lower()
        
        # Extract domain
        if '@' not in email_str:
            return result
        
        domain = email_str.split('@')[1]
        result['domain'] = domain
        
        # Remove TLD (.com, .co.uk, etc.)
        domain_name = domain.split('.')[0]
        
        # Standardize company name
        company_name = self._standardize_company_name(domain_name)
        
        result['company_name'] = company_name
        result['source'] = 'EXTRACTED'
        result['confidence'] = 75
        
        return result
    
    def _standardize_company_name(self, name):
        """Standardize company name to Title Case with spaces"""
        if not name or pd.isna(name):
            return ''
        
        name_str = str(name).strip()
        
        # Insert spaces before capital letters (for camelCase like acmeCorp)
        result = re.sub(r'([a-z])([A-Z])', r'\1 \2', name_str)
        
        # Title case
        result = result.title()
        
        # Remove business indicators if present (LLC, Inc., Corp., etc.)
        business_indicators = ['Llc', 'Inc', 'Corp', 'Ltd', 'Inc.', 'Corp.', 'Ltd.', 'Llc.']
        for indicator in business_indicators:
            if result.endswith(indicator):
                result = result[:-len(indicator)].strip()
        
        return result
    
    def extract_first_last_from_email(self, email):
        """
        Extract potential first and last name from email
        Returns dict with first_name, last_name, method
        """
        result = {
            'first_name': '',
            'last_name': '',
            'method': None
        }
        
        if not email or pd.isna(email):
            return result
        
        email_str = str(email).strip().lower()
        
        # Get username part (before @)
        if '@' not in email_str:
            return result
        
        username = email_str.split('@')[0]
        
        # Try common patterns
        if '.' in username:
            parts = username.split('.')
            if len(parts) == 2:
                result['first_name'] = parts[0].title()
                result['last_name'] = parts[1].title()
                result['method'] = 'dot_separator'
                return result
        
        if '_' in username:
            parts = username.split('_')
            if len(parts) == 2:
                result['first_name'] = parts[0].title()
                result['last_name'] = parts[1].title()
                result['method'] = 'underscore_separator'
                return result
        
        # Try to split by numbers (e.g., john123 or j1234)
        match = re.match(r'([a-z]+)\d+', username)
        if match:
            result['first_name'] = match.group(1).title()
            result['method'] = 'alpha_numeric'
            return result
        
        # Last resort: assume whole username is first name
        result['first_name'] = username.title()
        result['method'] = 'whole_username'
        
        return result
    
    def standardize_job_title(self, title):
        """Standardize job title to Title Case"""
        if not title or pd.isna(title):
            return ''
        
        title_str = str(title).strip()
        return title_str.title()