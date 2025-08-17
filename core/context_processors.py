from .models import Notification

def notifications(request):
    try:
        latest = Notification.objects.all()[:5]
        unread_count = Notification.objects.filter(is_read=False).count()
    except Exception:
        latest = []
        unread_count = 0

    cart = request.session.get('cart', {})
    cart_count = sum(cart.values()) if isinstance(cart, dict) else 0

    return {
        "notif_latest": latest,
        "notif_unread_count": unread_count,
        "cart_count": cart_count
    }