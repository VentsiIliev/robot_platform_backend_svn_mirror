"""ROS collision channel with bounded waits, request correlation and fresh observations."""
import json
import logging
import threading
import time
from uuid import uuid4

from runtime_gateway.errors import GatewayError

logger = logging.getLogger(__name__)


class CollisionMonitorChannel:
    def __init__(self, node_getter, *, discovery_timeout_s=1.0, confirmation_timeout_s=2.0,
                 state_max_age_s=2.0):
        self._node_getter = node_getter
        self._discovery_timeout = discovery_timeout_s
        self._confirmation_timeout = confirmation_timeout_s
        self._state_max_age = state_max_age_s
        self._publisher = None
        self._subscription = None
        self._channel_node = None
        self._setup_lock = threading.Lock()
        self._command_lock = threading.Lock()
        self._changed = threading.Condition()
        self._state = None
        self._received_at = 0.0

    def _observe(self, message):
        try:
            state = json.loads(message.data)
            if not isinstance(state, dict):
                return
        except (TypeError, ValueError):
            logger.warning('Ignored invalid collision configuration observation')
            return
        with self._changed:
            self._state = state
            self._received_at = time.monotonic()
            self._changed.notify_all()

    def _channel(self):
        node = self._node_getter()
        if node is None:
            raise GatewayError('collision_controller_unavailable', 'Collision controller is not initialized',
                               kind='unavailable', retryable=True)
        with self._setup_lock:
            if self._publisher is None or self._channel_node is not node:
                from std_msgs.msg import String
                if self._channel_node is not None:
                    self._channel_node.destroy_publisher(self._publisher)
                    self._channel_node.destroy_subscription(self._subscription)
                with self._changed:
                    self._state = None
                    self._received_at = 0.0
                self._publisher = node.create_publisher(String, '/zeroerr/collision_monitor/config', 10)
                self._subscription = node.create_subscription(
                    String, '/zeroerr/collision_monitor/config_state', self._observe, 10)
                self._channel_node = node
        deadline = time.monotonic() + self._discovery_timeout
        while self._publisher.get_subscription_count() < 1 and time.monotonic() < deadline:
            time.sleep(0.02)
        if self._publisher.get_subscription_count() < 1:
            raise GatewayError('collision_config_subscriber_unavailable',
                               'No collision controller is subscribed to configuration updates',
                               kind='unavailable', retryable=True,
                               details={'topic': '/zeroerr/collision_monitor/config'})
        return self._publisher

    def observed(self):
        if self._node_getter() is None:
            return None
        try:
            self._channel()
        except GatewayError:
            return None
        with self._changed:
            if self._state is None or time.monotonic() - self._received_at > self._state_max_age:
                return None
            return dict(self._state)

    def read(self):
        self._channel()
        deadline = time.monotonic() + self._confirmation_timeout
        with self._changed:
            while True:
                if self._state is not None and time.monotonic() - self._received_at <= self._state_max_age:
                    return dict(self._state)
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                self._changed.wait(remaining)
        raise GatewayError('collision_config_state_unavailable', 'No fresh collision controller configuration was received',
                           kind='timeout', retryable=True, details={'timeout_s': self._confirmation_timeout})

    def publish(self, payload):
        from std_msgs.msg import String
        if not self._command_lock.acquire(timeout=self._confirmation_timeout):
            raise GatewayError('collision_config_busy', 'Another collision configuration command is awaiting confirmation',
                               kind='conflict', retryable=True)
        try:
            publisher = self._channel()
            request_id = uuid4().hex
            message = String()
            message.data = json.dumps({**payload, '_request_id': request_id}, allow_nan=False)
            publisher.publish(message)
            deadline = time.monotonic() + self._confirmation_timeout
            with self._changed:
                while True:
                    state = self._state
                    if (state is not None and state.get('_request_id') == request_id
                            and all(state.get(key) == value for key, value in payload.items())):
                        return dict(state)
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        break
                    self._changed.wait(remaining)
            raise GatewayError('collision_config_confirmation_timeout',
                               'Collision configuration was sent, but the controller did not confirm the matching request',
                               kind='timeout', details={'command_id': request_id, 'timeout_s': self._confirmation_timeout},
                               outcome_unknown=True)
        finally:
            self._command_lock.release()

    def apply(self, payload):
        self.publish(payload)
        return None

    def trigger(self, service_name, timeout_s=3.0):
        from std_srvs.srv import Trigger
        node = self._node_getter()
        if node is None:
            raise GatewayError('runtime_unavailable', 'Robot runtime is not initialized', kind='unavailable', retryable=True)
        client = node.create_client(Trigger, service_name)
        try:
            if not client.wait_for_service(timeout_sec=timeout_s):
                raise GatewayError('service_unavailable', f'ROS service is unavailable: {service_name}',
                                   kind='unavailable', retryable=True, details={'service': service_name})
            future = client.call_async(Trigger.Request())
            completed = threading.Event()
            future.add_done_callback(lambda _: completed.set())
            if not completed.wait(timeout_s):
                raise GatewayError('service_confirmation_timeout', f'ROS service did not confirm: {service_name}',
                                   kind='timeout', outcome_unknown=True,
                                   details={'service': service_name, 'timeout_s': timeout_s})
            result = future.result()
            if result is None:
                raise GatewayError('empty_service_response', f'ROS service returned no response: {service_name}',
                                   details={'service': service_name}, outcome_unknown=True)
            return {'success': bool(result.success), 'message': str(result.message)}
        finally:
            node.destroy_client(client)
