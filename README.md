# Pubfiles

Plataforma web para gerenciamento, publicação e leitura de revistas digitais com autenticação por email, catálogo, leitor page-by-page, comentários, avaliações e sistema de assinaturas.

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.12 + Django 6.0 |
| Banco (dev) | SQLite |
| Banco (prod) | PostgreSQL 15 |
| Cache (prod) | Redis 7 |
| WSGI | Gunicorn |
| Reverse proxy | Nginx + Traefik |
| Container | Docker Compose |
| Admin | Django Jazzmin |
| Categorias | django-mptt |
| i18n | django-modeltranslation (pt-br, en, es) |
| Pagamentos | Stripe (preparado) |

## Desenvolvimento local

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env  # configure DEBUG=1 e DJANGO_SETTINGS_MODULE=core.settings-dev
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Deploy em produção (VPS)

Pré-requisitos na VPS: Docker, Traefik rodando em `reverse-proxy/`, script `scripts/new-project.sh`.

```bash
git clone <repo> ~/projects/pubfiles
bash ~/scripts/new-project.sh pubfiles
cp .env.example .env
# Preencher .env com DOMAIN, SECRET_KEY, POSTGRES_DB, etc
docker compose up -d --build
docker compose exec web python manage.py migrate
```

O deploy é automatizado via GitHub Actions (`.github/workflows/deploy.yml`) no push da branch `main`.

## Estrutura do projeto

```
pubfiles/
├── apps/
│   ├── accounts/       # Auth, registro, perfil
│   ├── categories/     # Categorias MPTT
│   ├── publications/   # Catálogo, leitor, comentários, ratings
│   ├── subscriptions/  # Stripe
│   └── website/        # Config visual do site
├── core/               # settings, urls, wsgi, asgi
├── static/             # CSS, JS, imagens
├── templates/          # Templates Django
├── nginx/              # Dockerfile + nginx.conf
├── Dockerfile
├── docker-compose.yml
├── wait-for-database.sh
├── .github/workflows/  # CI/CD
└── .env.example        # Template de variáveis
```

## Variáveis de ambiente

Copie `.env.example` para `.env` e preencha:

| Variável | Descrição |
|---|---|
| `COMPOSE_PROJECT_NAME` | Nome do projeto para Docker |
| `DOMAIN` | Domínio do site |
| `SECRET_KEY` | Chave secreta Django |
| `POSTGRES_DB` | Nome do banco |
| `POSTGRES_USER` | Usuário do banco |
| `POSTGRES_PASSWORD` | Senha do banco |
| `POSTGRES_HOST` | Host do banco (padrão: `db`) |
| `POSTGRES_PORT` | Porta do banco (padrão: `5432`) |
| `DJANGO_ALLOWED_HOSTS` | Hosts permitidos (separados por vírgula) |
| `EMAIL_HOST` / `EMAIL_PORT` / ... | Config SMTP |
| `STRIPE_SECRET_KEY` / ... | Credenciais Stripe |
