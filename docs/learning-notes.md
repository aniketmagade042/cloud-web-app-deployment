# Learning Notes: Cloud Services, Security and Deployment

## 1. Core cloud services

| Service | Purpose | AWS | Azure | GCP |
|---|---|---|---|---|
| Compute | Runs your code | EC2, Elastic Beanstalk | Virtual Machines, App Service | Compute Engine, Cloud Run |
| Object storage | Stores files as objects in buckets | S3 | Blob Storage | Cloud Storage |
| Managed database | Provider handles patching, backups, scaling | RDS | Azure SQL / PostgreSQL | Cloud SQL |
| Virtual networking | Private network, subnets, firewalls | VPC, security groups | VNet, NSG | VPC, firewall rules |
| IAM | Who can do what | IAM | Entra ID + RBAC | IAM |
| Monitoring | Metrics, logs, alarms | CloudWatch | Azure Monitor | Cloud Monitoring |

Key ideas:
- **Managed vs self-managed**: a managed database saves effort but costs more and gives less control.
- **Object vs block vs file storage**: object (S3) for files and backups, block (EBS) for VM disks, file (EFS) for shared folders.
- **IAM**: least privilege, roles instead of shared keys, MFA, no root for daily work.
- **Networking**: databases belong in private networks; only the app tier is exposed.

## 2. Secure configuration

- **Environment variables**: configuration outside the code, so the same code runs in dev and production.
- **Secrets**: passwords, API keys, tokens. Never commit them. Use `.env` locally (git-ignored) and a secrets manager or protected env file in the cloud. Rotate them if they leak.
- **Application logging**: structured, leveled messages (INFO/WARNING/ERROR). Log events, never passwords, tokens, or personal data.
- **Resource quotas**: limits per account/region that protect you from runaway usage. Combine with budget alerts.

## 3. Deployment flow

Code -> Compute -> Database/Storage -> Networking -> Live app

1. Write code that reads all settings from environment variables.
2. Provision compute and install the runtime.
3. Provision the managed database and connect through a private rule.
4. Open only the needed ports (80/443 public, 22 from your IP, 5432 from the app only).
5. Verify with `/health`, logs, and a monitoring alarm.
6. Clean up resources.

## Things that confused me
- `<add your own>`

## Self-test
- Why should the database security group allow the app's security group instead of an IP?
- What is the difference between an environment variable and a secret?
- Why does `.env` go in `.gitignore`?
- What does `/health` let a load balancer or monitor do?
