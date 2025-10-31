#!/usr/bin/env python3
"""
MAMBO-3: VALIDATE & SCORE - Data Validation & Quality Scoring
Validates emails, phones, addresses, names
Calculates comprehensive quality scores
"""

import pandas as pd
import re

class EmailValidator:
    """Validate and check email addresses"""
    
    # Common disposable email domains
    DISPOSABLE_DOMAINS = {
        'tempmail.com', 'throwaway.email', 'guerrillamail.com', 'mailinator.com',
        '10minutemail.com', 'sharklasers.com', 'maildrop.cc', 'yopmail.com',
        'temp-mail.org', 'trashmail.com', '0-mail.com', 'fakeinbox.com'
    }
    
    # Catch-all domain indicators
    GENERIC_DOMAINS = {
        'test.com', 'example.com', 'sample.com', 'demo.com', 'tempmail.com'
    }
    
    def __init__(self):
        """Initialize email validator"""
        self.stats = {'emails_validated': 0, 'valid_emails': 0}
    
    def validate_email(self, email):
        """
        Validate email format
        Returns: {valid: bool, email_clean: str, issues: []}
        """
        result = {
            'valid': False,
            'email_clean': None,
            'issues': [],
            'domain': None
        }
        
        if not email or pd.isna(email):
            result['issues'].append('Empty email')
            return result
        
        email_str = str(email).strip().lower()
        self.stats['emails_validated'] += 1
        
        # Check format
        if not re.match(r'^[^@\s]+@[^@\s]+\.[a-z]{2,}$', email_str):
            result['issues'].append('Invalid format')
            return result
        
        # Extract parts
        local, domain = email_str.rsplit('@', 1)
        
        # Validate local part
        if not re.match(r'^[a-z0-9._%-]+$', local):
            result['issues'].append('Invalid local part')
            return result
        
        # Check length
        if len(local) > 64:
            result['issues'].append('Local part too long')
        
        if len(domain) > 255:
            result['issues'].append('Domain too long')
        
        # Check for consecutive dots
        if '..' in local or '..' in domain:
            result['issues'].append('Consecutive dots')
        
        # If no issues, email is valid
        if not result['issues']:
            result['valid'] = True
            result['email_clean'] = email_str
            result['domain'] = domain
            self.stats['valid_emails'] += 1
        
        return result
    
    def check_domain_quality(self, domain):
        """Check domain reputation"""
        if not domain:
            return 'UNKNOWN'
        
        if domain in self.DISPOSABLE_DOMAINS:
            return 'DISPOSABLE'
        
        if domain in self.GENERIC_DOMAINS:
            return 'GENERIC'
        
        # Check for personal domains
        personal = {'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com',
                   'aol.com', 'icloud.com', 'mail.com', 'protonmail.com'}
        if domain in personal:
            return 'PERSONAL'
        
        return 'BUSINESS'


class PhoneValidator:
    """Validate and standardize phone numbers"""
    
    def __init__(self):
        """Initialize phone validator"""
        self.stats = {'phones_standardized': 0, 'valid_phones': 0}
    
    def standardize_phone(self, phone, format_type='VBA'):
        """
        Standardize phone number to specified format
        
        Formats:
        - VBA: 314-550-0950 Ext. 1234
        - E164: +13145500950
        - INTL: +1 314-550-0950
        """
        if not phone or pd.isna(phone):
            return None, False, 0
        
        phone_str = str(phone).strip()
        
        # Extract extension
        extension = None
        ext_match = re.search(r'(?:ext\.?|x)\s*(\d+)', phone_str, re.IGNORECASE)
        if ext_match:
            extension = ext_match.group(1)
            phone_str = phone_str[:ext_match.start()].strip()
        
        # Extract digits only
        digits = re.sub(r'\D', '', phone_str)
        
        # Must have at least 10 digits
        if len(digits) < 10:
            return digits if digits else None, False, 20
        
        # Handle 11 digits (US +1 prefix)
        if len(digits) == 11 and digits[0] == '1':
            digits = digits[1:]
        elif len(digits) > 10:
            return digits, False, 40  # Invalid length
        
        # Now we have 10 digits
        if len(digits) != 10:
            return digits, False, 50
        
        # Format based on type
        if format_type == 'VBA':
            formatted = f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
            if extension:
                formatted += f" Ext. {extension}"
            self.stats['phones_standardized'] += 1
            self.stats['valid_phones'] += 1
            return formatted, True, 100
        
        elif format_type == 'E164':
            formatted = f"+1{digits}"
            if extension:
                formatted += f" Ext. {extension}"
            self.stats['phones_standardized'] += 1
            self.stats['valid_phones'] += 1
            return formatted, True, 100
        
        elif format_type == 'INTL':
            formatted = f"+1 {digits[:3]}-{digits[3:6]}-{digits[6:]}"
            if extension:
                formatted += f" Ext. {extension}"
            self.stats['phones_standardized'] += 1
            self.stats['valid_phones'] += 1
            return formatted, True, 100
        
        else:
            return digits, True, 80
    
    def detect_phone_type(self, phone):
        """Detect if phone is mobile or landline (basic detection)"""
        if not phone or pd.isna(phone):
            return None
        
        phone_str = str(phone).strip()
        digits = re.sub(r'\D', '', phone_str)
        
        if len(digits) < 10:
            return None
        
        # Extract area code (first 3 digits)
        area_code = digits[-10:-7] if len(digits) == 10 else digits[-10:-7]
        
        # Basic mobile area code patterns (simplified)
        # Real implementation would use NANP database
        mobile_patterns = ['201', '202', '203', '205', '206', '207', '208', '209',
                          '210', '212', '213', '214', '215', '216', '217', '218', '219']
        
        if area_code in mobile_patterns:
            return 'MOBILE'
        
        return 'LANDLINE'


class AddressValidator:
    """Validate address components"""
    
    # US state abbreviations
    US_STATES = {
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
        'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
        'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
        'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
        'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'DC'
    }
    
    def __init__(self):
        """Initialize address validator"""
        self.stats = {'addresses_validated': 0, 'valid_addresses': 0}
    
    def validate_zip(self, zip_code):
        """Validate US ZIP code format"""
        if not zip_code or pd.isna(zip_code):
            return False, None
        
        zip_str = str(zip_code).strip().upper()
        
        # Standard 5-digit ZIP
        if re.match(r'^\d{5}$', zip_str):
            return True, zip_str
        
        # ZIP+4 format
        if re.match(r'^\d{5}-\d{4}$', zip_str):
            return True, zip_str
        
        # Clean and try again
        clean = re.sub(r'\D', '', zip_str)
        if len(clean) == 5:
            return True, clean
        elif len(clean) == 9:
            return True, f"{clean[:5]}-{clean[5:]}"
        
        return False, None
    
    def standardize_state(self, state):
        """Standardize state to 2-letter abbreviation"""
        if not state or pd.isna(state):
            return None
        
        state_str = str(state).strip().upper()
        
        # Already a valid abbreviation
        if state_str in self.US_STATES:
            return state_str
        
        # State name mapping (partial)
        state_names = {
            'ALABAMA': 'AL', 'ALASKA': 'AK', 'ARIZONA': 'AZ', 'ARKANSAS': 'AR',
            'CALIFORNIA': 'CA', 'COLORADO': 'CO', 'CONNECTICUT': 'CT', 'DELAWARE': 'DE',
            'FLORIDA': 'FL', 'GEORGIA': 'GA', 'HAWAII': 'HI', 'IDAHO': 'ID',
            'ILLINOIS': 'IL', 'INDIANA': 'IN', 'IOWA': 'IA', 'KANSAS': 'KS',
            'KENTUCKY': 'KY', 'LOUISIANA': 'LA', 'MAINE': 'ME', 'MARYLAND': 'MD',
            'MASSACHUSETTS': 'MA', 'MICHIGAN': 'MI', 'MINNESOTA': 'MN', 'MISSISSIPPI': 'MS',
            'MISSOURI': 'MO', 'MONTANA': 'MT', 'NEBRASKA': 'NE', 'NEVADA': 'NV',
            'NEW HAMPSHIRE': 'NH', 'NEW JERSEY': 'NJ', 'NEW MEXICO': 'NM', 'NEW YORK': 'NY',
            'NORTH CAROLINA': 'NC', 'NORTH DAKOTA': 'ND', 'OHIO': 'OH', 'OKLAHOMA': 'OK',
            'OREGON': 'OR', 'PENNSYLVANIA': 'PA', 'RHODE ISLAND': 'RI', 'SOUTH CAROLINA': 'SC',
            'SOUTH DAKOTA': 'SD', 'TENNESSEE': 'TN', 'TEXAS': 'TX', 'UTAH': 'UT',
            'VERMONT': 'VT', 'VIRGINIA': 'VA', 'WASHINGTON': 'WA', 'WEST VIRGINIA': 'WV',
            'WISCONSIN': 'WI', 'WYOMING': 'WY', 'DISTRICT OF COLUMBIA': 'DC'
        }
        
        if state_str in state_names:
            return state_names[state_str]
        
        return None
    
    def validate_address_complete(self, street, city, state, zip_code):
        """Check if address is complete"""
        complete = True
        issues = []
        
        if not street or pd.isna(street):
            complete = False
            issues.append('Missing street')
        
        if not city or pd.isna(city):
            complete = False
            issues.append('Missing city')
        
        state_valid = self.standardize_state(state)
        if not state_valid:
            complete = False
            issues.append('Invalid state')
        
        zip_valid, _ = self.validate_zip(zip_code)
        if not zip_valid:
            complete = False
            issues.append('Invalid ZIP')
        
        return complete, issues
    
    def detect_po_box(self, street_address):
        """Detect if address is a PO Box"""
        if not street_address or pd.isna(street_address):
            return False
        
        street_upper = str(street_address).upper()
        return bool(re.search(r'\bP\.?O\.?\s+BOX\b|\bPOB\b', street_upper))


class NameValidator:
    """Validate name patterns"""
    
    def __init__(self):
        """Initialize name validator"""
        self.stats = {'names_validated': 0}
    
    def detect_invalid_patterns(self, first_name, last_name):
        """Detect obviously invalid names"""
        issues = []
        
        # Check first name
        if first_name and pd.notna(first_name):
            fname = str(first_name).strip()
            
            # All same character (AAA, XXX, etc.)
            if len(fname) > 1 and len(set(fname.upper())) == 1:
                issues.append('First name: all same character')
            
            # All numbers
            if fname.replace(' ', '').isdigit():
                issues.append('First name: all numbers')
            
            # Too short (single letter ok, but 2+ chars should be letter)
            if len(fname) > 1 and fname[0].isdigit():
                issues.append('First name: starts with number')
        
        # Check last name
        if last_name and pd.notna(last_name):
            lname = str(last_name).strip()
            
            # All same character
            if len(lname) > 1 and len(set(lname.upper())) == 1:
                issues.append('Last name: all same character')
            
            # All numbers
            if lname.replace(' ', '').isdigit():
                issues.append('Last name: all numbers')
        
        return len(issues) == 0, issues
    
    def check_realistic_length(self, first_name, last_name):
        """Check if names are realistic lengths"""
        issues = []
        
        if first_name and pd.notna(first_name):
            fname = str(first_name).strip()
            if len(fname) > 50:
                issues.append(f'First name too long: {len(fname)} chars')
        
        if last_name and pd.notna(last_name):
            lname = str(last_name).strip()
            if len(lname) > 50:
                issues.append(f'Last name too long: {len(lname)} chars')
        
        return len(issues) == 0, issues
    
    def validate_characters(self, first_name, last_name):
        """Check for invalid characters (emoji, control chars, etc.)"""
        issues = []
        
        for fname in [first_name, last_name]:
            if fname and pd.notna(fname):
                name_str = str(fname)
                
                # Check for emoji and special Unicode
                if any(ord(c) > 127 for c in name_str):
                    # Allow accented characters but flag others
                    if any(ord(c) > 1000 for c in name_str):
                        issues.append(f'Invalid characters in: {name_str}')
        
        return len(issues) == 0, issues


class QualityScorer:
    """Calculate comprehensive quality scores"""
    
    def __init__(self):
        """Initialize quality scorer"""
        self.email_validator = EmailValidator()
        self.phone_validator = PhoneValidator()
        self.address_validator = AddressValidator()
        self.name_validator = NameValidator()
    
    def calculate_score(self, record):
        """
        Calculate comprehensive quality score (0-115 possible)
        
        Scoring breakdown:
        - Name: 35 base + 5 bonus (if prefix/suffix/middle) = 40 max
        - Email: 25 (if valid)
        - Phone: 15 (if valid)
        - Address: 15 (if complete)
        - Company: 10 (if provided or extracted)
        - BONUS: +10% if all components present = 115 max
        """
        score = 0
        components = []
        issues = []
        
        # NAMES (40 max)
        first_name = record.get('first_name')
        last_name = record.get('last_name')
        middle_name = record.get('middle_name')
        prefix = record.get('prefix')
        suffix = record.get('suffix')
        
        has_name = pd.notna(first_name) and pd.notna(last_name)
        has_partial_name = pd.notna(first_name) or pd.notna(last_name)
        
        if has_name:
            score += 35
            components.append('Name')
            
            # Bonus for complete name components
            if (pd.notna(prefix) or pd.notna(suffix) or pd.notna(middle_name)):
                score += 5
                components.append('Name_Complete')
            
            # Validate name
            valid, name_issues = self.name_validator.detect_invalid_patterns(first_name, last_name)
            if not valid:
                score -= 5
                issues.extend(name_issues)
        
        elif has_partial_name:
            score += 17  # Partial credit
            components.append('Name_Partial')
        
        # EMAIL (25 max)
        email = record.get('primary_email')
        if pd.notna(email):
            email_result = self.email_validator.validate_email(email)
            if email_result['valid']:
                score += 25
                components.append('Email')
                
                # Check domain quality
                domain_quality = self.email_validator.check_domain_quality(email_result['domain'])
                if domain_quality == 'DISPOSABLE':
                    score -= 10
                    issues.append('Disposable email domain')
                elif domain_quality == 'GENERIC':
                    score -= 5
                    issues.append('Generic email domain')
            else:
                score += 5  # Some credit for having email
                issues.append(f"Invalid email: {', '.join(email_result['issues'])}")
        
        # PHONE (15 max)
        phone = record.get('primary_phone')
        if pd.notna(phone):
            phone_formatted, valid, conf = self.phone_validator.standardize_phone(phone)
            if valid and conf >= 90:
                score += 15
                components.append('Phone')
            elif conf >= 70:
                score += 8
                components.append('Phone_Uncertain')
            else:
                issues.append('Invalid phone format')
        
        # ADDRESS (15 max)
        street = record.get('street_address')
        city = record.get('city')
        state = record.get('state')
        zip_code = record.get('postal_code')
        
        address_complete, addr_issues = self.address_validator.validate_address_complete(street, city, state, zip_code)
        if address_complete:
            score += 15
            components.append('Address')
        else:
            partial = 0
            if pd.notna(street):
                partial += 1
            if pd.notna(city):
                partial += 1
            if pd.notna(state) and self.address_validator.standardize_state(state):
                partial += 1
            if pd.notna(zip_code):
                partial += 1
            
            if partial > 0:
                score += (15 * partial) // 4
                components.append(f'Address_Partial({partial}/4)')
            if addr_issues:
                issues.extend(addr_issues)
        
        # COMPANY (10 max)
        company = record.get('company')
        company_source = record.get('company_source')
        if pd.notna(company):
            score += 10
            if company_source == 'EXTRACTED_FROM_EMAIL':
                components.append('Company_Extracted')
            else:
                components.append('Company_Provided')
        
        # BONUS MULTIPLIER: +10% if ALL categories present
        has_all_categories = all([
            has_name,
            pd.notna(email),
            pd.notna(phone),
            address_complete,
            pd.notna(company)
        ])
        
        if has_all_categories:
            bonus = int(score * 0.10)
            score += bonus
            components.append(f'Bonus({bonus})')
        
        # Determine tier
        tier = 'PREMIUM' if score >= 85 else 'HIGH' if score >= 70 else 'MEDIUM' if score >= 50 else 'LOW' if score >= 30 else 'MINIMAL'
        
        return {
            'score': min(score, 115),  # Cap at 115
            'tier': tier,
            'components': '; '.join(components),
            'issues': '; '.join(issues) if issues else None,
            'max_score': 115
        }
    
    def score_dataframe(self, df):
        """Score all records in dataframe"""
        result_df = df.copy()
        
        scores = []
        tiers = []
        components_list = []
        issues_list = []
        
        for _, row in df.iterrows():
            score_result = self.calculate_score(row)
            scores.append(score_result['score'])
            tiers.append(score_result['tier'])
            components_list.append(score_result['components'])
            issues_list.append(score_result['issues'])
        
        result_df['quality_score'] = scores
        result_df['quality_tier'] = tiers
        result_df['quality_components'] = components_list
        result_df['quality_issues'] = issues_list
        
        return result_df