def compute_total_price(offers, required_quantity):
    quantity_so_far = 0
    total_price = 0
    required_quantity = float(required_quantity)
    for offer in offers:
        current_price = offer["price"]
        current_quantity = offer["amount"]
        if quantity_so_far <= required_quantity:
            if current_quantity > required_quantity - quantity_so_far:
                total_price += (required_quantity - quantity_so_far) * current_price
                break
            else:
                total_price += current_quantity * current_price
                quantity_so_far += current_quantity
    return total_price
