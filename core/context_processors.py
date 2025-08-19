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
    user_favorites_ids = []
    favorites_count = 0
    
    if request.user.is_authenticated:
        try:
            from products.models import Favorite
            favorites_qs = Favorite.objects.filter(user=request.user).select_related('product')
            user_favorites = list(favorites_qs)
            user_favorites_ids = [fav.product.id for fav in user_favorites]
            favorites_count = len(user_favorites)
        except:
            user_favorites = []
            user_favorites_ids = []
            favorites_count = 0

    return {
        "notif_latest": latest,
        "notif_unread_count": unread_count,
        "cart_count": cart_count,
        "user_favorites": user_favorites,
        "user_favorites_ids": user_favorites_ids,
        "favorites_count": favorites_count,
    }