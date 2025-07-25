# deploy_deploy

Main role for deploy-deploy system that provides the core deployment infrastructure - installs systemd units, wrapper scripts, and the deploy command to manage deployments.

## Requirements

- Debian-based operating system
- Systemd init system

## Role Variables

See `defaults/main.yaml` for available variables.

## Dependencies

None.

## Example Playbook

```yaml
- hosts: servers
  roles:
     - mkbrechtel.deploy_deploy.deploy_deploy
```

## License

Apache-2.0

## Author Information

This role was created for the mkbrechtel.deploy_deploy collection.