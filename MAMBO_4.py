#!/usr/bin/env python3
"""
MAMBO-4: DEDUPLICATE & RECLEAN - Duplicate Detection & Merge Engine
Finds duplicates using fuzzy matching and safely merges records
"""

import pandas as pd
import re
from difflib import SequenceMatcher

class DuplicateDetector:
    """Detect duplicate records using multiple matching strategies"""
    
    def __init__(self):
        """Initialize duplicate detector"""
        self.stats = {
            'records_compared': 0,
            'exact_email_matches': 0,
            'fuzzy_name_matches': 0,
            'phone_matches': 0,
            'potential_duplicates': 0,
        }
    
    def normalize_email(self, email):
        """Normalize email for comparison"""
        if not email or pd.isna(email):
            return None
        return str(email).strip().lower()
    
    def normalize_name(self, name):
        """Normalize name for fuzzy matching"""
        if not name or pd.isna(name):
            return None
        # Remove punctuation, extra spaces, convert to lowercase
        name_str = str(name).strip().lower()
        name_str = re.sub(r'[^\w\s]', '', name_str)
        name_str = ' '.join(name_str.split())
        return name_str
    
    def extract_phone_digits(self, phone):
        """Extract only digits from phone for comparison"""
        if not phone or pd.isna(phone):
            return None
        digits = re.sub(r'\D', '', str(phone))
        return digits if digits else None
    
    def fuzzy_match_score(self, str1, str2, threshold=0.85):
        """
        Calculate fuzzy match score (0-1)
        Returns (score, is_match)
        """
        if not str1 or not str2:
            return 0.0, False
        
        s1 = self.normalize_name(str1)
        s2 = self.normalize_name(str2)
        
        if not s1 or not s2:
            return 0.0, False
        
        # Exact match is best
        if s1 == s2:
            return 1.0, True
        
        # Use SequenceMatcher for fuzzy matching
        score = SequenceMatcher(None, s1, s2).ratio()
        is_match = score >= threshold
        
        return score, is_match
    
    def match_emails(self, email1, email2):
        """Match emails (exact or variant)"""
        norm1 = self.normalize_email(email1)
        norm2 = self.normalize_email(email2)
        
        if not norm1 or not norm2:
            return 0.0
        
        # Exact match
        if norm1 == norm2:
            return 1.0
        
        # Extract local and domain parts
        try:
            local1, domain1 = norm1.rsplit('@', 1)
            local2, domain2 = norm2.rsplit('@', 1)
        except:
            return 0.0
        
        # Same domain with similar local = high confidence
        if domain1 == domain2:
            score, _ = self.fuzzy_match_score(local1, local2, 0.85)
            return score * 0.95  # Slightly lower than exact
        
        # Different domain = lower confidence
        score, _ = self.fuzzy_match_score(norm1, norm2, 0.90)
        return score * 0.7
    
    def match_names(self, first1, last1, first2, last2, threshold=0.85):
        """
        Match first and last names
        Returns confidence score (0-1)
        """
        if not (first1 and last1 and first2 and last2):
            return 0.0
        
        # Both first and last must match
        first_score, first_match = self.fuzzy_match_score(first1, first2, threshold)
        last_score, last_match = self.fuzzy_match_score(last1, last2, threshold)
        
        if first_match and last_match:
            # Both match: average the scores
            return (first_score + last_score) / 2
        
        return 0.0
    
    def match_phones(self, phone1, phone2):
        """Match phones (digit extraction)"""
        digits1 = self.extract_phone_digits(phone1)
        digits2 = self.extract_phone_digits(phone2)
        
        if not digits1 or not digits2:
            return 0.0
        
        # Must have at least 10 digits (US phone)
        if len(digits1) < 10 or len(digits2) < 10:
            return 0.0
        
        # Exact match of last 10 digits
        if digits1[-10:] == digits2[-10:]:
            return 1.0
        
        return 0.0
    
    def find_duplicates(self, df, email_threshold=0.90, name_threshold=0.85, 
                       confidence_min=0.70):
        """
        Find potential duplicates in dataframe
        Returns list of (idx1, idx2, confidence, match_type)
        """
        duplicates = []
        n_records = len(df)
        self.stats['records_compared'] = n_records
        
        for i in range(n_records):
            for j in range(i + 1, n_records):
                record_i = df.iloc[i]
                record_j = df.iloc[j]
                
                # Email match (highest confidence)
                email_i = record_i.get('primary_email')
                email_j = record_j.get('primary_email')
                
                if pd.notna(email_i) and pd.notna(email_j):
                    email_score = self.match_emails(email_i, email_j)
                    if email_score >= email_threshold:
                        duplicates.append({
                            'idx1': i,
                            'idx2': j,
                            'confidence': email_score,
                            'match_type': 'EMAIL',
                            'evidence': f"{email_i} ≈ {email_j}"
                        })
                        self.stats['exact_email_matches'] += 1
                        continue
                
                # Phone match (high confidence, no false positives)
                phone_i = record_i.get('primary_phone')
                phone_j = record_j.get('primary_phone')
                
                if pd.notna(phone_i) and pd.notna(phone_j):
                    phone_score = self.match_phones(phone_i, phone_j)
                    if phone_score >= 0.95:  # Phone must match exactly
                        duplicates.append({
                            'idx1': i,
                            'idx2': j,
                            'confidence': phone_score,
                            'match_type': 'PHONE',
                            'evidence': f"{phone_i} = {phone_j}"
                        })
                        self.stats['phone_matches'] += 1
                        continue
                
                # Name match (fuzzy, requires both first and last)
                first_i = record_i.get('first_name')
                last_i = record_i.get('last_name')
                first_j = record_j.get('first_name')
                last_j = record_j.get('last_name')
                
                if (pd.notna(first_i) and pd.notna(last_i) and 
                    pd.notna(first_j) and pd.notna(last_j)):
                    
                    name_score = self.match_names(first_i, last_i, first_j, last_j, 
                                                 threshold=name_threshold)
                    
                    if name_score >= confidence_min:
                        # Additional check: email or phone should also be similar
                        # (to avoid false positives with common names)
                        
                        duplicates.append({
                            'idx1': i,
                            'idx2': j,
                            'confidence': name_score,
                            'match_type': 'NAME',
                            'evidence': f"{first_i} {last_i} ≈ {first_j} {last_j}"
                        })
                        self.stats['fuzzy_name_matches'] += 1
        
        self.stats['potential_duplicates'] = len(duplicates)
        return duplicates
    
    def get_stats(self):
        """Return detection statistics"""
        return self.stats


class DuplicateMerger:
    """Merge duplicate records intelligently"""
    
    def __init__(self):
        """Initialize merger"""
        self.stats = {
            'records_merged': 0,
            'conflicts_resolved': 0,
            'data_recovered': 0,
        }
    
    def _get_best_value(self, value1, value2, source1_score=None, source2_score=None):
        """
        Get best value between two options
        Prefers: non-empty > non-null > longest > first
        """
        # Both empty
        if (pd.isna(value1) or str(value1).strip() == '') and \
           (pd.isna(value2) or str(value2).strip() == ''):
            return None
        
        # One is empty, return other
        val1_empty = pd.isna(value1) or str(value1).strip() == ''
        val2_empty = pd.isna(value2) or str(value2).strip() == ''
        
        if val1_empty:
            return value2
        if val2_empty:
            return value1
        
        # Both have values - use score if provided
        if source1_score is not None and source2_score is not None:
            if source1_score > source2_score:
                return value1
            elif source2_score > source1_score:
                return value2
        
        # Use length (longer is usually better for addresses, names)
        len1 = len(str(value1)) if value1 else 0
        len2 = len(str(value2)) if value2 else 0
        
        if len1 > len2:
            return value1
        elif len2 > len1:
            return value2
        
        # Default to first
        return value1
    
    def merge_records(self, record1, record2, duplicate_info):
        """
        Merge two duplicate records into one
        Returns merged record and merge report
        """
        merged = {}
        conflicts = []
        data_recovered = 0
        
        # Key fields to prioritize
        critical_fields = ['primary_email', 'primary_phone', 'first_name', 'last_name']
        
        all_fields = set(record1.keys()) | set(record2.keys())
        
        for field in all_fields:
            val1 = record1.get(field)
            val2 = record2.get(field)
            
            # Both have values and they differ
            if (pd.notna(val1) and pd.notna(val2) and str(val1) != str(val2)):
                
                # For critical fields, use best value
                if field in critical_fields:
                    score1 = record1.get(f'{field}_confidence', 50)
                    score2 = record2.get(f'{field}_confidence', 50)
                    best = self._get_best_value(val1, val2, score1, score2)
                    merged[field] = best
                    conflicts.append({
                        'field': field,
                        'value1': val1,
                        'value2': val2,
                        'selected': best
                    })
                    self.stats['conflicts_resolved'] += 1
                else:
                    # For non-critical fields, take first non-empty
                    merged[field] = self._get_best_value(val1, val2)
                    if merged[field] == val2:
                        data_recovered += 1
                        self.stats['data_recovered'] += 1
            
            # One has value
            elif pd.notna(val1):
                merged[field] = val1
            elif pd.notna(val2):
                merged[field] = val2
                if field not in critical_fields:
                    data_recovered += 1
                    self.stats['data_recovered'] += 1
        
        # Add merge metadata
        merged['merged_from'] = f"Record 1 + Record 2"
        merged['merge_confidence'] = duplicate_info.get('confidence', 0)
        merged['merge_match_type'] = duplicate_info.get('match_type', 'UNKNOWN')
        merged['merge_evidence'] = duplicate_info.get('evidence', '')
        
        self.stats['records_merged'] += 1
        
        return merged, {
            'num_conflicts': len(conflicts),
            'conflicts_resolved': conflicts,
            'data_recovered': data_recovered,
            'merge_confidence': duplicate_info.get('confidence', 0),
            'match_type': duplicate_info.get('match_type', 'UNKNOWN')
        }
    
    def merge_dataframe(self, df, duplicates):
        """
        Merge all duplicate groups in dataframe
        Returns merged dataframe and merge audit trail
        """
        # Create set of indices to skip (merged records)
        merged_indices = set()
        audit_trail = []
        result_records = []
        
        # Sort duplicates by confidence (highest first)
        sorted_dupes = sorted(duplicates, key=lambda x: x['confidence'], reverse=True)
        
        # Track which indices have been merged
        idx_map = {}  # Maps old index to merge group
        
        for dup in sorted_dupes:
            idx1, idx2 = dup['idx1'], dup['idx2']
            
            # Skip if either record already merged
            if idx1 in merged_indices or idx2 in merged_indices:
                continue
            
            # Merge the records
            record1 = df.iloc[idx1].to_dict()
            record2 = df.iloc[idx2].to_dict()
            
            merged, report = self.merge_records(record1, record2, dup)
            result_records.append(merged)
            
            # Mark as merged
            merged_indices.add(idx1)
            merged_indices.add(idx2)
            
            # Track merge
            audit_trail.append({
                'merged_from_idx': [idx1, idx2],
                'result_idx': len(result_records) - 1,
                'match_type': report['match_type'],
                'confidence': report['merge_confidence'],
                'num_conflicts': report['num_conflicts'],
                'data_recovered': report['data_recovered'],
                'evidence': dup.get('evidence', '')
            })
        
        # Add non-merged records
        for idx in range(len(df)):
            if idx not in merged_indices:
                result_records.append(df.iloc[idx].to_dict())
        
        # Convert to dataframe
        result_df = pd.DataFrame(result_records)
        
        return result_df, audit_trail
    
    def get_stats(self):
        """Return merge statistics"""
        return self.stats


class DeduplicationEngine:
    """Main deduplication orchestrator"""
    
    def __init__(self, aggressive_mode=False):
        """
        Initialize deduplication engine
        
        aggressive_mode: If True, use lower thresholds for personal domains
        """
        self.detector = DuplicateDetector()
        self.merger = DuplicateMerger()
        self.aggressive_mode = aggressive_mode
    
    def deduplicate(self, df, email_threshold=0.90, name_threshold=0.85, 
                   confidence_min=0.70):
        """
        Complete deduplication workflow
        Returns: (deduplicated_df, duplicates_found, merge_audit_trail)
        """
        
        # Adjust thresholds for aggressive mode
        if self.aggressive_mode:
            email_threshold = 0.85
            name_threshold = 0.80
            confidence_min = 0.65
        
        # Find duplicates
        duplicates = self.detector.find_duplicates(
            df, 
            email_threshold=email_threshold,
            name_threshold=name_threshold,
            confidence_min=confidence_min
        )
        
        # Merge duplicates
        if duplicates:
            deduplicated_df, audit_trail = self.merger.merge_dataframe(df, duplicates)
        else:
            deduplicated_df = df.copy()
            audit_trail = []
        
        return deduplicated_df, duplicates, audit_trail
    
    def get_statistics(self):
        """Get complete statistics"""
        return {
            'detector_stats': self.detector.get_stats(),
            'merger_stats': self.merger.get_stats(),
            'aggressive_mode': self.aggressive_mode
        }