from django.conf import settings
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse
from django.views.generic.base import View
from django.views.generic.detail import SingleObjectMixin, DetailView
from django.views.generic.edit import FormMixin
from django.http import HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect

from products.models import Variation
from orders.forms import GuestCheckoutForm
from .mixins import CartOrderMixin
from orders.models import UserCheckout, Order, UserAddress

from .models import Cart, CartItem

import braintree

if settings.DEBUG:
    braintree.Configuration.configure(
        braintree.Environment.Sandbox,
        merchant_id=settings.BRAINTREE_MERCHANT_ID,
        public_key=settings.BRAINTREE_PUBLIC,
        private_key=settings.BRAINTREE_PRIVATE,
    )


class ItemCountView(View):

    def get(self, *args, **kwargs):
        if self.request.is_ajax():
            cart_id = self.request.session.get("cart_id")
            if cart_id == None:
                count = 0
            else:
                cart = Cart.objects.get(id=cart_id)
                count = cart.items.count()
            self.request.session["cart_item_count"] = count
            return JsonResponse({"count": count})
        else:
            raise Http404


class CartView(View):
    model = Cart
    template_name = "carts/view.html"

    def get_object(self, *args, **kwargs):
        self.request.session.set_expiry(0)
        cart_id = self.request.session.get("cart_id")
        if cart_id is None:
            cart = Cart()
            cart.save()
            cart_id = cart.id
            self.request.session["cart_id"] = cart_id
        cart = Cart.objects.get(id=cart_id)
        if self.request.user.is_authenticated():
            cart.user = self.request.user
            cart.save()
        return cart

    def get(self, *args, **kwargs):
        cart = self.get_object()
        item_id = self.request.GET.get("item")
        delete_item = self.request.GET.get("delete", False)
        item_added = False
        if item_id:
            item_instance = get_object_or_404(Variation, id=item_id)
            qty = self.request.GET.get("qty", 1)
            try:
                if int(qty) < 1:
                    delete_item = True
            except:
                raise Http404
            cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item_instance)
            if created:
                flash_message = "Item successfully added"
                item_added = True
            if delete_item:
                flash_message = "Item successfully removed"
                cart_item.delete()
            else:
                flash_message = "Item successfully updated"
                cart_item.quantity = qty
                cart_item.save()
            if not self.request.is_ajax():
                return HttpResponseRedirect(reverse("cart"))
        if self.request.is_ajax():
            try:
                total = cart_item.line_item_total
            except:
                total = None
            try:
                subtotal = cart_item.cart.subtotal
            except:
                subtotal = None
            try:
                tax_total = cart_item.cart.tax_total
            except:
                tax_total = None
            try:
                total = cart_item.cart.total
            except:
                total = None
            try:
                total_items = cart_item.cart.items.count()
            except:
                total_items = 0
            data = {
                    "deleted": delete_item,
                    "item_added": item_added,
                    "line_total": total,
                    "subtotal": subtotal,
                    "tax_total": tax_total,
                    "cart_total": total,
                    "flash_message": flash_message,
                    "total_items": total_items
            }
            return JsonResponse(data)

        context = {
            "object": cart
        }
        template = self.template_name
        return render(self.request, template, context)


class CheckoutView(CartOrderMixin, FormMixin, DetailView):
    model = Cart
    template_name = "carts/checkout_view.html"
    form_class = GuestCheckoutForm

    def get_object(self, *args, **kwargs):
        cart = self.get_cart()
        if cart is None:
            return None
        return cart

    def get_context_data(self, *args, **kwargs):
        context = super(CheckoutView, self).get_context_data(*args, **kwargs)
        user_can_continue = False
        user_check_id = self.request.session.get("user_checkout_id")
        if self.request.user.is_authenticated():
            user_can_continue = True
            user_checkout, created = UserCheckout.objects.get_or_create(email=self.request.user.email)       
            user_checkout.user = self.request.user
            user_checkout.save()
            context["client_token"] = user_checkout.get_client_token()
            self.request.session["user_checkout_id"] = user_checkout.id
        elif not self.request.user.is_authenticated() and user_check_id == None:
            context["login_form"] = AuthenticationForm()
            context["next_url"] = self.request.build_absolute_uri()
        else:
            pass
        if user_check_id != None:
            user_can_continue = True
            if self.request.user.is_authenticated():
                user_checkout_2 = UserCheckout.objects.get(id=user_check_id)
                context["client_token"] = user_checkout_2.get_client_token()
        context["order"] = self.get_order()
        context["user_can_continue"] = user_can_continue
        context["form"] = self.get_form()
        return context

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            email = form.cleaned_data.get("email")
            user_checkout, created = UserCheckout.objects.get_or_create(email=email)
            self.request.session["user_checkout_id"] = user_checkout.id
            return self.form_valid(form)
        return self.form_invalid(form)

    def get_success_url(self):
        return reverse("checkout")

    def get(self, *args, **kwargs):
        get_data = super(CheckoutView, self).get(*args, **kwargs)
        cart = self.get_object()
        if cart == None:
            return redirect("cart")
        new_order = self.get_order()
        user_checkout_id = self.request.session.get("user_checkout_id")
        if user_checkout_id != None:
            user_checkout = UserCheckout.objects.get(id=user_checkout_id)
            if new_order.billing_address == None or new_order.shipping_address == None:
                return redirect("order_address")

            new_order.user = user_checkout
            new_order.save()
        return get_data


class CheckoutFinalView(CartOrderMixin, View):

    def post(self, *args, **kwargs):
        order = self.get_order()
        order_total = order.order_total
        nonce = self.request.POST.get("payment_method_nonce")
        if nonce:
            result = braintree.Transaction.sale({
                "amount": order_total,
                "payment_method_nonce": nonce,
                "billing": {
                    "postal_code": "{0}".format(order.billing_address.zipcode)
                },
                "options": {
                    "submit_for_settlement": True
                }
            })
            if result.is_success:
                order.order_id = result.transaction.id
                order.mark_completed(order_id=result.transaction.id)
                messages.success(self.request, "Thank you for your oder.")
                del self.request.session["cart_id"]
                del self.request.session["order_id"]
            else:
                messages.error(self.request, "{0}".format(result.message))
                return redirect("checkout")
        return redirect("order_detail", pk=order.pk)

    def get(self, *args, **kwargs):
        return redirect("checkout")
