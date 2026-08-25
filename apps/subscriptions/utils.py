from apps.subscriptions.models import Subscription


def has_premium_access(user) -> bool:
    # verifica se usuário tem acesso total a conteúdo premium
    if not user or not user.is_authenticated:
        return False
    # superuser tem acesso total sem assinatura
    if user.is_superuser:
        return True
    # membros do grupo Administrador (case-sensitive, hardcode) têm acesso total
    if user.groups.filter(name="Administrador").exists():
        return True
    return Subscription.objects.is_active_for(user)
