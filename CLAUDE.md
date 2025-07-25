## Ansible Project Structure

### File Organization

Files can be placed in `./files/` at the collection root instead of in individual role directories. Ansible's search path includes the collection's files directory, so roles can reference these files directly without duplication.

For example, `deploy.py` is in `./files/` and can be referenced by any role using:

```yaml
- name: Copy deploy script
  copy:
    src: deploy.py
    dest: /usr/local/bin/deploy
    mode: '0755'
```

## Release Process

To create a new release:

1. Update the version in `galaxy.yml`
2. Update the CHANGELOG.md with release notes
3. Commit all changes with a descriptive message
4. Create an annotated git tag: `git tag -a v0.0.X -m "Release version 0.0.X - Brief description"`
5. Push commits and tag: `git push origin main --tags`

The GitHub Actions workflow will automatically:
- Build the Ansible collection
- Publish to Ansible Galaxy
- Create a GitHub release (if configured)

Requirements for successful Galaxy import:
- All roles must have a `README.md` file
- All roles must have a `meta/main.yml` file with galaxy_info
- The collection must have a valid `galaxy.yml` file