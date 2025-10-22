# Copilot Instructions for send-to-influx

## Project Overview
send-to-influx is a Python application that collects data from various smart home and energy monitoring devices and sends them to InfluxDB for time-series monitoring and visualization. The project is designed with a modular architecture that makes it easy to add new data sources.

## Architecture

### Main Application (`sendtoinflux.py`)
- **Entry Point**: Command-line script with signal handling for graceful shutdown
- **Source Selection**: Supports multiple data sources via `--source` parameter
- **CLI Modes**: 
  - `--dump`: One-time data export (JSON format)
  - `--print`: Continuous monitoring with JSON output to console
  - Normal mode: Continuous data collection and transmission to InfluxDB
- **Timing**: Uses interval-based timing system to avoid drift

### Modular Data Sources (`toinflux/` package)
The project uses a plugin-like architecture where each data source is implemented as a separate module:

#### Base Classes (`toinflux/general.py`)
- **`Settings`**: Manages YAML configuration file loading and validation
- **`DataHandler`**: Base class for all data source implementations
- **`get_class()`**: Factory function to instantiate data source classes dynamically

#### Current Data Sources
- **`toinflux/philipshue.py`**: Philips Hue Bridge integration
- **`toinflux/myenergi.py`**: MyEnergi Zappi/Eddi/Harvi devices integration

### Configuration (`settings.yml`)
YAML-based configuration supporting multiple data sources:
- **Hue**: Bridge connection, sensor mappings, temperature units
- **MyEnergi**: API endpoints, authentication, device serials
- **Zappi**: Field selection, collection intervals
- **InfluxDB**: Connection details, database settings

## Code Style & Standards

### Python Style
- **Line Length**: 120 characters (Black formatter)
- **Type Hints**: Use where appropriate for function parameters and return types
- **Docstrings**: Comprehensive docstrings with parameter and return type documentation
- **Naming**: Meaningful variable and function names following PEP 8
- **Complexity**: Maximum complexity of 10 (flake8 configuration)

### Error Handling
- **Exit Codes**:
  - `0`: Normal exit
  - `1`: Configuration errors (missing/invalid settings.yml)
  - `2`: Connection errors (API endpoints, InfluxDB)
- **Error Messages**: Descriptive messages printed to stderr
- **Network Handling**: Proper timeout handling and connection failure management
- **Validation**: Configuration validation before processing

### Testing Requirements
- **Framework**: pytest with mock support
- **Coverage**: Unit tests for all functions with mocked external dependencies
- **Fixtures**: Use pytest fixtures for common setup
- **Scenarios**: Test both success and error conditions
- **External Dependencies**: Mock Hue API, MyEnergi API, InfluxDB, HTTP requests

## Development Guidelines

### Adding New Data Sources
1. **Create Module**: Add new file in `toinflux/` directory (e.g., `toinflux/newsource.py`)
2. **Implement Class**: Create class inheriting from `general.DataHandler`
3. **Required Methods**:
   - `get_data()`: Return processed data as dictionary
   - `send_data(data)`: Send data to InfluxDB (inherited from base class)
4. **Configuration**: Add corresponding section to `settings.yml`
5. **Testing**: Create comprehensive unit tests
6. **Documentation**: Update docstrings and comments

### Data Source Implementation Pattern
```python
class NewSource(general.DataHandler):
    """Child class of general.DataHandler for new data source"""
    
    def get_data(self):
        """
        Get and process data from the new source
        
        :return: Processed data dictionary
        :rtype: dict
        """
        raw_data = self.get_data_from_api()
        return self.parse_data(raw_data)
    
    def get_data_from_api(self):
        """Get raw data from external API"""
        # Implementation here
        pass
    
    def parse_data(self, raw_data):
        """Parse raw data into InfluxDB format"""
        # Implementation here
        pass
```

### Configuration Schema
Each data source should have its own section in `settings.yml`:
```yaml
newsource:
  # API endpoint
  url: "https://api.example.com/endpoint"
  # Authentication
  api_key: "your_api_key"
  # Collection settings
  interval: 300
  timeout: 5
  # Source-specific settings
  fields:
    - "field1"
    - "field2"
```

### Error Handling Patterns
```python
try:
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"Error connecting to API - {e}")
    sys.exit(2)
```

### Testing Patterns
```python
def test_data_source_with_mock(monkeypatch):
    """Test data source with mocked external API"""
    def mock_api_call():
        return {"field1": "value1", "field2": "value2"}
    
    monkeypatch.setattr(module, "external_api_call", mock_api_call)
    handler = NewSource("newsource")
    result = handler.get_data()
    assert result == expected_result
```

## Current Data Sources

### Philips Hue (`toinflux/philipshue.py`)
- **Supported Sensors**:
  - `ZLLTemperature`: Temperature sensors (converted to C/F/K)
  - `ZLLLightLevel`: Light level sensors (converted to lux)
  - `ZLLPresence`: Motion/presence sensors (converted to 0/1)
- **Lights**: Brightness percentage (0-100) or boolean on/off (0/1)
- **Configuration**: Bridge host, username, sensor name mappings, temperature units

### MyEnergi (`toinflux/myenergi.py`)
- **Devices**: Zappi (EV charger), Eddi (water heater), Harvi (energy monitor)
- **Data Types**: Real-time status and historical day/hour data
- **Authentication**: HTTP Digest authentication with serial/API key
- **Configuration**: API endpoints, device serials, field selection

## Dependencies

### Core Dependencies
- `requests~=2.32.3`: HTTP requests for APIs and InfluxDB
- `pyyaml~=6.0.3`: YAML configuration file parsing

### Development Dependencies
- `black~=24.4.2`: Code formatting
- `flake8~=7.1.1`: Linting with bugbear and black plugins
- `flake8-bugbear~=24.10.31`: Additional linting rules
- `flake8-black~=0.3.6`: Black integration for flake8

## CLI Usage
```bash
# Normal operation (send data to InfluxDB)
python sendtoinflux.py --source hue

# One-time data export
python sendtoinflux.py --source zappi --dump

# Continuous monitoring (console output)
python sendtoinflux.py --source hue --print

# Available sources: hue, zappi (and any other implemented sources)
```

## Configuration Examples

### Hue Configuration
```yaml
hue:
  host: "hue.example.com"
  user: "your_hue_user"
  timeout: 5
  interval: 300
  temperature_units: "C"
  sensors:
    "Hue ambient light sensor 1": "Room1_Light_Sensor"
    "Hue temperature sensor 1": "Room1_Temperature_Sensor"
```

### MyEnergi Configuration
```yaml
myenergi:
  zappi_url: "https://s18.myenergi.net/cgi-jstatus-Z"
  dayhour_url: "https://s18.myenergi.net/cgi-jdayhour-Z"
  apikey: "your_api_key"
  timeout: 5

zappi:
  interval: 300
  serial: "your_zappi_serial"
  zappi_fields:
    - "frq"
    - "vol"
    - "gen"
    - "grd"
```

### InfluxDB Configuration
```yaml
influx:
  url: "https://influx.example.com:8086"
  db: "smart_home_db"
  user: "your_influx_user"
  password: "your_influx_password"
  timeout: 5
```

## Data Format
- **InfluxDB Line Protocol**: `measurement,tag=value field=value timestamp`
- **Timestamp Precision**: Seconds
- **Data Types**: Numeric values (integers, floats) for time-series data
- **Field Names**: Sanitized device names (spaces replaced with underscores)

## Performance Considerations
- **Timeouts**: Appropriate timeouts for all network operations (default: 5 seconds)
- **Intervals**: Configurable collection intervals per data source
- **Memory**: Efficient data structures for processing
- **Rate Limiting**: Consider API rate limits when setting intervals
- **Error Recovery**: Graceful handling of temporary network issues

## Security Notes
- **Credentials**: Store sensitive data in `settings.yml` with appropriate file permissions
- **HTTPS**: Use HTTPS for all API connections in production
- **Validation**: Validate all input data before processing
- **Logging**: Avoid logging sensitive information
- **Environment Variables**: Consider using environment variables for sensitive data

## Common Tasks

### Debugging Issues
1. **Configuration**: Use `--dump` mode to inspect raw API data
2. **Processing**: Use `--print` mode to see processed data without sending to InfluxDB
3. **Validation**: Check `settings.yml` syntax and values
4. **Connectivity**: Verify network connectivity to APIs and InfluxDB
5. **Testing**: Use pytest to isolate specific functionality

### Adding New Sensor Types
1. **Identify**: Find sensor type in API response
2. **Process**: Add processing logic in data source's `parse_data()` method
3. **Convert**: Handle unit conversions if needed
4. **Test**: Add test cases for new sensor type
5. **Document**: Update configuration documentation

### Modifying Data Format
1. **Update**: Modify InfluxDB line protocol formatting in `send_data()` method
2. **Compatibility**: Ensure backward compatibility with existing data
3. **Test**: Update tests to reflect new format
4. **Document**: Update configuration and usage documentation

## Testing Strategy
- **Unit Tests**: All functions with mocked dependencies
- **Error Conditions**: Test network failures, invalid configurations, API errors
- **Data Processing**: Test with various sensor types and data formats
- **CLI**: Test argument parsing and signal handling
- **Integration**: Test end-to-end data flow (with mocked external services)

## Development Workflow
1. **Setup**: Copy `example_settings.yml` to `settings.yml` and configure
2. **Development**: Use `--print` mode for testing without affecting InfluxDB
3. **Testing**: Run `pytest` to ensure all tests pass
4. **Linting**: Run `flake8` to check code style
5. **Formatting**: Run `black` to format code
6. **Integration**: Test with actual devices and InfluxDB instance
