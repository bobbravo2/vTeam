# vTeam Local Development

> **🎉 STATUS: FULLY WORKING** - Complete local development with operator integration

## Quick Start

### 1. Install Prerequisites
```bash
# macOS
brew install crc

# Get Red Hat pull secret (free account):
# 1. Visit: https://console.redhat.com/openshift/create/local  
# 2. Download to ~/.crc/pull-secret.json
# That's it! The script handles crc setup and configuration automatically.
```

### 2. Start Development Environment
```bash
make dev-start
```
*First run: ~5-10 minutes. Subsequent runs: ~2-3 minutes.*

### 3. Access Your Environment
- **Frontend**: https://vteam-frontend-vteam-dev.apps-crc.testing
- **Backend**: https://vteam-backend-vteam-dev.apps-crc.testing/health  
- **Console**: https://console-openshift-console.apps-crc.testing

### 4. Verify Everything Works
```bash
make dev-test  # Should show 24/24 tests passing (includes operator tests)
```

## Hot-Reloading Development

```bash
# Terminal 1: Start with development mode
DEV_MODE=true make dev-start

# Terminal 2: Enable file sync  
make dev-sync
```

## Essential Commands

```bash
# Day-to-day workflow
make dev-start          # Start environment (backend + frontend + operator)
make dev-test           # Run tests (24 tests including operator)
make dev-stop           # Stop (keep CRC running)

# Operator management
make dev-logs-operator     # View operator logs
make dev-restart-operator  # Restart operator deployment
make dev-operator-status   # Check operator status and events

# Troubleshooting
make dev-clean          # Delete project, fresh start
crc status              # Check CRC status
oc get pods -n vteam-dev # Check pod status
```

## Operator Integration

The local development environment now includes the **vTeam operator** that manages AgenticSession workflows:

- ✅ **Fully integrated**: Operator builds and deploys automatically with `make dev-start`
- ✅ **End-to-end testing**: Create AgenticSessions and watch them execute locally
- ✅ **Real backend connections**: Operator connects to local backend service
- ✅ **Complete test coverage**: 12 operator-specific tests (24 total tests)

### Testing AgenticSessions Locally

```bash
# Create a test session
cat <<EOF | oc apply -f -
apiVersion: vteam.ambient-code/v1alpha1
kind: AgenticSession
metadata:
  name: my-test-session
  namespace: vteam-dev
spec:
  prompt: "echo 'Hello from local dev!'"
  timeout: 300
  interactive: false
  llmSettings:
    model: "claude-sonnet-4-20250514"
    temperature: 0.7
    maxTokens: 4096
EOF

# Watch the operator create and manage the job
oc get jobs -n vteam-dev -w

# View session status updates
oc get agenticsession my-test-session -n vteam-dev -o yaml
```

## System Requirements

- **CPU**: 4 cores, **RAM**: 11GB, **Disk**: 50GB (auto-validated)
- **OS**: macOS 10.15+ or Linux with KVM (auto-detected)
- **Internet**: Download access for images (~2GB first time)
- **Network**: No VPN conflicts with CRC networking
- **Reduce if needed**: `CRC_CPUS=2 CRC_MEMORY=6144 make dev-start`

*Note: The script automatically validates resources and provides helpful guidance.*

## Common Issues & Fixes

**CRC won't start:**
```bash
crc stop && crc start
```

**DNS issues:**
```bash
sudo bash -c 'echo "127.0.0.1 api.crc.testing" >> /etc/hosts'
```

**Memory issues:**
```bash
CRC_MEMORY=6144 make dev-start
```

**Complete reset:**
```bash
crc stop && crc delete && make dev-start
```

**Corporate environment issues:**
- **VPN**: Disable during setup if networking fails
- **Proxy**: May need `HTTP_PROXY`/`HTTPS_PROXY` environment variables
- **Firewall**: Ensure CRC downloads aren't blocked

---

**📖 Detailed Guides:**
- [Installation Guide](INSTALLATION.md) - Complete setup instructions
- [Hot-Reload Guide](DEV_MODE.md) - Development mode details  
- [Migration Guide](MIGRATION_GUIDE.md) - Moving from Kind to CRC