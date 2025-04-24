# AGENT SECURITY POLICY

Purpose: Define security responsibilities and protocols for AI coding agents.

## 1. Security Principles

- Maintain project integrity and confidentiality at all times
- Only use open source, auditable dependencies (see .augment-guidelines.yaml)
- Validate all code and configuration changes for security impact

## 2. Agent Responsibilities

- Monitor for vulnerabilities in dependencies and report via project_memory_graph
- Enforce least-privilege access to data and APIs
- Log and escalate any detected security incident or anomaly

## 3. Vulnerability Handling

- If a vulnerability is found, update SECURITY.md and notify via project_memory_graph
- Reference the affected files, tasks, and planning items

## 4. Sensitive Operations

- Tag all sensitive code regions with # @security-critical
- Ensure tests exist for all security-critical paths (see TESTING.md)

# End of AGENT SECURITY POLICY
