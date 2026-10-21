"""ROS channel failure semantics with a fake node; no ROS network or robot commands."""
import json
from pathlib import Path
import sys
import time
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from runtime_gateway.adapters.collision_monitor import CollisionMonitorChannel
from runtime_gateway.errors import GatewayError


class Message:
    data = ''


@pytest.fixture
def channel(monkeypatch):
    monkeypatch.setitem(sys.modules, 'std_msgs.msg', SimpleNamespace(String=Message))
    node = Mock()
    publisher = Mock()
    publisher.get_subscription_count.return_value = 1
    node.create_publisher.return_value = publisher
    channel = CollisionMonitorChannel(lambda: node, discovery_timeout_s=0,
                                     confirmation_timeout_s=0.005, state_max_age_s=0.02)
    return node, publisher, channel


def test_matching_acknowledgement_confirms_only_its_request(channel):
    node, publisher, channel = channel
    def acknowledge(message):
        payload = json.loads(message.data)
        channel._observe(SimpleNamespace(data=json.dumps(payload)))
    publisher.publish.side_effect = acknowledge
    result = channel.publish({'diagnostics_enabled': True})
    assert result['diagnostics_enabled'] is True
    assert result['_request_id']
    node.create_subscription.assert_called_once()


def test_cached_equal_values_cannot_confirm_a_new_request(channel):
    node, publisher, channel = channel
    channel._channel()
    channel._observe(SimpleNamespace(data=json.dumps({'diagnostics_enabled': True, '_request_id': 'old'})))
    with pytest.raises(GatewayError) as failed:
        channel.publish({'diagnostics_enabled': True})
    assert failed.value.code == 'collision_config_confirmation_timeout'
    assert failed.value.outcome_unknown is True
    assert failed.value.retryable is False
    assert failed.value.details['command_id'] != 'old'


def test_unavailable_subscriber_is_known_not_sent(channel):
    node, publisher, channel = channel
    publisher.get_subscription_count.return_value = 0
    with pytest.raises(GatewayError) as failed:
        channel.publish({'diagnostics_enabled': True})
    assert failed.value.code == 'collision_config_subscriber_unavailable'
    assert not failed.value.outcome_unknown
    publisher.publish.assert_not_called()


def test_stale_observation_is_not_returned_as_applied(channel):
    node, publisher, channel = channel
    channel._channel()
    channel._observe(SimpleNamespace(data='{"detection_enabled":true}'))
    assert channel.observed()['detection_enabled']
    channel._received_at = time.monotonic() - 1
    assert channel.observed() is None
    with pytest.raises(GatewayError, match='fresh'):
        channel.read()


def test_invalid_json_observation_does_not_erase_good_state(channel):
    node, publisher, channel = channel
    channel._channel()
    channel._observe(SimpleNamespace(data='{"detection_enabled":true}'))
    channel._observe(SimpleNamespace(data='broken json'))
    assert channel.observed()['detection_enabled'] is True
