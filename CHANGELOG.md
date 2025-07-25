# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-07-25

### Added
- Core `deploy` wrapper script with systemd journal integration
- Comprehensive systemd unit support (system and user level)
  - Service units for deployment execution
  - Timer units for scheduled deployments (minutely, hourly, daily, nightly, weekly, thursdays)
  - Path units for file-triggered deployments
  - Target unit for grouping deployments
- Multiple deployment strategies:
  - `ansible_play`: Direct Ansible playbook execution
  - `ansible_pull`: Git-based pull deployment
  - `triggered_by_git_hook`: Git hook integration
  - `webhook_server`: HTTP webhook trigger support
- Email notification support for deployment status
- Instance name validation with character and length constraints
- Proper handling of keyboard interrupts and exit codes
- Support for deployment environment variables and initialization scripts
- Test roles for validation (`test_ohai`, `test_fail`)
- Documentation for Ansible file search paths and project structure

### Changed
- Improved systemd exit detection using CODE_FUNC field
- Enhanced deploy.py logging to show all messages from unit start
- Refactored systemd units from templates to static files

### Fixed
- Deploy script execution and path handling
- Systemd journal message parsing for malformed JSON
- Exit code display only on failure