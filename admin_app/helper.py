from user_app.models import Orders
from django.db.models import Sum,F
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


def get_recent_orders(start,end):
    orders=Orders.objects.filter(created_at__date__range=[start,end]).all().order_by("-created_at")[:5]
    return {"order":orders}



def get_ordered_products(start, end):

    items = (OrderItem.objects.filter(order__created_at__date__range=[start, end]).values('product__product__name')
                    .annotate(total_qty=Sum('quantity'), total_revenue=Sum(F("quantity") * F("price"))).order_by('-total_qty'))

    if not items:
        return None

    total_qty_sum=sum(i['total_qty'] for i in items)
    
    total_qty_sum = sum(item['total_qty'] for item in items)

    circumference = 2 * 3.14159 * 80 
    circumference = 502               

  
    colors = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6"]

    result = []
    offset = 0 

    for index, item in enumerate(items):
        name = item['product__product__name']
        qty = item['total_qty']
        percentage = round((qty / total_qty_sum) * 100, 2)       
        revenue=item['total_revenue']

    
        arc_length = (percentage / 100) * circumference

        result.append({
            "name": name,
            "quantity": qty,
            "percentage": percentage,
            "revenue":revenue,
            "color": colors[index % len(colors)],
            "dasharray": arc_length,
            "dashoffset": -offset,
        })

        offset += arc_length

    return result


def get_ordered_categories(start,end):
    items = (OrderItem.objects.filter(order__created_at__date__range=[start, end]).values('product__product__category__name')
                    .annotate(total_qty=Sum('quantity'), total_revenue=Sum(F("quantity") * F("price"))).order_by('-total_qty'))

    if not items:
        return None

    total_qty_sum=sum(i['total_qty'] for i in items)
    
    total_qty_sum = sum(item['total_qty'] for item in items)

    circumference = 2 * 3.14159 * 80 
    circumference = 502               

  
    colors = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6"]

    result = []
    offset = 0 

    for index, item in enumerate(items):
        name = item['product__product__category__name']
        qty = item['total_qty']
        percentage = round((qty / total_qty_sum) * 100, 2)       
        revenue=item['total_revenue']

    
        arc_length = (percentage / 100) * circumference

        result.append({
            "name": name,
            "quantity": qty,
            "percentage": percentage,
            "revenue":revenue,
            "color": colors[index % len(colors)],
            "dasharray": arc_length,
            "dashoffset": -offset,
        })

        offset += arc_length

    return result


