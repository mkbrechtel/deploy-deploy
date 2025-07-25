# deploy_deploy

Main role for deploy-deploy system that sets up deployment infrastructure.

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