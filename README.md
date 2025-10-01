# vTeam: Ambient Agentic Runner

> Kubernetes-native AI automation platform for intelligent agentic sessions with multi-agent collaboration

## Overview

**vTeam** is an AI automation platform that combines Claude Code CLI with multi-agent collaboration capabilities. The platform enables teams to create and manage intelligent agentic sessions through a modern web interface.

### Key Capabilities

- **Intelligent Agentic Sessions**: AI-powered automation for analysis, research, content creation, and development tasks
- **Multi-Agent Workflows**: Specialized AI agents model realistic software team dynamics
- **Kubernetes Native**: Built with Custom Resources, Operators, and proper RBAC for enterprise deployment
- **Real-time Monitoring**: Live status updates and job execution tracking

## Architecture

The platform consists of containerized microservices orchestrated via Kubernetes:

| Component | Technology | Description |
|-----------|------------|-------------|
| **Frontend** | NextJS + Shadcn | User interface for managing agentic sessions |
| **Backend API** | Go + Gin | REST API for managing Kubernetes Custom Resources (multi-tenant: projects, sessions, access control) |
| **Agentic Operator** | Go | Kubernetes operator that watches CRs and creates Jobs |
| **Claude Code Runner** | Python + Claude Code CLI | Pod that executes AI with multi-agent collaboration capabilities |

### Agentic Session Flow

1. **Create Session**: User creates agentic session via web UI with task description
2. **API Processing**: Backend creates `AgenticSession` Custom Resource in Kubernetes
3. **Job Scheduling**: Operator detects CR and creates Kubernetes Job with runner pod
4. **AI Execution**: Pod runs Claude Code CLI with multi-agent collaboration for intelligent analysis
5. **Result Storage**: Analysis results stored back in Custom Resource status
6. **UI Updates**: Frontend displays real-time progress and completed results

## Prerequisites

### Required Tools
- **OpenShift Local (CRC)** for local development or OpenShift cluster for production
- **oc** (OpenShift CLI) or **kubectl** v1.28+ configured to access your cluster  
- **Docker or Podman** for building container images
- **Container registry access** (Docker Hub, Quay.io, ECR, etc.) for production
- **Go 1.24+** for building backend services (if building from source)
- **Node.js 20+** and **npm** for the frontend (if building from source)

### Required API Keys
- **Anthropic API Key** - Get from [Anthropic Console](https://console.anthropic.com/)
  - Configure via web UI: Settings → Runner Secrets after deployment

## Quick Start

### Local Development (Recommended for Getting Started)

**🎉 Complete local development environment with full operator integration:**

```bash
# 1. Install prerequisites
brew install crc  # Get pull secret from console.redhat.com/openshift/create/local

# 2. Start complete environment (backend + frontend + operator)
make dev-start

# 3. Verify all components working (24/24 tests)
make dev-test
```

**What you get:**
- ✅ Full vTeam platform running locally in CRC
- ✅ Create and test AgenticSessions end-to-end
- ✅ Operator managing job execution and status updates
- ✅ Real backend API connections (no more connection errors!)
- ✅ Hot-reloading development mode available

See [Local Development Guide](components/scripts/local-dev/README.md) for details.

### 1. Deploy to Production OpenShift

Deploy using the default images from `quay.io/ambient_code`:

```bash
# Deploy to ambient-code namespace (default)
make deploy

# Or deploy to custom namespace
make deploy NAMESPACE=my-namespace
```

### 2. Verify Deployment

```bash
# Check pod status
oc get pods -n ambient-code

# Check services and routes
oc get services,routes -n ambient-code
```

### 3. Access the Web Interface

```bash
# Get the route URL
oc get route frontend-route -n ambient-code

# Or use port forwarding as fallback
kubectl port-forward svc/frontend-service 3000:3000 -n ambient-code
```

### 4. Configure API Keys

1. Access the web interface
2. Navigate to Settings → Runner Secrets
3. Add your Anthropic API key

## Usage

### Creating an Agentic Session

1. **Access Web Interface**: Navigate to your deployed route URL
2. **Create New Session**:
   - **Prompt**: Task description (e.g., "Review this codebase for security vulnerabilities and suggest improvements")
   - **Model**: Choose AI model (Claude Sonnet/Haiku)
   - **Settings**: Adjust temperature, token limits, timeout (default: 300s)
3. **Monitor Progress**: View real-time status updates and execution logs
4. **Review Results**: Download analysis results and structured output

### Example Use Cases

- **Code Analysis**: Security reviews, code quality assessments, architecture analysis
- **Technical Documentation**: API documentation, user guides, technical specifications
- **Project Planning**: Feature specifications, implementation plans, task breakdowns
- **Research & Analysis**: Technology research, competitive analysis, requirement gathering
- **Development Workflows**: Code reviews, testing strategies, deployment planning

## Advanced Configuration

### Building Custom Images

To build and deploy your own container images:

```bash
# Set your container registry
export REGISTRY="quay.io/your-username"

# Build all images
make build-all

# Push to registry (requires authentication)
make push-all REGISTRY=$REGISTRY

# Deploy with custom images
cd components/manifests
REGISTRY=$REGISTRY ./deploy.sh
```

### Container Engine Options

```bash
# Use Podman instead of Docker
make build-all CONTAINER_ENGINE=podman

# Build for specific platform
# Default is linux/amd64
make build-all PLATFORM=linux/arm64

# Build with additional flags
make build-all BUILD_FLAGS="--no-cache --pull"
```

### OpenShift OAuth Integration

For cluster-based authentication and authorization:

```bash
# Enable OAuth integration during deployment
cd components/manifests
ENABLE_OAUTH=true ./deploy.sh
```

See [docs/OPENSHIFT_OAUTH.md](docs/OPENSHIFT_OAUTH.md) for detailed OAuth configuration.

## Configuration & Secrets

### Session Timeout Configuration

Sessions have a configurable timeout (default: 300 seconds):

- **Environment Variable**: Set `TIMEOUT=1800` for 30-minute sessions
- **CRD Default**: Modify `components/manifests/crds/agenticsessions-crd.yaml`
- **Interactive Mode**: Set `interactive: true` for unlimited chat-based sessions

### Runner Secrets Management

Configure AI API keys and integrations via the web interface:

- **Settings → Runner Secrets**: Add Anthropic API keys
- **Project-scoped**: Each project namespace has isolated secret management
- **Security**: All secrets stored as Kubernetes Secrets with proper RBAC

## Troubleshooting

### Common Issues

**Pods Not Starting:**
```bash
oc describe pod <pod-name> -n ambient-code
oc logs <pod-name> -n ambient-code
```

**API Connection Issues:**
```bash
oc get endpoints -n ambient-code
oc exec -it <pod-name> -- curl http://backend-service:8080/health
```

**Job Failures:**
```bash
oc get jobs -n ambient-code
oc describe job <job-name> -n ambient-code
oc logs <failed-pod-name> -n ambient-code
```

### Verification Commands

```bash
# Check all resources
oc get all -l app=ambient-code -n ambient-code

# View recent events
oc get events --sort-by='.lastTimestamp' -n ambient-code

# Test frontend access
curl -f http://localhost:3000 || echo "Frontend not accessible"

# Test backend API
kubectl port-forward svc/backend-service 8080:8080 -n ambient-code &
curl http://localhost:8080/health
```

## Production Considerations

### Security
- **API Key Management**: Store Anthropic API keys securely in Kubernetes secrets
- **RBAC**: Configure appropriate role-based access controls
- **Network Policies**: Implement network isolation between components
- **Image Scanning**: Scan container images for vulnerabilities before deployment

### Monitoring
- **Prometheus Metrics**: Configure metrics collection for all components
- **Log Aggregation**: Set up centralized logging (ELK, Loki, etc.)
- **Alerting**: Configure alerts for pod failures, resource exhaustion
- **Health Checks**: Implement comprehensive health endpoints

### Scaling
- **Horizontal Pod Autoscaling**: Configure HPA based on CPU/memory usage
- **Resource Limits**: Set appropriate resource requests and limits
- **Node Affinity**: Configure pod placement for optimal resource usage

## Development

### Local Development with OpenShift Local (CRC)

**Single Command Setup:**
```bash
# Start complete local development environment
make dev-start
```

**What this provides:**
- ✅ Full OpenShift cluster with CRC
- ✅ Real OpenShift authentication and RBAC  
- ✅ Production-like environment
- ✅ Automatic image builds and deployments
- ✅ Working frontend-backend integration

**Prerequisites:**
```bash
# Install CRC (macOS)
brew install crc

# Get Red Hat pull secret (free):
# 1. Visit: https://console.redhat.com/openshift/create/local
# 2. Download pull secret to ~/.crc/pull-secret.json
# 3. Run: crc setup

# Then start development
make dev-start
```

**Hot Reloading (optional):**
```bash
# Terminal 1: Start with development images
DEV_MODE=true make dev-start

# Terminal 2: Enable file sync for hot-reloading
make dev-sync
```

**Access URLs:**
- Frontend: `https://vteam-frontend-vteam-dev.apps-crc.testing`
- Backend: `https://vteam-backend-vteam-dev.apps-crc.testing/health`
- Console: `https://console-openshift-console.apps-crc.testing`

### Building from Source
```bash
# Build all images locally
make build-all

# Build specific components
make build-frontend
make build-backend
make build-operator
make build-runner
```

## File Structure

```
vTeam/
├── components/                     # 🚀 Ambient Agentic Runner Platform
│   ├── frontend/                   # NextJS web interface
│   ├── backend/                    # Go API service
│   ├── operator/                   # Kubernetes operator
│   ├── runners/                   # AI runner services
│   │   └── claude-code-runner/    # Python Claude Code CLI service
│   └── manifests/                  # Kubernetes deployment manifests
├── docs/                           # Documentation
│   ├── OPENSHIFT_DEPLOY.md        # Detailed deployment guide
│   └── OPENSHIFT_OAUTH.md         # OAuth configuration
├── tools/                          # Supporting development tools
│   ├── vteam_shared_configs/       # Team configuration management
│   └── mcp_client_integration/     # MCP client library
└── Makefile                        # Build and deployment automation
```

## Production Considerations

### Security
- **RBAC**: Comprehensive role-based access controls
- **Network Policies**: Component isolation and secure communication
- **Secret Management**: Kubernetes-native secret storage with encryption
- **Image Scanning**: Vulnerability scanning for all container images

### Monitoring & Observability
- **Health Checks**: Comprehensive health endpoints for all services
- **Metrics**: Prometheus-compatible metrics collection
- **Logging**: Structured logging with OpenShift logging integration
- **Alerting**: Integration with OpenShift monitoring and alerting

### Scaling & Performance
- **Horizontal Pod Autoscaling**: Auto-scaling based on CPU/memory metrics
- **Resource Management**: Proper requests/limits for optimal resource usage
- **Job Queuing**: Intelligent job scheduling and resource allocation
- **Multi-tenancy**: Project-based isolation with shared infrastructure

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following the existing patterns
4. Add tests if applicable
5. Commit with conventional commit messages
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Support & Documentation

- **Deployment Guide**: [docs/OPENSHIFT_DEPLOY.md](docs/OPENSHIFT_DEPLOY.md)
- **OAuth Setup**: [docs/OPENSHIFT_OAUTH.md](docs/OPENSHIFT_OAUTH.md)
- **Architecture Details**: [diagrams/](diagrams/)
- **API Documentation**: Available in web interface after deployment

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
