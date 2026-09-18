import json
from decimal import Decimal

from django.db.models import Q
from django.shortcuts import redirect, render

from .models import Address, Ecomm_OrderItem, Ecomm_order, Product


CATEGORY_SLUG_ALIASES = {
    "gold_jewellery": ["gold_jewellery", "gold"],
    "diamond_jewellery": ["diamond_jewellery", "diamond"],
}


def _active_products(category_slug=None):
    products = Product.objects.filter(is_active=True)
    if category_slug:
        aliases = CATEGORY_SLUG_ALIASES.get(category_slug, [category_slug])
        products = products.filter(
            Q(category__slug__in=aliases)
            | Q(category__name__iexact=aliases[0].replace("_jewellery", ""))
            | Q(category__name__icontains=aliases[0].split("_")[0])
        )
    return products


def _catalog_context(category_slug=None):
    return {"products": _active_products(category_slug)}


def search(request):
    query = request.GET.get("q", "").strip()
    products = _active_products()
    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
            | Q(category__slug__icontains=query)
        )
    return render(request, "catalog_page.html", {
        "products": products,
        "page_key": "search",
        "page_title": f'Search results for "{query}"' if query else "Search products",
        "page_description": "Find the piece that feels made for your moment.",
    })


def home(request):
    site_name = "juelary"
    tagline = "what you need is here"
    title = "juelary App"
    context = {
        "site_name": site_name,
        "tagline": tagline,
        "title": title,
    }
    context["products"] = _active_products()
    context["featured_products"] = _active_products().filter(is_featured=True)
    return render(request, "index.html", context)


def cart(request):
    return render(request, "cart.html")


def checkout(request):
    saved_addresses = []
    default_address = None
    latest_order = None

    if request.user.is_authenticated:
        saved_addresses = Address.objects.filter(user=request.user).order_by('-created_at')
        default_address = saved_addresses.filter(is_default=True).first() or saved_addresses.first()

    order_id = request.GET.get("order_id")
    if order_id:
        latest_order = Ecomm_order.objects.filter(order_id=order_id).first()

    if request.method == "POST":
        if request.user.is_authenticated and request.POST.get("delete_address_id"):
            address_id = request.POST.get("delete_address_id")
            address_to_delete = Address.objects.filter(user=request.user, pk=address_id).first()
            if address_to_delete:
                was_default = address_to_delete.is_default
                address_to_delete.delete()

                if was_default:
                    fallback_address = Address.objects.filter(user=request.user).order_by('-created_at').first()
                    if fallback_address:
                        fallback_address.is_default = True
                        fallback_address.save()
            return redirect("checkout")

        if request.POST.get("place_order") == "1":
            selected_address = None
            if request.user.is_authenticated:
                selected_id = request.POST.get("selected_address_id")
                if selected_id:
                    selected_address = Address.objects.filter(user=request.user, pk=selected_id).first()

                if not selected_address and request.POST.get("address_mode") == "new":
                    address_line1 = request.POST.get("address_line1", "").strip()
                    if address_line1:
                        selected_address = Address.objects.filter(user=request.user, address_line1=address_line1).order_by('-created_at').first()

                if not selected_address:
                    selected_address = Address.objects.filter(user=request.user).order_by('-created_at').first()

            cart_payload = request.POST.get("order_items", "[]")
            try:
                cart_items = json.loads(cart_payload) if cart_payload else []
            except json.JSONDecodeError:
                cart_items = []

            total_amount = Decimal("0")
            order_items = []
            for item in cart_items:
                product_id = item.get("id")
                qty = int(item.get("qty", 1) or 1)
                product = Product.objects.filter(pk=product_id).first()
                if product:
                    order_items.append((product, qty))
                    total_amount += Decimal(str(product.price)) * qty

            if not request.user.is_authenticated or not order_items or not selected_address:
                return redirect("checkout")

            order = Ecomm_order.objects.create(
                user=request.user,
                shipping_address=selected_address,
                total_amount=total_amount,
                payment_mode=request.POST.get("payment_method", "cod"),
                payment_status="pending",
            )

            for product, qty in order_items:
                Ecomm_OrderItem.objects.create(order=order, product=product, quantity=qty)

            return redirect(f"{request.path}?order_id={order.order_id}")

        if request.user.is_authenticated and request.POST.get("address_mode") == "new":
            save_address = request.POST.get("save_address") == "save_and_default"
            set_as_default = save_address or request.POST.get("set_as_default") == "on"
            new_address = Address.objects.create(
                user=request.user,
                address_line1=request.POST.get("address_line1", "").strip(),
                address_line2=request.POST.get("address_line2", "").strip() or "",
                city=request.POST.get("city", "").strip(),
                state=request.POST.get("state", "").strip(),
                postal_code=request.POST.get("postal_code", "").strip(),
                country=request.POST.get("country", "").strip(),
                is_default=set_as_default,
            )

            if set_as_default:
                Address.objects.filter(user=request.user).exclude(pk=new_address.pk).update(is_default=False)
            return redirect("checkout")

        if request.POST.get("selected_address_id"):
            selected_id = request.POST.get("selected_address_id")
            if selected_id:
                Address.objects.filter(user=request.user).exclude(pk=selected_id).update(is_default=False)
                Address.objects.filter(user=request.user, pk=selected_id).update(is_default=True)
            return redirect("checkout")

    return render(request, "checkout.html", {
        "saved_addresses": saved_addresses,
        "default_address": default_address,
        "latest_order": latest_order,
    })


def bridal(request):
    return render(request, "bridal.html", _catalog_context("bridal"))


def collections(request):
    return render(request, "collections.html", _catalog_context("collections"))


def gold_jewellery(request):
    return render(request, "gold_jewellery.html", _catalog_context("gold_jewellery"))


def footer(request):
    return render(request, "footer.html")


def diamond_jewellery(request):
    return render(request, "diamond_jewellery.html", _catalog_context("diamond_jewellery"))


def navbar(request):
    return render(request, "navbar.html")


def offers(request):
    return render(request, "offers.html", _catalog_context("offers"))


def new_arrivals(request):
    return render(request, "new_arrivals.html", _catalog_context("new_arrivals"))

