 
import logging 
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
    def check_enrollment_status(fp, identifiersStr):
        count = 0 
        identifiers = HelperUtils.get_identifiers(identifiersStr)
        for x in  identifiers:
            if fp.check_enrolled(x):
                count += 1
        status_message = f"Enrolled {count} of {len(identifiers)}" if count > 0 else "Not Enrolled"
        return count > 0, status_message
    

    
    @staticmethod
    def logInfo(msg):
        print(msg)
        return
        logging.info(msg)

    @staticmethod 
    def logWarning(msg):
        print(f"Warning: {msg}")
        return
        logging.warning(msg)

    @staticmethod 
    def logError(msg):
        print(f"Error: {msg}")
        return
        logging.error(msg)

