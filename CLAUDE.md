## Ansible Project Structure

### File Organization and Search Path

Some files are intentionally placed in `./files/` at the project root rather than in `roles/deploy_deploy/files/`. This is a deliberate design decision based on how Ansible searches for files.

#### Why Files Are in ./files/

1. **Ansible File Search Order**: When using the `copy` or `template` modules with a relative `src` path, Ansible searches in this order:
   - Files in the role's `files/` or `templates/` directory
   - Files in the playbook directory's `files/` or `templates/` directory
   - Files relative to the playbook file itself
   - Files in the collections path

2. **Development Workflow**: By keeping core functionality files like `deploy.py` in the root `./files/` directory:
   - Changes are centralized in one location
   - Development and testing can happen without modifying role internals
   - The files are accessible to both the role and any direct playbook usage

3. **Collections Path Behavior**: When this project is installed as an Ansible collection, Ansible will search the collection's path structure, making these files available to the role without needing to duplicate them.

#### Important Files in ./files/

- `deploy.py` - The main deployment wrapper script (installed as `/usr/local/bin/deploy`)
- Other scripts that need to be globally accessible across the project

**Note**: Do NOT duplicate these files into `roles/deploy_deploy/files/` - Ansible will find them in the project's `./files/` directory when the role references them with relative paths.