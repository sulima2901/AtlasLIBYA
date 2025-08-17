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
    
    # المفضلة للمستخدم المسجل
    user_favorites = []
    if request.user.is_authenticated:
        try:
            from products.models import Favorite
            user_favorites = list(Favorite.objects.filter(
                user=request.user
            ).values_list('product_id', flat=True))
        except:
            user_favorites = []

    return {
        "notif_latest": latest,
        "notif_unread_count": unread_count,
        "cart_count": cart_count,
        "user_favorites": user_favorites
    }