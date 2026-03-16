# Synapse Admin Portal
This service is the internal control plane for Synapse.

## Deployment
This service is deployed as a standalone Cloud Run container.

## API
- `GET /api/tenants`: List all tenants.
- `POST /api/tenants`: Provision a new tenant.
- `DELETE /api/tenants/{id}`: Decommission a tenant.
