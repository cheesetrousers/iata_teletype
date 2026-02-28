from datetime import datetime, timezone
from message_builder.builder import IataMessageBuilder

def test_message_control_characters_with_tag(monkeypatch):
    # Mock datetime to a specific UTC time using pytest's monkeypatch
    mock_now = datetime(2023, 10, 15, 14, 30, tzinfo=timezone.utc)
    
    class MockDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return mock_now

    monkeypatch.setattr("message_builder.builder.datetime", MockDateTime)
    
    dest = "LHRXXBA"
    orig = "JFKYYBA"
    body = "FLIGHT DELAYED DUE TO WEATHER"
    tag = "OPTIONAL TAG"
    
    msg = IataMessageBuilder.build(dest, orig, body, tag=tag)
    
    # Expected structure:
    # <SOH><CR><LF>
    # QU LHRXXBA<CR><LF>
    # .JFKYYBA 151430<CR><LF>
    # <STX><CR><LF>
    # OPTIONAL TAG<CR><LF>
    # FLIGHT DELAYED DUE TO WEATHER<CR><LF>
    # <ETX>
    
    SOH = "\x01"
    STX = "\x02"
    ETX = "\x03"
    CRLF = "\r\n"
    
    # Check exact byte-by-byte sequence for crucial bits
    assert msg.startswith(f"{SOH}{CRLF}")
    assert f"{CRLF}QU {dest}{CRLF}" in msg
    assert f"{CRLF}.{orig} 151430{CRLF}" in msg
    assert f"{CRLF}{STX}{CRLF}" in msg
    assert f"OPTIONAL TAG{CRLF}" in msg
    assert f"FLIGHT DELAYED DUE TO WEATHER{CRLF}" in msg
    assert msg.endswith(ETX)
    
    # Verify the exact full message construction
    expected_full = (
        f"{SOH}{CRLF}"        # Start Of Heading + CRLF
        f"QU {dest}{CRLF}"    # Priority + Dest + CRLF
        f".{orig} 151430{CRLF}" # Originator + Timestamp (GMT) + CRLF
        f"{STX}{CRLF}"        # Start Of Text + CRLF
        f"{tag}{CRLF}"         # Tag + CRLF
        f"{body}{CRLF}"        # Message Body + CRLF
        f"{ETX}"               # End Of Text
    )
    
    assert msg == expected_full


def test_message_control_characters_no_tag(monkeypatch):
    # Mock datetime similarly
    mock_now = datetime(2023, 10, 15, 14, 30, tzinfo=timezone.utc)
    
    class MockDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return mock_now

    monkeypatch.setattr("message_builder.builder.datetime", MockDateTime)
    
    dest = "LHRXXBA"
    orig = "JFKYYBA"
    body = "FLIGHT DELAYED DUE TO WEATHER"
    
    msg = IataMessageBuilder.build(dest, orig, body)
    
    SOH = "\x01"
    STX = "\x02"
    ETX = "\x03"
    CRLF = "\r\n"
    
    expected_full = (
        f"{SOH}{CRLF}"
        f"QU {dest}{CRLF}"
        f".{orig} 151430{CRLF}"
        f"{STX}{CRLF}"
        f"{body}{CRLF}"
        f"{ETX}"
    )
    assert msg == expected_full


def test_message_with_eot_enabled(monkeypatch):
    # Mock datetime
    mock_now = datetime(2023, 10, 15, 14, 30, tzinfo=timezone.utc)
    class MockDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return mock_now
    monkeypatch.setattr("message_builder.builder.datetime", MockDateTime)
    
    # "XR" has eot_enabled: True in address_config.json
    dest = "LHRXXXR"
    orig = "JFKYYBA"
    body = "FLIGHT DELAYED"
    
    msg = IataMessageBuilder.build(dest, orig, body)
    
    SOH = "\x01"
    STX = "\x02"
    ETX = "\x03"
    EOT = "\x04"
    CRLF = "\r\n"
    
    expected_full = (
        f"{SOH}{CRLF}"
        f"QU {dest}{CRLF}"
        f".{orig} 151430{CRLF}"
        f"{STX}{CRLF}"
        f"{body}{CRLF}"
        f"{ETX}"
        f"{CRLF}{EOT}"
    )
    assert msg.endswith(f"{ETX}{CRLF}{EOT}")
    assert msg == expected_full
