from user_app.models import CartItem
from django.db.models import Sum

def cart_item_count(request):
    if request.user.is_authenticated:
        product_count=CartItem.objects.filter(cart__user=request.user).count
    else:
        product_count=0

    return {'cart_item_count':product_count}
