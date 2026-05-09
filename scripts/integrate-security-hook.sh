#!/bin/bash
# Security Hook Integration Script

echo "Setting up Security Hook integration..."

# Make security hook executable
chmod +x /home/zhaog/.openclaw/workspace/scripts/security-hook.sh

# Add to shell profile for automatic loading
PROFILE_FILES=("$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile")

for profile in "${PROFILE_FILES[@]}"; do
    if [ -f "$profile" ]; then
        # Add alias if not already present
        if ! grep -q "alias pre-exec-security-hook" "$profile"; then
            cat >> "$profile" << 'EOF'

# Security Hook Integration
alias pre-exec-security-hook='/home/zhaog/.openclaw/workspace/scripts/security-hook.sh'
export PATH="/home/zhaog/.openclaw/workspace/scripts:$PATH"
EOF
            echo "Added Security Hook alias to $profile"
        fi
    fi
done

# Create cron job for periodic security checks
CRON_JOB="@daily /home/zhaog/.openclaw/workspace/scripts/security-hook.sh --cron"

(crontab -l 2>/dev/null | grep -v "security-hook" ; echo "$CRON_JOB") | crontab -

echo "Security Hook integration complete!"
echo "Run 'source ~/.bashrc' to load the new alias"
echo "Test with: pre-exec-security-hook 'git status'"