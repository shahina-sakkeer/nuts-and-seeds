from user_app.models import Orders
from django.db.models import Sum
from datetime import date,timedelta
from user_app.models import OrderItem


def get_sales_data(start,end):
    qs=Orders.objects.filter(created_at__date__range=[start,end])
    sales=qs.aggregate(total=Sum('total_price'))['total'] or 0
    discount=qs.aggregate(total=Sum('discount'))['total'] or 0
    net=sales-discount
    count=qs.count()

    return{
        "sales":sales,
        "discount":discount,
        "net":net,
        "count":count
    }


def get_most_ordered_product(start, end):

    items = (
        OrderItem.objects
        .filter(order__created_at__date__range=[start, end])
        .values('product__product__name')
        .annotate(total_qty=Sum('quantity'))
        .order_by('-total_qty')
    )

    if not items:
        return None

    top_quantity = items[0]['total_qty']
    top_products = [i['product__product__name'] for i in items if i['total_qty'] == top_quantity]

    return {
        "products": top_products,
        "quantity": top_quantity,
    }