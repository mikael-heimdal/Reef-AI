from datetime import datetime

class GHLService:

    @staticmethod
    def get_status():
        return {
            "connected": True,
            "temperature": 25.3,
            "ph": 8.15,
            "kh": 8.1,
            "salinity": 35.0,
            "redox": 355,
            "timestamp": datetime.utcnow().isoformat()
        }