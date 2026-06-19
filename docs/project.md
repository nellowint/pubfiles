# Histórico de Engenharia e Desenvolvimento — Projeto Pubfiles

Este documento consolida todas as manutenções corretivas, evolutivas e refinamentos de interface de usuário (UI/UX) realizados no ecossistema do projeto Django.

## 1. Otimização e Ajustes do Painel Administrativo (Django Jazzmin)

### 1.1. Dimensionamento do Logotipo de Login
* **Problema:** A imagem do logotipo na tela de login do painel administrativo quebrava o layout devido ao tamanho excessivo.
* **Solução:** Injeção de propriedades CSS inline diretamente na chave `login_logo_styles` do dicionário de configuração do Jazzmin para limitar a altura e centralizar o elemento.

### 1.2. Substituição de Texto Residual do Django
* **Problema:** O texto nativo `<span class="brand-text fw-light">Administração do Django</span>` ainda era exibido na barra superior.
* **Solução:** Definição explícita da propriedade `"site_brand": "Painel Admin"` nas configurações do Jazzmin para sobrescrever o comportamento padrão do Django.

### 1.3. Correção de Exibição no Formulário de Usuário (`CustomUserAdmin`)
* **Problema:** Erro de exceção `FieldError` ao tentar renderizar a página de alteração de usuário (`/admin/accounts/user/1/change/`). O campo `date_joined` estava declarado em `fieldsets` dentro de um formulário editável, violando a regra de campos não editáveis do Django.
* **Solução:** O campo foi removido dos `fields` editáveis e as permissões de exibição foram higienizadas utilizando os atributos corretos de herança do `UserAdmin`.

### Configuração Final do Painel (`settings.py` / `admin.py`):

```python
# apps/accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    ordering = ('email',)
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password'),
        }),
    )

    readonly_fields = ('last_login',)

admin.site.register(User, CustomUserAdmin)
```

---

## 2. Implementação de Logotipo e Favicon Dinâmicos

### 2.1. Arquitetura de Fallback para Mídia
* **Demanda:** O sistema precisava carregar o logotipo e o favicon salvos dinamicamente pelo administrador no banco de dados (`WebsiteModel`). Caso nenhum registro existisse, o sistema deveria renderizar de forma segura uma imagem padrão estática (`img/default-logo.png`).
* **Estratégia Adotada:** Criação de um **Context Processor** global para o ecossistema de templates do Django. Isso evita consultas redundantes repetidas dentro das views e disponibiliza as tags de imagem para qualquer arquivo HTML.

### Arquivo do Processador de Contexto (`context_processors.py`):

```python
# apps/website/context_processors.py
from .models import Website

def site_settings(request):
    config = Website.objects.first()

    # Define caminhos seguros caso não existam dados no banco
    favicon_url = config.logo.url if config and config.logo else "img/default-logo.png"
    site_title = config.site_name if config else "Pubfiles"

    return {
        'site_favicon': favicon_url,
        'site_title': site_title,
    }
```

*Nota de Engenharia:* Para ativar o código acima, o caminho do interpretador `'apps.website.context_processors.site_settings'` foi mapeado no array `TEMPLATES > OPTIONS > context_processors` do arquivo `settings.py`.

---

## 3. Correção de Sintaxe no Módulo de Autenticação

### 3.1. Template de Registro (`register.html`)
* **Problema:** O servidor retornava `TemplateSyntaxError` ao tentar acessar a rota `/register/`, acusando tag `if` não fechada na linha 142.
* **Solução:** Correção estrutural na árvore do template, fechando o loop de renderização de campos de formulários com as tags complementares `{% endfor %}` e `{% endif %}`, além da inclusão do gatilho de disparo (botão de submissão do formulário).

---

## 4. Engenharia de Frontend e Animações (UI/UX)

### 4.1. Menu de Navegação Glassmorphism Dinâmico
* **Solução:** O arquivo `base.html` foi estruturado para suportar o tema Claro/Escuro (`data-theme`) persistido via `localStorage` no navegador do cliente. As subcategorias são controladas por injeção de parâmetros na URL via JavaScript autoinvocável.

### 4.2. Efeito Hover Zoom nos Cards da Home
* **Evolução da Demanda:** Inicialmente planejou-se dar zoom apenas na imagem interna. Após testes de experiência do usuário, refinou-se o comportamento para realizar a aproximação tridimensional **do card inteiro**, mantendo a proporção da imagem interna estática.
* **Solução CSS:** Adicionado tratamento com a propriedade `will-change: transform` para forçar a aceleração de hardware pela GPU, prevenindo engasgos na renderização. Foi aplicada uma curva de animação customizada `cubic-bezier(0.165, 0.84, 0.44, 1)` para conferir peso visual sofisticado ao card.

---

## 5. Códigos-Fonte Finais Estruturados

### 5.1. Código Final: `templates/publications/base.html`
```html
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ site_title }} - {% block title %}Home{% endblock %}</title>

    <link class="favicon" rel="icon" type="image/png" href="{{ site_favicon }}">

    <style>
        /* === ARQUITETURA DE CORES DINÂMICAS (CLARO / ESCURO) === */
        :root {
            --primary-color: {{ color_light_primary|default:"#007bff" }};
            --secondary-color: {{ color_light_secondary|default:"#6c757d" }};
            --bg-image: url("{{ site_background }}");
            --nav-bg: rgba(255, 255, 255, 0.25);
            --nav-border: rgba(255, 255, 255, 0.3);
            --dropdown-bg: rgba(255, 255, 255, 0.95);
            --dropdown-text: #333333;
            --card-bg: rgba(255, 255, 255, 0.85);
            --card-border: rgba(255, 255, 255, 0.4);
            --text-color: #333333;
        }

        [data-theme="dark"] {
            --primary-color: {{ color_dark_primary|default:"#121212" }};
            --secondary-color: {{ color_dark_secondary|default:"#1a1a1a" }};
            --nav-bg: rgba(0, 0, 0, 0.4);
            --nav-border: rgba(255, 255, 255, 0.1);
            --dropdown-bg: rgba(26, 26, 26, 0.95);
            --dropdown-text: #f8f9fa;
            --card-bg: rgba(30, 30, 30, 0.85);
            --card-border: rgba(255, 255, 255, 0.1);
            --text-color: #f8f9fa;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }
        html, body { min-height: 100vh; }

        body {
            font-family: Arial, sans-serif;
            color: var(--text-color);
            padding-bottom: 60px;
            background-image: var(--bg-image);
            background-attachment: fixed;
            background-position: center center;
            background-repeat: no-repeat;
            background-size: cover;
            transition: color 0.3s ease;
        }

        a { text-decoration: none; color: inherit; }
        .site-wrapper { max-width: 1300px; margin: 0 auto; padding: 20px; }

        .floating-nav {
            position: sticky;
            top: 20px;
            z-index: 1000;
            background: var(--nav-bg);
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
            border: 1px solid var(--nav-border);
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            margin-bottom: 40px;
        }

        .nav-main-row { display: flex; align-items: center; justify-content: space-between; padding: 15px 25px; }
        .nav-brand { display: flex; align-items: center; gap: 12px; }
        .nav-logo img { width: 50px; height: 50px; object-fit: cover; border-radius: 12px; vertical-align: middle; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .nav-title { font-size: 18px; font-weight: bold; color: #fff; text-shadow: 1px 1px 3px rgba(0,0,0,0.5); white-space: nowrap; }

        .search-form { display: flex; flex: 0 1 500px; margin: 0 20px; }
        .search-input { width: 100%; padding: 12px 18px; border: 1px solid var(--nav-border); background: rgba(255, 255, 255, 0.2); border-radius: 8px; font-size: 14px; outline: none; color: var(--text-color); transition: background 0.2s; }
        .search-input:focus { background: rgba(255, 255, 255, 0.3); }
        .search-input::placeholder { color: var(--text-color); opacity: 0.7; }

        .nav-right-zone { display: flex; align-items: center; gap: 15px; }
        .theme-toggle-btn { background: rgba(255, 255, 255, 0.25); border: 1px solid var(--nav-border); color: var(--text-color); width: 40px; height: 40px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 18px; }
        .btn-premium { background: #ffc107; color: #111; padding: 10px 20px; border-radius: 8px; font-weight: bold; font-size: 14px; box-shadow: 0 4px 10px rgba(255, 193, 7, 0.3); }

        .user-logged-box { display: flex; align-items: center; gap: 12px; }
        .user-avatar { display: flex; align-items: center; gap: 8px; font-weight: bold; font-size: 14px; color: #fff; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); }
        .avatar-icon { width: 35px; height: 35px; background: rgba(255,255,255,0.7); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 18px; border: 2px solid var(--primary-color); color: #333; }
        .btn-logout { background: transparent; color: #fff; border: 1px solid rgba(255,255,255,0.4); padding: 8px 14px; border-radius: 6px; font-size: 12px; font-weight: bold; cursor: pointer; text-shadow: 1px 1px 2px rgba(0,0,0,0.4); transition: background 0.2s, border-color 0.2s; }
        .btn-logout:hover { background: rgba(220, 53, 69, 0.2); border-color: #dc3545; }

        .nav-categories-row { padding: 15px 25px; background: rgba(0, 0, 0, 0.05); border-top: 1px solid var(--nav-border); }
        .categories-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 12px; }
        .category-nav-button { display: block; padding: 10px 14px; font-size: 13px; font-weight: bold; color: #fff; text-shadow: 1px 1px 2px rgba(0,0,0,0.4); border-radius: 6px; background: rgba(255,255,255,0.1); text-align: center; border: 1px solid transparent; transition: background 0.2s, border-color 0.2s; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .category-nav-button:hover, .category-nav-button.active { background: var(--primary-color); border-color: var(--nav-border); }

        .nav-children-row { padding: 12px 25px; background: rgba(0, 0, 0, 0.15); border-top: 1px solid rgba(255, 255, 255, 0.1); border-radius: 0 0 16px 16px; }
        .floating-nav:not(:has(.nav-children-row)) .nav-categories-row { border-radius: 0 0 16px 16px; }
        .children-grid { display: flex; flex-wrap: wrap; gap: 10px; }
        .child-nav-button { display: inline-block; padding: 6px 14px; font-size: 12px; font-weight: bold; color: var(--text-color); background: var(--card-bg); border-radius: 20px; border: 1px solid var(--card-border); transition: background 0.2s, color 0.2s; }
        .child-nav-button:hover, .child-nav-button.active { background: var(--primary-color); color: #fff !important; border-color: transparent; }

        {% block extra_css %}{% endblock %}
    </style>

    <script>
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
    </script>
</head>
<body>
    <div class="site-wrapper">
        <nav class="floating-nav">
            <div class="nav-main-row">
                <a href="{% url 'publications:home' %}" class="nav-brand">
                    <div class="nav-logo">
                        <img src="{{ site_logo }}" alt="{{ site_title }}">
                    </div>
                    <span class="nav-title">{{ site_title }}</span>
                </a>

                <form action="{% url 'publications:home' %}" method="GET" class="search-form">
                    <input type="text" name="q" value="{{ request.GET.q }}" placeholder="Digite para buscar..." class="search-input">
                </form>

                <div class="nav-right-zone">
                    <button class="theme-toggle-btn" id="themeToggle" title="Alternar Tema">🌓</button>
                    {% if request.user.is_authenticated %}
                        <div class="user-logged-box">
                            <div class="user-avatar" title="Logado como {{ request.user.username }}">
                                <div class="avatar-icon">👤</div>
                                <span>{{ request.user.username|truncatechars:10 }}</span>
                            </div>
                            <form action="{% url 'logout' %}" method="POST" style="display: inline;">
                                {% csrf_token %}
                                <button type="submit" class="btn-logout">Sair</button>
                            </form>
                        </div>
                    {% else %}
                        <a href="{% url 'login' %}" class="btn-premium">Seja Premium</a>
                    {% endif %}
                </div>
            </div>

            <div class="nav-categories-row">
                <div class="categories-grid">
                    <a href="{% url 'publications:home' %}" class="category-nav-button {% if not request.GET.category %}active{% endif %}">Todas</a>
                    {% for category in categories %}
                        {% if category.is_root_node %}
                            <a href="{% url 'publications:home' %}?category={{ category.id }}" class="category-nav-button id-pai-{{ category.id }}">
                                {{ category.name }}
                            </a>
                        {% endif %}
                    {% endfor %}
                </div>
            </div>

            {% for category in categories %}
                {% if category.is_root_node and not category.is_leaf_node %}
                    <div class="nav-children-row sub-bloco-pai-{{ category.id }}" style="display: none;">
                        <div class="children-grid">
                            <a href="{% url 'publications:home' %}?category={{ category.id }}" class="child-nav-button id-filha-{{ category.id }}">Ver Tudo de {{ category.name }}</a>
                            {% for child in category.children.all %}
                                <a href="{% url 'publications:home' %}?category={{ child.id }}" class="child-nav-button id-filha-{{ child.id }}">
                                    {{ child.name }}
                                </a>
                            {% endfor %}
                        </div>
                    </div>
                {% endif %}
            {% endfor %}
        </nav>

        <main>
            {% block content %}{% endblock %}
        </main>
    </div>

    <script>
        const themeToggleBtn = document.getElementById('themeToggle');
        themeToggleBtn.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            let newTheme = currentTheme === 'light' ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });

        (function() {
            const urlParams = new URLSearchParams(window.location.search);
            const activeId = urlParams.get('category');

            if (activeId) {
                const activeChildBtn = document.querySelector(`.id-filha-${activeId}`);
                if (activeChildBtn) { activeChildBtn.classList.add('active'); }

                const activeParentBtn = document.querySelector(`.id-pai-${activeId}`);
                const targetSubBlock = document.querySelector(`.sub-bloco-pai-${activeId}`);

                if (activeParentBtn && targetSubBlock) {
                    activeParentBtn.classList.add('active');
                    targetSubBlock.style.display = 'block';
                } else if (activeChildBtn) {
                    const parentContainer = activeChildBtn.closest('.nav-children-row');
                    if (parentContainer) {
                        parentContainer.style.display = 'block';
                        const classMatch = parentContainer.className.match(/sub-bloco-pai-(\d+)/);
                        if (classMatch && classMatch[1]) {
                            const rootParentBtn = document.querySelector(`.id-pai-${classMatch[1]}`);
                            if (rootParentBtn) rootParentBtn.classList.add('active');
                        }
                    }
                }
            }
        })();
    </script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### 5.2. Código Final: `templates/publications/home.html`
```html
{% extends "publications/base.html" %}

{% block title %}Home{% endblock %}

{% block extra_css %}
    /* Estilos exclusivos do Catálogo da Home */
    .carousel-container { position: relative; width: 100%; height: 340px; margin-bottom: 40px; border-radius: 16px; overflow: hidden; box-shadow: 0 8px 25px rgba(0,0,0,0.3); }
    .carousel-slide { display: none; width: 100%; height: 100%; }
    .carousel-slide.active { display: block; animation: fade 0.5s ease-in-out; }
    .carousel-slide img { width: 100%; height: 100%; object-fit: cover; }
    .carousel-btn { position: absolute; top: 50%; transform: translateY(-50%); background: rgba(0,0,0,0.4); color: white; border: none; padding: 12px 16px; font-size: 18px; cursor: pointer; border-radius: 50%; }
    .carousel-btn:hover { background: rgba(0,0,0,0.7); }
    .carousel-prev { left: 20px; }
    .carousel-next { right: 20px; }

    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 25px; }

    /* Estrutura dos Cards com Zoom Avançado no Card Inteiro */
    .card-wrapper { overflow: hidden; border-radius: 12px; }

    .card {
        background: var(--card-bg);
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        text-align: center;
        position: relative;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        backdrop-filter: blur(5px);
        border: 1px solid var(--card-border);
        transition: transform 0.4s cubic-bezier(0.165, 0.84, 0.44, 1), box-shadow 0.4s ease;
        will-change: transform;
    }

    .card:hover {
        transform: scale(1.04);
        box-shadow: 0 20px 40px rgba(0,0,0,0.5);
        z-index: 10;
    }

    .card-img-wrapper { position: relative; width: 100%; height: 260px; border-radius: 8px; overflow: hidden; margin-bottom: 12px; }
    .card-img-wrapper img { width: 100%; height: 100%; object-fit: cover; }

    .badge { position: absolute; top: 10px; right: 10px; background: #ffc107; color: black; padding: 4px 10px; font-size: 11px; font-weight: bold; border-radius: 4px; z-index: 2; }
    .card h3 { font-size: 16px; margin-bottom: 8px; text-align: left; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: var(--text-color); }
    .card .info-row { display: flex; justify-content: space-between; font-size: 12px; color: var(--text-color); opacity: 0.8; font-weight: bold; margin-bottom: 15px; }
    .btn-card { display: block; background: var(--primary-color); color: white; padding: 10px; text-decoration: none; border-radius: 6px; font-size: 14px; font-weight: bold; box-shadow: 0 4px 10px rgba(0,0,0,0.15); }

    .pagination { display: flex; justify-content: center; align-items: center; gap: 10px; margin-top: 40px; padding: 20px 0; }
    .page-link { padding: 10px 15px; border: 1px solid var(--nav-border); background: var(--card-bg); border-radius: 8px; font-size: 14px; font-weight: bold; color: var(--text-color); box-shadow: 0 4px 10px rgba(0,0,0,0.1); backdrop-filter: blur(5px); }
    .page-link.active { background: var(--primary-color); color: white; border-color: var(--primary-color); }

    @keyframes fade { from { opacity: 0.6; } to { opacity: 1; } }
{% endblock %}

{% block content %}
    {% if banners %}
    <div class="carousel-container">
        {% for banner in banners %}
            <div class="carousel-slide {% if forloop.first %}active{% endif %}">
                <img src="{{ banner.image.url }}" alt="Destaque">
            </div>
        {% endfor %}

        {% if banners.count > 1 %}
            <button class="carousel-btn carousel-prev" onclick="changeSlide(-1)">&#10094;</button>
            <button class="carousel-btn carousel-next" onclick="changeSlide(1)">&#10095;</button>
        {% endif %}
    </div>
    {% endif %}

    <div class="grid">
        {% for publication in publications %}
            <div class="card-wrapper">
                <div class="card">
                    <div class="card-img-wrapper">
                        {% if publication.is_members_only %}
                            <span class="badge">PREMIUM</span>
                        {% endif %}
                        {% if publication.cover %}
                            <img src="{{ publication.cover.url }}" alt="{{ publication.title }}">
                        {% endif %}
                    </div>

                    <div>
                        <h3>{{ publication.title }}</h3>
                        <div class="info-row">
                            <span>📁 {{ publication.category.name|default:"Geral" }}</span>
                            <span>👁️ {{ publication.views_count }}</span>
                        </div>
                        <a href="{% url 'publications:detail' publication.slug %}" class="btn-card">Acessar</a>
                    </div>
                </div>
            </div>
        {% empty %}
            <p style="grid-column: 1/-1; text-align: center; padding: 60px; background: var(--card-bg); backdrop-filter: blur(5px); border-radius: 12px; color: var(--text-color); font-weight: bold; border: 1px solid var(--card-border);">
                Nenhuma publicação correspondente foi encontrada.
            </p>
        {% endfor %}
    </div>

    {% if is_paginated %}
    <div class="pagination">
        {% if page_obj.has_previous %}
            <a href="?page=1{% if request.GET.q %}&q={{ request.GET.q }}{% endif %}{% if request.GET.category %}&category={{ request.GET.category }}{% endif %}" class="page-link">&laquo; Primeira</a>
            <a href="?page={{ page_obj.previous_page_number }}{% if request.GET.q %}&q={{ request.GET.q }}{% endif %}{% if request.GET.category %}&category={{ request.GET.category }}{% endif %}" class="page-link">Anterior</a>
        {% endif %}

        <span class="page-link active">{{ page_obj.number }} de {{ page_obj.paginator.num_pages }}</span>

        {% if page_obj.has_next %}
            <a href="?page={{ page_obj.next_page_number }}{% if request.GET.q %}&q={{ request.GET.q }}{% endif %}{% if request.GET.category %}&category={{ request.GET.category }}{% endif %}" class="page-link">Próxima</a>
            <a href="?page={{ page_obj.paginator.num_pages }}{% if request.GET.q %}&q={{ request.GET.q }}{% endif %}{% if request.GET.category %}&category={{ request.GET.category }}{% endif %}" class="page-link">Última &raquo;</a>
        {% endif %}
    </div>
    {% endif %}
{% endblock %}

{% block extra_js %}
<script>
    let currentSlideIndex = 0;
    const slides = document.querySelectorAll('.carousel-slide');

    function showSlide(index) {
        if(slides.length === 0) return;
        slides[currentSlideIndex].classList.remove('active');
        currentSlideIndex = (index + slides.length) % slides.length;
        slides[currentSlideIndex].classList.add('active');
    }

    function changeSlide(direction) { showSlide(currentSlideIndex + direction); }
    if(slides.length > 1) { setInterval(() => { changeSlide(1); }, 6000); }
</script>
{% endblock %}
```

### 5.3. Código Final: `templates/registration/register.html`
```html
{% extends "publications/base.html" %}

{% block title %}Register - {{ site_title }}{% endblock %}

{% block extra_css %}
/* Estilos exclusivos da Tela de Registro */
.register-wrapper { display: flex; justify-content: center; align-items: center; padding: 40px 20px; }
.register-box { max-width: 450px; width: 100%; background: var(--card-bg); padding: 40px 30px; border-radius: 16px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25); backdrop-filter: blur(5px); -webkit-backdrop-filter: blur(5px); border: 1px solid var(--card-border); transition: background 0.3s; }
.register-box h2 { font-size: 24px; margin-bottom: 10px; color: var(--text-color); text-align: center; }
.register-box p { font-size: 14px; color: var(--text-color); opacity: 0.7; margin-bottom: 30px; text-align: center; }

.form-group { margin-bottom: 20px; text-align: left; }
.form-group label { display: block; font-size: 13px; font-weight: bold; margin-bottom: 6px; color: var(--text-color); }
.form-group input { width: 100%; padding: 12px 14px; border: 1px solid var(--nav-border); background: rgba(255, 255, 255, 0.1); border-radius: 8px; font-size: 14px; color: var(--text-color); outline: none; transition: border-color 0.2s; }
.form-group input:focus { border-color: var(--primary-color); }

.helptext { display: block; font-size: 11px; color: var(--text-color); opacity: 0.6; margin-top: 5px; line-height: 1.4; }
.btn-register-submit { width: 100%; background: var(--primary-color); color: white; border: none; padding: 14px; font-size: 15px; font-weight: bold; border-radius: 8px; cursor: pointer; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 10px; transition: background 0.2s, transform 0.1s; }
.btn-register-submit:hover { opacity: 0.9; transform: translateY(-1px); }

.register-footer { margin-top: 25px; padding-top: 20px; border-top: 1px solid var(--nav-border); font-size: 14px; color: var(--text-color); text-align: center; }
.register-footer a { color: var(--text-color); font-weight: bold; text-decoration: underline; }
.errorlist { list-style: none; background: #f8d7da; color: #721c24; padding: 10px 14px; border-radius: 8px; font-size: 13px; font-weight: bold; margin-bottom: 15px; border: 1px solid #f5c6cb; }
{% endblock %}

{% block content %}
<div class="register-wrapper">
    <div class="register-box">
        <h2>Criar Conta</h2>
        <p>Preencha os campos abaixo para se registrar</p>

        <form method="POST" action="{% url 'register' %}">
            {% csrf_token %}

            {% if form.errors %}
                <div class="errorlist">
                    Por favor, corrija os erros abaixo.
                </div>
            {% endif %}

            {% if form %}
                {% for field in form %}
                    <div class="form-group">
                        <label for="{{ field.id_for_label }}">{{ field.label }}</label>
                        {{ field }}
                        {% if field.help_text %}
                            <span class="helptext">{{ field.help_text|safe }}</span>
                        {% endif %}
                        {% if field.errors %}
                            <div style="color: #dc3545; font-size: 12px; margin-top: 5px;">
                                {{ field.errors|striptags }}
                            </div>
                        {% endif %}
                    </div>
                {% endfor %}
            {% endif %}

            <button type="submit" class="btn-register-submit">Registrar</button>
        </form>

        <div class="register-footer">
            Já possui uma conta? <a href="{% url 'login' %}">Faça login aqui</a>
        </div>
    </div>
</div>
{% endblock %}
```

---
*Fim do Relatório Técnico.*
