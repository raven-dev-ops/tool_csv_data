#!/usr/bin/env python3
"""
MAMBO CORE - Platform Initialization & Configuration
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path

class MamboPlatform:
    """Core platform initialization and management"""
    
    def __init__(self, config_file=None):
        """Initialize platform"""
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = f"Mambo_Output_{self.timestamp}"
        self.lookups_dir = "Mambo_Lookups"
        
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.lookups_dir, exist_ok=True)
        
        # Setup logging
        self.log_file = os.path.join(self.output_dir, "mambo_processing.log")
        self._setup_logger()
        
        # Config
        self.config = self._load_config(config_file)
        
        self.log("✅ MAMBO Platform initialized")
        self.log(f"   Output: {self.output_dir}")
        self.log(f"   Lookups: {self.lookups_dir}")
    
    def _setup_logger(self):
        """Configure logging"""
        self.logger = logging.getLogger("mambo")
        self.logger.setLevel(logging.DEBUG)
        
        handler = logging.FileHandler(self.log_file)
        handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(message)s'
        ))
        self.logger.addHandler(handler)
    
    def _load_config(self, config_file=None):
        """Load configuration"""
        default_config = {
            'scoring_weights': {
                'name': 35,
                'email': 25,
                'phone': 15,
                'address': 15,
                'company': 10
            },
            'deduplication': {
                'fuzzy_threshold': 0.85,
                'company_domain_conservative': True
            },
            'enrichment': {
                'auto_company_from_email': True,
                'auto_title_extraction': False
            }
        }
        
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return json.load(f)
        
        return default_config
    
    def log(self, message):
        """Log message"""
        print(message)
        if hasattr(self, 'logger'):
            self.logger.info(message)
    
    def get_output_path(self, filename):
        """Get output file path"""
        return os.path.join(self.output_dir, filename)
    
    def get_lookups_path(self, filename):
        """Get lookup file path"""
        return os.path.join(self.lookups_dir, filename)