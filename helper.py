 
from fplib.fpmain import Fingerprint 
import os

class HelperUtils:
    @staticmethod
    def get_identifiers(identifiersStr):
        if not identifiersStr:
            return []

        identifiers = []
        for part in identifiersStr.split(","):
            part = part.strip()
            if not part:
                continue
            try:
                identifiers.append(int(part))
            except ValueError:
                print(f"⚠️ Invalid identifier skipped: '{part}'")

        return identifiers

    @staticmethod
    #fp type
    def check_enrollment_status(fp: Fingerprint, identifiersStr):
        count = 0 
        identifiers = HelperUtils.get_identifiers(identifiersStr)
        for x in  identifiers:
            if fp.check_enrolled(x):
                count += 1
        status_message = f"Enrolled {count} of {len(identifiers)}" if count > 0 else "Not Enrolled"
        return count > 0, status_message
    

 