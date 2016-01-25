from django.contrib import admin

from .models import Product, ProductImage, Variation, Category, ProductFeatured


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


class VariationInline(admin.TabularInline):
    model = Variation
    extra = 0


class ProductAdmin(admin.ModelAdmin):
    list_display = ["__str__", "price"]
    inlines = [
        ProductImageInline,
        VariationInline,
    ]

    class Meta:
        model = Product


admin.site.register(Category)

admin.site.register(Product, ProductAdmin)

admin.site.register(ProductImage)

admin.site.register(ProductFeatured)

admin.site.register(Variation)
