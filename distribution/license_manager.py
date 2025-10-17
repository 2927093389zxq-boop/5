"""
License manager stub for development mode.
"""

class LicenseManager:
    """Simple license manager that allows dev mode."""
    
    def verify_license(self, license_data):
        """Verify license data."""
        return {
            "valid": True,
            "feature_set": "all",
            "telemetry_enabled": False
        }
