# Pubfiles

Plataforma web para gerenciamento, publicação e leitura de revistas digitais com autenticação por email, catálogo, leitor page-by-page, comentários, avaliações e sistema de assinaturas.

## Recursos

- **Auth**: registro com verificação de email (link https), login com Remember Me, reset de senha, **reCAPTCHA v2** em login/registro/reset (fail-closed, pulado sem chaves)
- **Email transacional**: fila em background (`ThreadPoolExecutor`, retry com backoff, logs com endereços mascarados)
- **Anúncios**: slots por posição (cards, laterais, preview, footer) + **popunder global** (script da rede, antes do `</head>`, um por página); assinantes premium não veem anúncios; contagem de cliques
- **SEO**: redirect 301 apex→www, sitemap, robots, canonical, hreflang, JSON-LD `WebSite`, H1 único por página, `noindex` em páginas transacionais/leitor
- **i18n**: pt-br, en, es (django-modeltranslation + traduções Django)

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
| HTTP client | requests (verificação reCAPTCHA) |

## Desenvolvimento local

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Deploy em produção (VPS)

Pré-requisitos: Docker e Docker Compose instalados na VPS, e um reverse proxy (ex.: Traefik) configurado para rotear o domínio para o contêiner do projeto.

```bash
git clone <repo>
cd <repo>
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
│   ├── accounts/       # Auth, registro, perfil, reCAPTCHA
│   ├── advertisements/ # Anúncios (slots + popunder global)
│   ├── categories/     # Categorias MPTT
│   ├── publications/   # Catálogo, leitor, comentários, ratings
│   ├── subscriptions/  # Stripe
│   └── website/        # Config visual do site
├── core/               # settings, urls, email, wsgi, asgi
├── static/             # CSS, JS, imagens
├── templates/          # Templates Django
├── nginx/              # Dockerfile + nginx.conf
├── Dockerfile
├── docker-compose.yml
├── wait-for-database.sh
├── .github/workflows/  # CI/CD
└── .env.example        # Template de variáveis
```

## Testes

Django `TestCase` em `apps/<nome>/tests.py` — **um app por vez** (rodar vários juntos falha no discovery):

```bash
venv/bin/python manage.py test apps.publications
venv/bin/python manage.py test apps.accounts
```

## Variáveis de ambiente

Copie `.env.example` para `.env` e preencha (o `.env` nunca é commitado):

| Variável | Descrição |
|---|---|
| `COMPOSE_PROJECT_NAME` | Nome do projeto para Docker |
| `DOMAIN` | Domínio do site (ex.: `pubfiles.exemplo.com.br`) |
| `SECRET_KEY` | Chave secreta Django |
| `POSTGRES_DB` | Nome do banco |
| `POSTGRES_USER` | Usuário do banco |
| `POSTGRES_PASSWORD` | Senha do banco |
| `POSTGRES_HOST` | Host do banco (padrão: `db`) |
| `POSTGRES_PORT` | Porta do banco (padrão: `5432`) |
| `DJANGO_ALLOWED_HOSTS` | Hosts permitidos (separados por vírgula) |
| `EMAIL_HOST` / `EMAIL_PORT` / ... | Config SMTP (Gmail exige App Password) |
| `EMAIL_MAX_WORKERS` / `EMAIL_MAX_RETRIES` / `EMAIL_RETRY_DELAY` | Ajuste da fila de email (defaults: 2/2/1.0) |
| `RECAPTCHA_SITE_KEY` / `RECAPTCHA_SECRET_KEY` / `RECAPTCHA_TIMEOUT` | chaves reCAPTCHA v2 (sem chaves, verificação pulada) |
| `STRIPE_SECRET_KEY` / ... | Credenciais Stripe |
