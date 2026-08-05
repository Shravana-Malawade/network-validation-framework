# Network Validation Framework

## Project Overview

The Network Validation Framework is a modular Python-based automation framework developed to validate networking functionality on Embedded Linux devices. The framework performs layer-wise network validation, automates test execution through SSH, generates validation reports, and is designed for CI/CD integration using Jenkins.

The framework is designed to support different Linux-based devices with minimal configuration changes. Version 1.0 focuses on Ethernet-based validation using Raspberry Pi as the initial Device Under Test (DUT), while keeping the framework scalable for future platforms and networking technologies.

---

## Objectives

The primary objectives of this framework are:

- Validate networking functionality across different OSI layers.
- Automate repetitive network validation tasks.
- Reduce manual testing effort.
- Generate detailed validation reports.
- Support Embedded Linux devices.
- Integrate with Jenkins for continuous testing.
- Build a reusable, configurable, and scalable validation framework.

---

## Key Features

- Layer-wise Network Validation
- SSH-based Test Execution
- Configuration-driven Framework
- Automated Logging
- HTML, CSV and JSON Reports
- Jenkins Integration
- Modular Python Design
- Easy addition of new validation modules

---

## Supported Platform

### Current Version

- Raspberry Pi 3
- Embedded Linux
- Ethernet Network

### Future Support

- Wi-Fi
- USB Ethernet
- VLAN
- IPv6
- Multiple DUT Support

---

## Technology Stack

- Python
- Linux (WSL)
- Raspberry Pi OS
- SSH
- Git
- GitHub
- Jenkins
- YAML
- TCP/IP Networking

---

## Current Status

Project initialization completed.

Current development focuses on building the framework architecture and implementing networking validation modules.

---

## Project Structure

```
network-validation-framework
│
├── config
├── core
├── docs
├── logs
├── reports
├── sample_configs
├── scripts
├── tests
├── utils
└── validation
```

---

## Future Enhancements

- Layer 1 Validation
- Layer 2 Validation
- Layer 3 Validation
- Layer 4 Validation
- Application Layer Validation
- Performance Testing
- Stress Testing
- Packet Capture Analysis
- Jenkins Dashboard
- Email Notification
- Web Dashboard
## Layer 2 Validation

- Initial Layer 2 validation implementation.
---

## Author

Shravana Malawade
Embedded Software Trainee
