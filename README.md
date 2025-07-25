# Deploy deploy!

WIP: currently in early development

**Deploy deploy!** provides deployment infrastructure for running scripts with systemd in a controlled way. It supports shell scripts, Ansible playbooks, Terraform projects, and other deployment tools.

This **Ansible Collection** installs the necessary infrastructure - systemd units, wrapper scripts, and management tools - to execute your deployment scripts reliably. It provides different ways to trigger deployments, including webhooks and git hooks, enabling simple GitOps workflows. 


## Getting started
*Deploy deploy!* has two modes of operation:

- User mode: deployment runs in the scope of a systemd user session. It can be used for local development and deployment workflows for a singe user.
- System mode: deployment runs in the scope of the system. It can be used for deployment workflows for a whole system.

### Installation

### User mode
WIP

### System mode
TODO
