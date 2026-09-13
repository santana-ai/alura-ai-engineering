# Langfuse local (Docker), pra rodar `04_tracing.ipynb`

`docker-compose.yml` copiado da tag `v3.130.0` do [repositório oficial do Langfuse](https://github.com/langfuse/langfuse),
pra não depender de clonar o repo inteiro à parte.

```bash
cp .env.example .env
# preencha ENCRYPTION_KEY/NEXTAUTH_SECRET/SALT (openssl rand -hex 32) e as chaves LANGFUSE_INIT_PROJECT_*
docker compose up -d          # UI em http://localhost:3000 depois de uns 2-3 min
```

As variáveis `LANGFUSE_INIT_*` provisionam org, projeto e usuário na subida, sem passar pela tela de
cadastro da UI. Depois de subir, copie as mesmas chaves (`LANGFUSE_INIT_PROJECT_PUBLIC_KEY`/
`LANGFUSE_INIT_PROJECT_SECRET_KEY`) pro `.env` da raiz da aula (`ai_engineering/aula-05-bonus/.env`), como
`LANGFUSE_PUBLIC_KEY`/`LANGFUSE_SECRET_KEY`, com `LANGFUSE_HOST=http://localhost:3000`.

Pra derrubar: `docker compose down` (ou `docker compose down -v` pra apagar os dados também).

Trocar pra Langfuse Cloud é só apontar `LANGFUSE_HOST` pra `https://us.cloud.langfuse.com` (ou o host EU) e
usar as chaves de um projeto de lá; o código de `04_tracing.ipynb` não muda.
