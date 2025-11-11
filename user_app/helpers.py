from django.utils import timezone
from admin_app.models import ProductOffer,CategoryOffer

def get_offer_price(variant):
    now=timezone.now()
    highest_discount=0

    product=variant.product
    original_price=variant.price

    product_offer=ProductOffer.objects.filter(product=product,start_date__lt=now,
                    end_date__gt=now,is_active=True).first()
    
    if product_offer:
        highest_discount=product_offer.offer_percentage

    category_offer=CategoryOffer.objects.filter(category=product.category,
                    start_date__lt=now, end_date__gt=now,is_active=True).first()
    
    if category_offer:
        if category_offer.offer_percentage > highest_discount:
            highest_discount=category_offer.offer_percentage

    if highest_discount > 0:
        discount_amount=(original_price*highest_discount)/100
        final_price=original_price-discount_amount
        discount_percent=highest_discount

    else:
        final_price=original_price
        discount_percent=highest_discount

    return final_price,discount_percent



