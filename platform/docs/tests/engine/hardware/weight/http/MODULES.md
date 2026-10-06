# Module reference: `tests/engine/hardware/weight/http`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_http_transport.py](#test_http_transportpy)
- [test_http_weight_cell_factory.py](#test_http_weight_cell_factorypy)

## `__init__.py`

Source: [tests/engine/hardware/weight/http/__init__.py](../../../../../../tests/engine/hardware/weight/http/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_http_transport.py`

Source: [tests/engine/hardware/weight/http/test_http_transport.py](../../../../../../tests/engine/hardware/weight/http/test_http_transport.py).

Imports (including optional/function-local imports; not a startup dependency list): `requests.exceptions`, `src.engine.hardware.weight.config`, `src.engine.hardware.weight.http.http_cell_transport`, `src.engine.hardware.weight.http.http_weight_cell_factory`, `src.engine.hardware.weight.weight_cell_service`, `unittest`, `unittest.mock`.

### `_calib`

```python
def _calib()
```

### `_meas`

```python
def _meas()
```

### `_cell`

```python
def _cell(cid=0, url='http://192.168.1.100/weight1')
```

### `_cells`

```python
def _cells(*ids)
```

### `_mock_response`

```python
def _mock_response(json_data, status_code=200)
```

### `_mock_error_response`

```python
def _mock_error_response()
```

### `TestHttpCellTransportInit`

```python
class TestHttpCellTransportInit(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_base_url_strips_trailing_slash(self)
```

```python
def test_timeout_from_config(self)
```

```python
def test_initially_disconnected(self)
```

### `TestHttpCellTransportConnect`

```python
class TestHttpCellTransportConnect(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@patch('src.engine.hardware.weight.http.http_cell_transport._requests')
def test_connect_success(self, mock_req)
```

```python
@patch('src.engine.hardware.weight.http.http_cell_transport._requests')
def test_connect_http_error_returns_false(self, mock_req)
```

```python
@patch('src.engine.hardware.weight.http.http_cell_transport._requests')
def test_connect_connection_error_returns_false(self, mock_req)
```

```python
@patch('src.engine.hardware.weight.http.http_cell_transport._requests')
def test_connect_calls_base_url(self, mock_req)
```

```python
@patch('src.engine.hardware.weight.http.http_cell_transport._requests')
def test_disconnect_sets_not_connected(self, mock_req)
```

```python
def test_disconnect_without_connect_no_raise(self)
```

### `TestHttpCellTransportReadWeight`

```python
class TestHttpCellTransportReadWeight(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@patch('src.engine.hardware.weight.http.http_cell_transport._requests')
def test_read_raw_float(self, mock_req)
```

```python
@patch('src.engine.hardware.weight.http.http_cell_transport._requests')
def test_read_raw_int(self, mock_req)
```

```python
@patch('src.engine.hardware.weight.http.http_cell_transport._requests')
def test_read_dict_weight_key(self, mock_req)
```

```python
@patch('src.engine.hardware.weight.http.http_cell_transport._requests')
def test_read_dict_value_key(self, mock_req)
```

```python
@patch('src.engine.hardware.weight.http.http_cell_transport._requests')
def test_read_dict_weight_key_takes_priority(self, mock_req)
```

```python
@patch('src.engine.hardware.weight.http.http_cell_transport._requests')
def test_read_unexpected_format_raises(self, mock_req)
```

```python
@patch('src.engine.hardware.weight.http.http_cell_transport._requests')
def test_read_uses_base_url(self, mock_req)
```

```python
@patch('src.engine.hardware.weight.http.http_cell_transport._requests')
def test_read_http_error_propagates(self, mock_req)
```

### `TestHttpCellTransportCalibration`

```python
class TestHttpCellTransportCalibration(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@patch('src.engine.hardware.weight.http.http_cell_transport._requests')
def test_tare_calls_tare_endpoint(self, mock_req)
```

```python
@patch('src.engine.hardware.weight.http.http_cell_transport._requests')
def test_tare_success_returns_true(self, mock_req)
```

```python
@patch('src.engine.hardware.weight.http.http_cell_transport._requests')
def test_tare_http_error_returns_false(self, mock_req)
```

```python
def test_get_config_returns_local_calibration(self)
```

No HTTP call — returns local calibration from config.

```python
@patch('src.engine.hardware.weight.http.http_cell_transport._requests')
def test_update_offset_calls_correct_endpoint(self, mock_req)
```

```python
@patch('src.engine.hardware.weight.http.http_cell_transport._requests')
def test_update_scale_calls_correct_endpoint(self, mock_req)
```

```python
@patch('src.engine.hardware.weight.http.http_cell_transport._requests')
def test_update_config_calls_correct_endpoint(self, mock_req)
```

```python
@patch('src.engine.hardware.weight.http.http_cell_transport._requests')
def test_update_config_success_returns_true(self, mock_req)
```

```python
@patch('src.engine.hardware.weight.http.http_cell_transport._requests')
def test_update_config_http_error_returns_false(self, mock_req)
```

```python
@patch('src.engine.hardware.weight.http.http_cell_transport._requests')
def test_update_offset_http_error_returns_false(self, mock_req)
```

```python
@patch('src.engine.hardware.weight.http.http_cell_transport._requests')
def test_update_scale_http_error_returns_false(self, mock_req)
```

### `TestBuildHttpWeightCellService`

```python
class TestBuildHttpWeightCellService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_returns_weight_cell_service(self)
```

```python
def test_creates_one_context_per_cell(self)
```

```python
def test_transport_is_http_cell_transport(self)
```

```python
def test_calibrator_is_http_cell_transport(self)
```

Same HttpCellTransport instance implements both ICellTransport and ICellCalibrator.

```python
def test_transport_and_calibrator_same_instance(self)
```

```python
def test_empty_cells_creates_no_contexts(self)
```

```python
def test_cell_url_correctly_assigned(self)
```

```python
def test_cell_timeout_correctly_assigned(self)
```

## `test_http_weight_cell_factory.py`

Source: [tests/engine/hardware/weight/http/test_http_weight_cell_factory.py](../../../../../../tests/engine/hardware/weight/http/test_http_weight_cell_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.weight.config`, `src.engine.hardware.weight.http.http_cell_transport`, `src.engine.hardware.weight.http.http_weight_cell_factory`, `src.engine.hardware.weight.weight_cell_service`, `unittest`, `unittest.mock`.

### `_calib`

```python
def _calib()
```

### `_meas`

```python
def _meas()
```

### `_cell`

```python
def _cell(cid, url=None)
```

### `_cells`

```python
def _cells(*ids)
```

### `TestBuildHttpWeightCellServiceType`

```python
class TestBuildHttpWeightCellServiceType(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_returns_weight_cell_service(self)
```

```python
def test_creates_one_context_per_cell(self)
```

```python
def test_empty_cells_creates_no_contexts(self)
```

### `TestBuildHttpWeightCellServiceTransport`

```python
class TestBuildHttpWeightCellServiceTransport(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_transport_is_http_cell_transport(self)
```

```python
def test_calibrator_is_http_cell_transport(self)
```

```python
def test_transport_and_calibrator_same_instance(self)
```

HttpCellTransport implements both interfaces — must be same object.

```python
def test_each_cell_gets_own_transport(self)
```

```python
def test_cell_url_assigned(self)
```

```python
def test_cell_timeout_assigned(self)
```

```python
def test_multiple_cells_urls_independent(self)
```

### `TestBuildHttpWeightCellServiceMessaging`

```python
class TestBuildHttpWeightCellServiceMessaging(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_messaging_service_passed(self)
```
