from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from orders.models import Order
from .models import Cart


class LoginRequiredMixin:
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


class CartOrderMixin:

    def get_order(self, *args, **kwargs):
        cart = self.get_cart()
        if cart is None:
            return None
        new_order_id = self.request.session.get("order_id")
        if new_order_id is None:
            new_order = Order.objects.create(cart=cart)
            self.request.session["order_id"] = new_order.id
        else:
            new_order = Order.objects.get(id=new_order_id)
        return new_order

    def get_cart(self, *args, **kwargs):
        cart_id = self.request.session.get("cart_id")
        if cart_id is None:
            return None
        cart = Cart.objects.get(id=cart_id)
        if cart.items.count() == 0:
            return None
        return cart
