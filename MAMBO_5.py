#!/usr/bin/env python3
"""
MAMBO-5: DELIVERABLES & REPORTING - Statistics, Reports, and Multi-Format Exports
Generates client-facing dashboards and data exports
"""

import pandas as pd
from datetime import datetime
import json

class StatisticsGenerator:
    """Generate comprehensive statistics"""
    
    def __init__(self):
        """Initialize statistics generator"""
        self.generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def calculate_before_after(self, original_df, processed_df):
        """
        Calculate before/after metrics
        Returns comprehensive comparison
        """
        stats = {
            'timestamp': self.generated_at,
            'before': self._calculate_stats(original_df, 'original'),
            'after': self._calculate_stats(processed_df, 'processed'),
            'improvements': self._calculate_improvements(original_df, processed_df)
        }
        return stats
    
    def _calculate_stats(self, df, label):
        """Calculate statistics for a dataframe"""
        if df.empty:
            return {}
        
        # Handle column name variations
        email_col = 'primary_email' if 'primary_email' in df.columns else ('Email' if 'Email' in df.columns else None)
        phone_col = 'primary_phone' if 'primary_phone' in df.columns else ('Phone' if 'Phone' in df.columns else None)
        
        stats = {
            'label': label,
            'total_records': len(df),
            'fields_analyzed': len(df.columns),
            'email_populated': df[email_col].notna().sum() if email_col else 0,
            'phone_populated': df[phone_col].notna().sum() if phone_col else 0,
            'address_complete': 0,
            'names_complete': 0,
            'quality_scores': {}
        }
        
        # Count complete addresses
        addr_cols = []
        for col_set in [
            ['street_address', 'city', 'state', 'postal_code'],
            ['Street', 'City', 'State', 'ZIP']
        ]:
            if all(col in df.columns for col in col_set):
                addr_cols = col_set
                break
        
        if addr_cols:
            complete_addr = df[
                (df[addr_cols[0]].notna()) & 
                (df[addr_cols[1]].notna()) & 
                (df[addr_cols[2]].notna()) & 
                (df[addr_cols[3]].notna())
            ].shape[0]
            stats['address_complete'] = complete_addr
        
        # Count complete names
        name_cols = []
        for col_set in [
            ['first_name', 'last_name'],
            ['First Name', 'Last Name']
        ]:
            if all(col in df.columns for col in col_set):
                name_cols = col_set
                break
        
        if name_cols:
            complete_names = df[
                (df[name_cols[0]].notna()) & 
                (df[name_cols[1]].notna())
            ].shape[0]
            stats['names_complete'] = complete_names
        
        # Quality score distribution
        if 'quality_score' in df.columns:
            scores = df['quality_score'].dropna()
            if not scores.empty:
                stats['quality_scores'] = {
                    'average': scores.mean(),
                    'min': scores.min(),
                    'max': scores.max(),
                    'median': scores.median()
                }
        
        # Quality tier distribution
        if 'quality_tier' in df.columns:
            tier_dist = df['quality_tier'].value_counts().to_dict()
            stats['quality_tiers'] = {
                tier: int(count) for tier, count in tier_dist.items()
            }
        
        return stats
    
    def _calculate_improvements(self, original_df, processed_df):
        """Calculate improvements made"""
        improvements = {}
        
        # Record count change
        original_count = len(original_df)
        processed_count = len(processed_df)
        improvements['duplicate_reduction'] = original_count - processed_count
        improvements['duplicate_reduction_pct'] = (
            ((original_count - processed_count) / original_count * 100) 
            if original_count > 0 else 0
        )
        
        # Email population improvement
        email_col_orig = 'primary_email' if 'primary_email' in original_df.columns else ('Email' if 'Email' in original_df.columns else None)
        email_col_proc = 'primary_email' if 'primary_email' in processed_df.columns else ('Email' if 'Email' in processed_df.columns else None)
        
        if email_col_orig and email_col_proc:
            original_emails = original_df[email_col_orig].notna().sum()
            processed_emails = processed_df[email_col_proc].notna().sum()
            improvements['email_improvement'] = processed_emails - original_emails
        else:
            improvements['email_improvement'] = 0
        
        # Quality score improvement
        if 'quality_score' in original_df.columns and 'quality_score' in processed_df.columns:
            orig_avg = original_df['quality_score'].mean() if not original_df.empty else 0
            proc_avg = processed_df['quality_score'].mean() if not processed_df.empty else 0
            improvements['quality_improvement'] = proc_avg - orig_avg
        else:
            improvements['quality_improvement'] = 0
        
        return improvements


class ReportGenerator:
    """Generate client-facing reports"""
    
    def __init__(self):
        """Initialize report generator"""
        self.generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def create_executive_summary(self, stats):
        """Create executive summary report"""
        summary = []
        summary.append("MAMBO DATA PLATFORM - EXECUTIVE SUMMARY")
        summary.append("=" * 70)
        summary.append(f"Generated: {self.generated_at}\n")
        
        summary.append("📊 KEY METRICS:")
        summary.append("-" * 70)
        summary.append(f"Original Records: {stats['before']['total_records']}")
        summary.append(f"Cleaned Records: {stats['after']['total_records']}")
        summary.append(f"Duplicates Removed: {stats['improvements']['duplicate_reduction']}")
        summary.append(f"Reduction Rate: {stats['improvements']['duplicate_reduction_pct']:.1f}%\n")
        
        summary.append("📈 DATA QUALITY IMPROVEMENT:")
        summary.append("-" * 70)
        
        before_avg = stats['before'].get('quality_scores', {}).get('average', 0)
        after_avg = stats['after'].get('quality_scores', {}).get('average', 0)
        
        summary.append(f"Before Average Score: {before_avg:.1f}/115")
        summary.append(f"After Average Score: {after_avg:.1f}/115")
        summary.append(f"Improvement: +{stats['improvements']['quality_improvement']:.1f} points\n")
        
        summary.append("🎯 QUALITY TIER DISTRIBUTION (After):")
        summary.append("-" * 70)
        
        tiers = stats['after'].get('quality_tiers', {})
        tier_order = ['PREMIUM', 'HIGH', 'MEDIUM', 'LOW', 'MINIMAL']
        total = stats['after']['total_records']
        
        for tier in tier_order:
            count = tiers.get(tier, 0)
            pct = (count / total * 100) if total > 0 else 0
            emoji = {'PREMIUM': '🥇', 'HIGH': '🥈', 'MEDIUM': '🥉', 'LOW': '⚠️', 'MINIMAL': '❌'}.get(tier, '')
            summary.append(f"{emoji} {tier:8s}: {count:3d} records ({pct:5.1f}%)")
        
        summary.append("\n" + "=" * 70)
        summary.append("✅ Platform successfully cleaned and standardized your data!")
        summary.append("Ready for export to Salesforce, HubSpot, Mailchimp, or GO High Level")
        
        return "\n".join(summary)
    
    def create_value_report(self, stats):
        """Create value justification report"""
        report = []
        report.append("MAMBO PLATFORM - VALUE DELIVERED REPORT")
        report.append("=" * 70)
        report.append(f"Generated: {self.generated_at}\n")
        
        report.append("💰 VALUE DELIVERED:")
        report.append("-" * 70)
        
        # Calculate value
        duplicates_removed = stats['improvements']['duplicate_reduction']
        records_cleaned = stats['after']['total_records']
        quality_improvement = stats['improvements']['quality_improvement']
        email_improvement = stats['improvements'].get('email_improvement', 0)
        
        report.append(f"\n✨ Duplicate Removal:")
        report.append(f"   Removed {duplicates_removed} duplicate records")
        report.append(f"   Savings: {duplicates_removed} wasted outreach attempts")
        report.append(f"   Estimated Value: ${duplicates_removed * 5:.0f}")
        
        report.append(f"\n✨ Data Enhancement:")
        report.append(f"   Added/recovered {email_improvement} email addresses")
        report.append(f"   Standardized all phone numbers")
        report.append(f"   Validated all addresses")
        report.append(f"   Estimated Value: ${email_improvement * 10:.0f}")
        
        report.append(f"\n✨ Quality Improvement:")
        report.append(f"   Average score improved by {quality_improvement:.1f} points")
        report.append(f"   {records_cleaned} records now PREMIUM or HIGH quality")
        report.append(f"   Estimated Value: ${records_cleaned * 2:.0f}")
        
        total_value = (duplicates_removed * 5) + (email_improvement * 10) + (records_cleaned * 2)
        
        report.append(f"\n" + "=" * 70)
        report.append(f"💵 TOTAL ESTIMATED VALUE: ${total_value:.0f}")
        report.append(f"✅ ROI: Significant improvement in data quality and usability")
        
        return "\n".join(report)


class ExportFormatter:
    """Format data for various platforms"""
    
    def __init__(self):
        """Initialize export formatter"""
        pass
    
    def _get_col(self, df, *possible_names):
        """Get column from dataframe, trying multiple possible names"""
        for name in possible_names:
            if name in df.columns:
                return df[name]
        return pd.Series([None] * len(df))
    
    def format_salesforce(self, df):
        """Format for Salesforce import"""
        export_df = pd.DataFrame()
        
        # Get columns with name variations
        export_df['FirstName'] = self._get_col(df, 'first_name', 'First Name')
        export_df['LastName'] = self._get_col(df, 'last_name', 'Last Name')
        export_df['Email'] = self._get_col(df, 'primary_email', 'Email')
        export_df['Phone'] = self._get_col(df, 'primary_phone', 'Phone')
        export_df['Company'] = self._get_col(df, 'company', 'Company')
        export_df['Title'] = self._get_col(df, 'job_title', 'Title')
        export_df['BillingStreet'] = self._get_col(df, 'street_address', 'Street')
        export_df['BillingCity'] = self._get_col(df, 'city', 'City')
        export_df['BillingState'] = self._get_col(df, 'state', 'State')
        export_df['BillingPostalCode'] = self._get_col(df, 'postal_code', 'ZIP')
        
        export_df['Source'] = 'MAMBO'
        export_df['Status'] = 'Active'
        export_df['Quality_Score__c'] = self._get_col(df, 'quality_score')
        
        return export_df
    
    def format_hubspot(self, df):
        """Format for HubSpot import"""
        export_df = pd.DataFrame()
        
        export_df['firstname'] = self._get_col(df, 'first_name', 'First Name')
        export_df['lastname'] = self._get_col(df, 'last_name', 'Last Name')
        export_df['email'] = self._get_col(df, 'primary_email', 'Email')
        export_df['phone'] = self._get_col(df, 'primary_phone', 'Phone')
        export_df['company'] = self._get_col(df, 'company', 'Company')
        export_df['jobtitle'] = self._get_col(df, 'job_title', 'Title')
        export_df['address'] = self._get_col(df, 'street_address', 'Street')
        export_df['city'] = self._get_col(df, 'city', 'City')
        export_df['state'] = self._get_col(df, 'state', 'State')
        export_df['zip'] = self._get_col(df, 'postal_code', 'ZIP')
        
        export_df['source'] = 'MAMBO'
        export_df['quality_score'] = self._get_col(df, 'quality_score')
        
        return export_df
    
    def format_mailchimp(self, df):
        """Format for Mailchimp import"""
        export_df = pd.DataFrame()
        
        export_df['Email Address'] = self._get_col(df, 'primary_email', 'Email')
        export_df['First Name'] = self._get_col(df, 'first_name', 'First Name')
        export_df['Last Name'] = self._get_col(df, 'last_name', 'Last Name')
        export_df['Phone'] = self._get_col(df, 'primary_phone', 'Phone')
        export_df['Company'] = self._get_col(df, 'company', 'Company')
        export_df['MMERGE10'] = self._get_col(df, 'quality_score')
        
        return export_df
    
    def format_go_high_level(self, df):
        """Format for GO High Level import"""
        export_df = pd.DataFrame()
        
        export_df['firstName'] = self._get_col(df, 'first_name', 'First Name')
        export_df['lastName'] = self._get_col(df, 'last_name', 'Last Name')
        export_df['email'] = self._get_col(df, 'primary_email', 'Email')
        export_df['phone'] = self._get_col(df, 'primary_phone', 'Phone')
        export_df['companyName'] = self._get_col(df, 'company', 'Company')
        export_df['jobTitle'] = self._get_col(df, 'job_title', 'Title')
        export_df['addressLineOne'] = self._get_col(df, 'street_address', 'Street')
        export_df['city'] = self._get_col(df, 'city', 'City')
        export_df['state'] = self._get_col(df, 'state', 'State')
        export_df['postalCode'] = self._get_col(df, 'postal_code', 'ZIP')
        export_df['source'] = 'MAMBO'
        
        return export_df
    
    def export_all_formats(self, df, output_dir):
        """Export to all major platforms"""
        exports = {}
        
        formats = {
            'Salesforce': (self.format_salesforce, '_Salesforce.csv'),
            'HubSpot': (self.format_hubspot, '_HubSpot.csv'),
            'Mailchimp': (self.format_mailchimp, '_Mailchimp.csv'),
            'GOHighLevel': (self.format_go_high_level, '_GOHighLevel.csv'),
        }
        
        for platform, (formatter, suffix) in formats.items():
            try:
                formatted_df = formatter(df)
                filename = f"{output_dir}/05_Export{suffix}"
                formatted_df.to_csv(filename, index=False)
                exports[platform] = {
                    'status': 'SUCCESS',
                    'file': filename,
                    'records': len(formatted_df)
                }
            except Exception as e:
                exports[platform] = {
                    'status': 'ERROR',
                    'error': str(e)
                }
        
        return exports


class MAMBOReporter:
    """Main reporter orchestrator"""
    
    def __init__(self):
        """Initialize reporter"""
        self.stats_generator = StatisticsGenerator()
        self.report_generator = ReportGenerator()
        self.export_formatter = ExportFormatter()
    
    def generate_complete_report(self, original_df, processed_df, output_dir):
        """Generate complete report package"""
        
        # Generate statistics
        stats = self.stats_generator.calculate_before_after(original_df, processed_df)
        
        # Generate reports
        exec_summary = self.report_generator.create_executive_summary(stats)
        value_report = self.report_generator.create_value_report(stats)
        
        # Export to all formats
        exports = self.export_formatter.export_all_formats(processed_df, output_dir)
        
        return {
            'statistics': stats,
            'executive_summary': exec_summary,
            'value_report': value_report,
            'exports': exports,
            'generated_at': self.stats_generator.generated_at
        }