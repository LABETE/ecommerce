import random
from django.core.exceptions import ImproperlyConfigured
from django.contrib import messages
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from django_filters import FilterSet, CharFilter, NumberFilter

from .forms import VariationInventoryFormset, ProductFilterForm
from .mixins import StaffRequiredMixin
from .models import Product, Variation, Category


class CategoryListView(ListView):
    model = Category
    queryset = Category.objects.all()
    template_name = "products/product_list.html"


class CategoryDetailView(DetailView):
    model = Category

    def get_context_data(self, *args, **kwargs):
        context = super(CategoryDetailView, self).get_context_data(*args, **kwargs)
        obj = self.get_object()
        product_set = obj.product_set.all()
        default_products = obj.default_category.all()
        products = (product_set | default_products).distinct()
        context["product_list"] = products
        return context


class VariationListView(StaffRequiredMixin, ListView):
    model = Variation
    template_name = "products/variations_list.html"
    queryset = Product.objects.all()

    def get_context_data(self, *args, **kwargs):
        context = super(VariationListView, self).get_context_data(*args, **kwargs)
        context["formset"] = VariationInventoryFormset(queryset=self.get_queryset())
        return context

    def get_queryset(self, *args, **kwargs):
        product_pk = self.kwargs.get("pk")
        if product_pk:
            product = get_object_or_404(Product, pk=product_pk)
            variations = Variation.objects.filter(product=product)
        return variations

    def post(self, *args, **kwargs):
        formset = VariationInventoryFormset(self.request.POST, self.request.FILES)
        if formset.is_valid():
            messages.success(self.request, "Your inventory and pricing has been updated.")
            return redirect("products:list")
        raise Http404


class ProductFilter(FilterSet):
    title = CharFilter(name="title", lookup_type="icontains", distinct=True)
    category = CharFilter(name="categories__title", lookup_type="icontains", distinct=True)
    category_id = CharFilter(name="categories__id", lookup_type="icontains", distinct=True)
    min_price = NumberFilter(name="variation__price", lookup_type="gte", distinct=True)
    max_price = NumberFilter(name="variation__price", lookup_type="lte", distinct=True)
    class Meta:
        model = Product
        fields = [
            "min_price",
            "max_price",
            "category",
            "title",
            "description",
        ]


class FilterMixin:
    filter_class = None
    search_ordering_param = "ordering"

    def get_queryset(self, *args, **kwargs):
        try:
            qs = super(FilterMixin, self).get_queryset(*args, **kwargs)
            return qs
        except:
            raise ImproperlyConfigured("You must have a queryset in order to use the FilterMixin")

    def get_context_data(self, *args, **kwargs):
        context = super(FilterMixin, self).get_context_data(*args, **kwargs)
        qs = self.get_queryset()
        ordering = self.request.GET.get(self.search_ordering_param)
        if ordering:
            qs = qs.order_by(ordering)
        filter_class = self.filter_class
        if filter_class:
            f = filter_class(self.request.GET, queryset=qs)
            context["object_list"] = f
        return context


class ProductListView(FilterMixin, ListView):
    model = Product
    queryset = Product.objects.all()
    filter_class = ProductFilter

    def get_context_data(self, *args, **kwargs):
        context = super(ProductListView, self).get_context_data(*args, **kwargs)
        context["query"] = self.request.GET.get("q")
        context["filter_form"] = ProductFilterForm(data=self.request.GET or None)
        return context

    def get_queryset(self, *args, **kwargs):
        qs = super(ProductListView, self).get_queryset(*args, **kwargs)
        query = self.request.GET.get("q")
        if query:
            qs = Product.objects.filter(Q(title__icontains=query) |
                Q(description__icontains=query))
            try:
                qs2 = Product.objects.filter(Q(price=query))
                qs = (qs | qs2).distinct()
            except:
                pass
        return qs


class ProductDetailView(DetailView):
    model = Product

    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailView, self).get_context_data(*args, **kwargs)
        instance = self.get_object()
        context["related"] = sorted(Product.objects.get_related(instance)[:6], key= lambda x: random.random())
        return context