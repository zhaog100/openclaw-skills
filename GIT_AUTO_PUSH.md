# Git Auto-Push Retry System

This system provides automatic retry mechanisms for git pushes with exponential backoff, error handling, and comprehensive logging.

## Features

- 🔄 **Exponential Backoff**: Automatically retries failed pushes with increasing delays
- 📝 **Comprehensive Logging**: Detailed logs of all attempts and results
- 🛡️ **Error Handling**: Graceful handling of common git push errors
- 🔧 **Multiple Scripts**: Choose from simple to advanced retry mechanisms
- ⚙️ **Configurable**: Adjustable retry counts, delays, and behavior

## Scripts

### 1. `git-push-retry` (Simple)
A lightweight wrapper for basic git push retry.

**Usage:**
```bash
./git-push-retry          # Default: 3 retries, 2s delay
./git-push-retry 5        # 5 retries, 2s delay
./git-push-retry 5 5      # 5 retries, 5s delay
```

**Features:**
- Simple retry loop
- Color-coded output
- Easy to integrate into scripts

### 2. `git-auto-push-enhanced.sh` (Advanced)
A comprehensive auto-commit and push system with detailed logging.

**Usage:**
```bash
./git-auto-push-enhanced.sh    # Full auto-commit and push
./git-auto-push-enhanced.sh 3  # Custom max retries and initial delay
```

**Features:**
- Automatic staging and committing
- Exponential backoff retry logic
- Comprehensive status checking
- Detailed logging with timestamps
- Error recovery and reporting

### 3. `git-auto-push.sh` (Legacy)
The original script for reference.

## Installation

1. Copy the scripts to your project root:
   ```bash
   cp git-auto-push*.sh git-push-retry /path/to/your/repo/
   ```

2. Make them executable:
   ```bash
   chmod +x git-auto-push*.sh git-push-retry
   ```

3. Add to your PATH or use directly:
   ```bash
   ./git-push-retry
   ```

## Git Hooks Integration

### Pre-push Hook (Recommended)

Create `.git/hooks/pre-push`:
```bash
#!/bin/bash

# Auto-retry on push failure
./git-push-retry 3 2
exit $?
```

Make it executable:
```bash
chmod +x .git/hooks/pre-push
```

### Post-commit Hook

Create `.git/hooks/post-commit`:
```bash
#!/bin/bash

# Auto-push after commit if changes exist
if [[ -n $(git status --porcelain) ]]; then
    ./git-auto-push-enhanced.sh
fi
```

## Configuration

### Environment Variables

You can customize behavior using environment variables:

```bash
export GIT_MAX_RETRIES=5
export GIT_INITIAL_DELAY=2
export GIT_MAX_DELAY=60
export GIT_REMOTE="origin"
```

Then modify the scripts to read these values.

### Script Parameters

All scripts support command-line parameters:

- `git-push-retry [max_retries] [delay]`
- `git-auto-push-enhanced.sh [max_retries] [initial_delay]`

## Usage Examples

### Basic Retry
```bash
# Simple retry with defaults
./git-push-retry

# Custom retry settings
./git-push-retry 5 3
```

### Automated Workflow
```bash
# Auto-commit and push everything
./git-auto-push-enhanced.sh

# Just push existing commits with retry
./git-push-retry 4
```

### Integration with CI/CD
```bash
# In your deployment script
./git-auto-push-enhanced.sh || {
    echo "Failed to push after multiple attempts"
    exit 1
}
```

## Error Handling

The system handles common git push errors:

- **Network connectivity issues**: Automatic retry with backoff
- **Authentication failures**: Immediate failure (no point retrying auth errors)
- **Remote repository not found**: Clear error message
- **Branch conflicts**: User must resolve manually
- **Rate limiting**: Exponential backoff helps avoid this

## Logging

Logs are written to stdout with color coding:

- 🟢 **Green**: Success messages
- 🔵 **Blue**: Information messages
- 🟡 **Yellow**: Warnings
- 🔴 **Red**: Errors

## Best Practices

1. **Use pre-push hooks** for critical repositories
2. **Test scripts** in a safe environment first
3. **Monitor logs** to understand retry patterns
4. **Adjust timeouts** based on your network conditions
5. **Keep scripts updated** when upgrading the system

## Troubleshooting

### Common Issues

1. **Permission denied**: Run `chmod +x` on the scripts
2. **Not a git repo**: Run from within a git repository
3. **No remote configured**: Set up git remote first
4. **Authentication issues**: Check SSH keys or token permissions

### Debug Mode

Run with debug output:
```bash
bash -x ./git-auto-push-enhanced.sh
```

## Contributing

To add features or fix bugs:

1. Test changes locally
2. Update documentation
3. Ensure backward compatibility
4. Submit pull request with clear description

## License

MIT License - See individual files for details.