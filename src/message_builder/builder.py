import json
import os
import re
import logging
from datetime import datetime, timezone

logger = logging.getLogger("iata_builder")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
if not logger.handlers:
    logger.addHandler(handler)

class IataMessageBuilder:
    SOH = "\x01"  # Start of Heading
    STX = "\x02"  # Start of Text
    ETX = "\x03"  # End of Text
    CR = "\r"     # Carriage Return
    LF = "\n"     # Line Feed
    EOT = "\x04"    # End of Transmission
    
    CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "address_config.json")

    @classmethod
    def get_rule(cls, destination: str) -> dict:
        """
        Retrieves the rule for a given destination based on its last 2 characters.
        """
        dest_suffix = destination[-2:].upper() if len(destination) >= 2 else destination.upper()
        config = cls.load_config()
        rule = config.get(dest_suffix, {})
        return {
            "ccitt5": rule.get("ccitt5", True),
            "eot_enabled": rule.get("eot_enabled", False),
            "suffix": dest_suffix
        }

    @classmethod
    def load_config(cls) -> dict:
        if os.path.exists(cls.CONFIG_PATH):
            with open(cls.CONFIG_PATH, "r") as f:
                return json.load(f)
        return {}

    @classmethod
    def translate_to_ccitt5(cls, text: str) -> str:
        """
        Translates a string into strictly CCITT5 compatible characters.
        Uppercases all letters and replaces invalid symbols with spaces.
        """
        if not text:
            return text
        text = text.upper()
        # Keep A-Z, 0-9, whitespace (includes \r\n), and common IATA punctuation: . - + , ( ) ' = ? /
        text = re.sub(r'[^A-Z0-9\s\.\-\+\,\(\)\'\=\?\/]', ' ', text)
        return text

    @classmethod
    def build(cls, destination: str, origin: str, body: str, tag: str | None = None) -> str:
        """
        Builds a basic IATA teletype message as an ASCII string with control characters.
        """
        # Read the CCITT5 rule using the last 2 characters of the destination
        dest_suffix = destination[-2:].upper() if len(destination) >= 2 else destination.upper()
        config = cls.load_config()
        # Default is True for CCITT5 and False for EOT if not found
        rule = config.get(dest_suffix, {})
        use_ccitt5 = rule.get("ccitt5", True)
        eot_enabled = rule.get("eot_enabled", False)
        
        logger.info(f"Building Teletype Message -> Dest: {destination}, Orig: {origin}")
        logger.info(f"CCITT5 Translation enabled for suffix '{dest_suffix}': {use_ccitt5}")
        
        if use_ccitt5:
            destination = cls.translate_to_ccitt5(destination).replace(" ", "")
            origin = cls.translate_to_ccitt5(origin).replace(" ", "")
            if tag:
                tag = cls.translate_to_ccitt5(tag)
            body = cls.translate_to_ccitt5(body)
            logger.debug(f"Translated Body content successfully.")

        crlf = cls.CR + cls.LF
        
        # Header formatting
        header_dest = f"QU {destination}"
        
        # Timestamp formatted as DDHHMM (GMT)
        timestamp = datetime.now(timezone.utc).strftime("%d%H%M")
        header_orig = f".{origin} {timestamp}"

        # Assembling message
        message = (
            cls.SOH + crlf +
            header_dest + crlf +
            header_orig + crlf +
            cls.STX + crlf
        )
        
        # Add tag on its own line immediately after STX if provided
        if tag:
            message += tag + crlf
            
        message += body + crlf + cls.ETX
        
        if eot_enabled:
            message += crlf + cls.EOT
            
        return message
