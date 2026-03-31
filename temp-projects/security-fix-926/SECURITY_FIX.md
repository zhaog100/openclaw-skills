# Security Fix: Unsafe Deserialization in Mint Cache

## Issue Information
- **Issue**: #926
- **Repository**: nutshell
- **Severity**: HIGH
- **Type**: Unsafe Deserialization
- **CWE**: CWE-502 (Deserialization of Untrusted Data)

## Vulnerability Description

The Mint Cache component uses unsafe deserialization (pickle) on untrusted data, which can lead to remote code execution (RCE).

### Vulnerable Code Pattern

```python
# VULNERABLE - DO NOT USE
import pickle

def load_cache(file_path):
    with open(file_path, 'rb') as f:
        return pickle.load(f)  # UNSAFE!
```

**Risk**: Attackers can craft malicious pickle payloads that execute arbitrary code during deserialization.

## Proposed Fix

### Solution 1: Use JSON Instead of Pickle (Recommended)

```python
# SAFE - Use JSON
import json
from typing import Any, Dict

def save_cache(data: Dict[str, Any], file_path: str) -> None:
    """Save cache data safely using JSON"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except (IOError, TypeError, ValueError) as e:
        logger.error(f"Failed to save cache: {e}")
        raise CacheError(f"Cache save failed: {e}")

def load_cache(file_path: str) -> Dict[str, Any]:
    """Load cache data safely using JSON"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Validate structure
        if not isinstance(data, dict):
            raise ValueError("Cache data must be a dictionary")

        return data
    except FileNotFoundError:
        logger.info(f"Cache file not found: {file_path}, creating new cache")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in cache file: {e}")
        # Backup corrupted file
        backup_path = f"{file_path}.corrupted"
        shutil.copy(file_path, backup_path)
        logger.info(f"Corrupted cache backed up to: {backup_path}")
        return {}
    except Exception as e:
        logger.error(f"Failed to load cache: {e}")
        raise CacheError(f"Cache load failed: {e}")
```

### Solution 2: Secure Pickle with Allowed Classes (If JSON is not possible)

```python
# SAFER - Restricted unpickling
import pickle
import io
from typing import Any

class RestrictedUnpickler(pickle.Unpickler):
    """Unpickler that only allows safe built-in types"""

    SAFE_CLASSES = {
        'builtins': {'dict', 'list', 'tuple', 'str', 'int', 'float', 'bool', 'NoneType'},
        'collections': {'OrderedDict', 'defaultdict'},
    }

    def find_class(self, module: str, name: str) -> Any:
        """Only allow whitelisted classes"""
        if module in self.SAFE_CLASSES:
            if name in self.SAFE_CLASSES[module]:
                return super().find_class(module, name)

        # Block everything else
        raise pickle.UnpicklingError(
            f"Blocked unsafe deserialization: {module}.{name}"
        )

def safe_load_cache(file_path: str) -> Any:
    """Load pickle data with restricted unpickler"""
    try:
        with open(file_path, 'rb') as f:
            return RestrictedUnpickler(f).load()
    except pickle.UnpicklingError as e:
        logger.error(f"Unsafe pickle data blocked: {e}")
        raise SecurityError(f"Unsafe deserialization attempt: {e}")
    except Exception as e:
        logger.error(f"Failed to load cache: {e}")
        raise CacheError(f"Cache load failed: {e}")
```

### Solution 3: MessagePack (Alternative to JSON)

```python
# ALTERNATIVE - MessagePack (more efficient than JSON)
import msgpack
from typing import Any, Dict

def save_cache_msgpack(data: Dict[str, Any], file_path: str) -> None:
    """Save cache using MessagePack (binary, efficient)"""
    try:
        with open(file_path, 'wb') as f:
            packed = msgpack.packb(data, use_bin_type=True)
            f.write(packed)
    except Exception as e:
        logger.error(f"Failed to save cache: {e}")
        raise CacheError(f"Cache save failed: {e}")

def load_cache_msgpack(file_path: str) -> Dict[str, Any]:
    """Load cache using MessagePack"""
    try:
        with open(file_path, 'rb') as f:
            data = msgpack.unpackb(f.read(), raw=False)

        if not isinstance(data, dict):
            raise ValueError("Cache data must be a dictionary")

        return data
    except FileNotFoundError:
        return {}
    except Exception as e:
        logger.error(f"Failed to load cache: {e}")
        raise CacheError(f"Cache load failed: {e}")
```

## Implementation Steps

### Step 1: Identify All Pickle Usage

```bash
# Find all pickle usage
grep -r "pickle.load" --include="*.py" .
grep -r "pickle.loads" --include="*.py" .
grep -r "import pickle" --include="*.py" .
```

### Step 2: Replace with Safe Alternative

```python
# Before
import pickle

def load_data(path):
    with open(path, 'rb') as f:
        return pickle.load(f)

# After
import json

def load_data(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)
```

### Step 3: Add Validation

```python
from pydantic import BaseModel, ValidationError
from typing import Dict, Any

class CacheData(BaseModel):
    """Schema for cache data validation"""
    version: str
    timestamp: float
    data: Dict[str, Any]

def load_validated_cache(file_path: str) -> CacheData:
    """Load and validate cache data"""
    raw_data = load_cache(file_path)  # Using safe JSON loader

    try:
        validated = CacheData(**raw_data)
        return validated
    except ValidationError as e:
        logger.error(f"Cache data validation failed: {e}")
        raise CacheError(f"Invalid cache structure: {e}")
```

### Step 4: Migration Script

```python
import os
import pickle
import json
from pathlib import Path

def migrate_pickle_to_json(pickle_path: str, json_path: str) -> None:
    """Migrate existing pickle cache to JSON format"""
    logger.info(f"Migrating {pickle_path} to JSON format")

    # Load old pickle data (TRUSTED SOURCE ONLY)
    with open(pickle_path, 'rb') as f:
        data = pickle.load(f)

    # Save as JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Backup old pickle file
    backup_path = f"{pickle_path}.backup"
    os.rename(pickle_path, backup_path)
    logger.info(f"Old pickle file backed up to: {backup_path}")
```

## Testing

### Unit Tests

```python
import pytest
import json
import tempfile
from pathlib import Path

def test_safe_json_cache():
    """Test safe JSON cache operations"""
    test_data = {
        'version': '1.0',
        'timestamp': 1234567890.0,
        'data': {'key': 'value'}
    }

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json_path = f.name

    try:
        # Save
        save_cache(test_data, json_path)

        # Load
        loaded = load_cache(json_path)
        assert loaded == test_data
    finally:
        Path(json_path).unlink()

def test_malicious_pickle_blocked():
    """Test that malicious pickle data is blocked"""
    # Craft malicious pickle payload (for testing)
    import pickle
    import io

    class Malicious:
        def __reduce__(self):
            return (eval, ("__import__('os').system('echo HACKED')",))

    payload = pickle.dumps(Malicious())

    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pkl') as f:
        f.write(payload)
        pkl_path = f.name

    try:
        # Should raise SecurityError
        with pytest.raises(SecurityError):
            safe_load_cache(pkl_path)
    finally:
        Path(pkl_path).unlink()
```

## Security Impact

### Before Fix
- ❌ Unsafe deserialization
- ❌ Remote Code Execution possible
- ❌ CWE-502 vulnerability

### After Fix
- ✅ Safe deserialization (JSON/MessagePack)
- ✅ Input validation
- ✅ No arbitrary code execution
- ✅ Secure by default

## References

- CWE-502: https://cwe.mitre.org/data/definitions/502.html
- OWASP Deserialization Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html
- Python pickle security: https://docs.python.org/3/library/pickle.html

---

**Status**: Fix ready for implementation
**Priority**: HIGH
**Breaking Change**: Yes (requires cache migration)
