---
description: Analyze infrastructure specifications and server configurations from Knowledge Graph
argument-hint: [environment_or_component] (optional - defaults to all infrastructure)
allowed-tools: Bash
---

# Infrastructure Analysis from Knowledge Graph

Read the Knowledge Graph from `/mnt/c/Users/Javie/.knowledge_graph/graph.json` and analyze all infrastructure-related information, focusing on the "infra" entity and all server specifications including localhost.

## Query Context:
${ARGUMENTS ? `Specific focus: **$ARGUMENTS**` : `**All infrastructure components and specifications**`}

## Analysis Process:
1. **Read Graph**: Use `cat /mnt/c/Users/Javie/.knowledge_graph/graph.json` to load the Knowledge Graph
2. **Find Infrastructure Node**: Locate the "infra" entity with all its specifications
3. **Search Related Components**: Find server, localhost, deployment, environment entities
4. **Map Dependencies**: Understand how infrastructure components connect
5. **Comprehensive Analysis**: Examine all observations and relationships

## Focus Areas:
- **Server Configurations**: Hardware specs, OS details, installed software
- **Network Architecture**: IP addresses, ports, networking configurations  
- **Deployment Environments**: Development, staging, production setups
- **Local Infrastructure**: Localhost specifications and development environment
- **Resource Allocation**: CPU, memory, storage configurations
- **Service Dependencies**: How infrastructure components connect and depend on each other
- **Security Configurations**: Firewall rules, access controls, certificates
- **Monitoring Setup**: Observability tools and health check configurations

## Output Format:
1. **Infrastructure Overview**: High-level summary of all infrastructure components
2. **Server Inventory**: Detailed specifications for each server/environment
3. **Network Topology**: How systems connect and communicate
4. **Environment Configurations**: Environment-specific settings and differences
5. **Local Development Setup**: Localhost and development environment details
6. **Optimization Opportunities**: Recommendations for infrastructure improvements
7. **Security Posture**: Current security configurations and potential vulnerabilities
8. **Capacity Analysis**: Current resource usage and scaling considerations

Start by reading the Knowledge Graph file with `cat /mnt/c/Users/Javie/.knowledge_graph/graph.json` and then analyzing it for infrastructure components.
