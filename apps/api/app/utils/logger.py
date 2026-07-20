import json
import logging
from datetime import datetime, timezone
from app.middleware.request_id import request_id_var

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        # Standardize audit log dictionary payload
        log_payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "request_id": request_id_var.get() or None
        }
        
        # Append traceback details if an exception is handled
        if record.exc_info:
            log_payload["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_payload)

def setup_logger(name: str = "forge") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Configure JSON console handler if no handlers exist
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.propagate = False # Prevent double logs in uvicorn
        
    return logger

logger = setup_logger()
