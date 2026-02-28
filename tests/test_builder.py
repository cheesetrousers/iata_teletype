import pytest
from unittest.mock import patch
from datetime import datetime, timezone
from message_builder.builder import IataMessageBuilder

@patch('message_builder.builder.datetime')
def test_builder_basic_message(mock_datetime):
    # Mock datetime to a specific UTC time
    mock_datetime.now.return_value = datetime(2023, 10, 15, 14, 30, tzinfo=timezone.utc)
    mock_datetime.timezone = timezone
    
    # "BA" will trigger CCITT5 filtering (true)
    dest = "LHRXXBA"
    orig = "JFKYYBA"
    body = "Flight@Delayed!"
    
    msg = IataMessageBuilder.build(dest, orig, body)
    
    # Asserting CCITT5 formatting stripped invalid chars and uppercased everything
    assert "QU LHRXXBA" in msg
    assert ".JFKYYBA 151430" in msg
    assert "FLIGHT DELAYED " in msg # "Flight@Delayed!" becomes "FLIGHT DELAYED " 

@patch('message_builder.builder.datetime')
def test_builder_with_tag(mock_datetime):
    mock_datetime.now.return_value = datetime(2023, 10, 15, 14, 30, tzinfo=timezone.utc)
    mock_datetime.timezone = timezone
    
    msg = IataMessageBuilder.build("LHRXXBA", "JFKYYBA", "BODY", tag="opt_tag")
    
    # Tag should be on its own line and UPPERCASED by the filter
    assert "\x02\r\nOPT TAG\r\nBODY" in msg # "opt_tag" translates to "OPT TAG" due to '_' replacement


@patch('message_builder.builder.datetime')
def test_builder_disable_ccitt5(mock_datetime):
    mock_datetime.now.return_value = datetime(2023, 10, 15, 14, 30, tzinfo=timezone.utc)
    mock_datetime.timezone = timezone
    
    # "AA" disables CCITT5 filtering in our rules engine
    dest = "LHRXXAA"
    orig = "JFKYYBA"
    body = "Flight@Delayed! (No Filter)"
    
    msg = IataMessageBuilder.build(dest, orig, body)
    
    assert "QU LHRXXAA" in msg
    # The body should remain mixed case with all special characters
    assert "Flight@Delayed! (No Filter)" in msg
