# Deploy backend with AWS SAM

## Prerequisites

- AWS account and credentials configured (`aws configure`)
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
- Python 3.11 available locally

## 1) Install backend dependencies

Run from `backend`:

```bash
pip install -r requirements.txt
```

## 2) Build the Lambda package

Run from `backend`:

```bash
sam build --template-file template.yaml
```

## 3) Deploy

Run from `backend`:

```bash
sam deploy --guided --template-file template.yaml
```

When prompted, set:

- `RedisUrl`: your Redis endpoint (ElastiCache/Redis URL), e.g. `redis://my-redis-host:6379/0`
- `OpenAiApiKey`: your OpenAI API key
- `InterpolStateKey`: keep default or choose another key namespace
- Stack name: e.g. `interpol-backend`
- Region: your AWS region
- Allow SAM role creation: `Y`

## 4) Use the deployed API URL

After deploy, SAM prints output `ApiUrl`.

Example health check:

```bash
curl "$API_URL/"
```

## Notes

- Lambda handler is `api.handler` (via Mangum).
- Current WebSocket endpoint (`/ws`) is not fully supported by this HTTP API setup. Keep it for local/docker use, or move realtime to API Gateway WebSocket API if needed.
