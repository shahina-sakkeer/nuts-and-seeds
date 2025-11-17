function updateCartCount(newCount) {
    document.getElementById('cart-count').textContent = newCount;
}

// AJAX request example
function addToCart(productId) {
    fetch('/cart/add/$productId', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
        body: JSON.stringify({ product_id: productId })
    })
    .then(response => response.json())
    .then(data => {
        updateCartCount(data.cart_item_count);
    });
}
