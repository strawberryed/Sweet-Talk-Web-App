from django.shortcuts import render
from datetime import datetime, timedelta
import random

def confirmation_view(request):
    """View to display order confirmation details."""
    # Example data (replace with actual order data)
    item_name = "Milk Tea"
    total_price = 8.50  # Example total price
    queue_number = random.randint(1, 100)  # Generate a random queue number
    order_time = datetime.now()
    estimated_pickup_time = order_time + timedelta(minutes=15)  # Estimated pickup time is 15 minutes after order time

    context = {
        'item_name': item_name,
        'total_price': total_price,
        'queue_number': queue_number,
        'order_time': order_time.strftime('%Y-%m-%d %H:%M:%S'),
        'estimated_pickup_time': estimated_pickup_time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    
    return render(request, 'confirmation.html', context)
