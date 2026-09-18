import re

from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from core.models import Product

from .services import create_product_from_chat_message, find_matching_products, get_ai_stylist_recommendation, get_jewelry_recommendation


'''def airecom(request):

    recommendation = get_jewelry_recommendation(
        product_name="Elegant Gold Necklace",
        product_description="A beautiful gold necklace with a traditional and elegant design."
    )

    return HttpResponse(recommendation)
'''

@require_POST
def ai_chat(request):
    user_input = request.POST.get("user_input", "").strip()
    if not user_input:
        return JsonResponse({"error": "Please ask a jewellery question."}, status=400)

    matching_products = find_matching_products(user_input)

    created_product = create_product_from_chat_message(user_input)
    if created_product and not matching_products:
        product = created_product["product"]
        return JsonResponse({
            "answer": created_product["answer"],
            "products": [
                {
                    "id": product.pk,
                    "name": product.name,
                    "price": str(product.price),
                    "image": product.local_image_url,
                    "category": product.category.name,
                }
            ],
        })

    try:
        recommendation = get_ai_stylist_recommendation(user_prompt=user_input)
        response = recommendation.get("answer") or ""
    except Exception:
        try:
            response = get_jewelry_recommendation(
                product_name=user_input,
                product_description=user_input,
            )
        except Exception:
            if matching_products:
                response = "Here are matching products from our catalog."
            else:
                return JsonResponse(
                    {"error": "The jewellery assistant is temporarily unavailable. Please try again later."},
                    status=503,
                )

    if not matching_products:
        terms = [term for term in re.findall(r"[a-zA-Z0-9]+", user_input.lower()) if len(term) > 2]
        matching_query = Q()
        for term in terms:
            matching_query |= (
                Q(name__icontains=term)
                | Q(description__icontains=term)
                | Q(category__name__icontains=term)
            )

        products = list(Product.objects.filter(is_active=True).filter(matching_query)[:4]) if terms else []
        if len(products) < 4:
            existing_ids = [product.pk for product in products]
            products.extend(
                Product.objects.filter(is_active=True, is_featured=True)
                .exclude(pk__in=existing_ids)[:4 - len(products)]
            )
    else:
        products = matching_products[:4]

    return JsonResponse({
        "answer": response,
        "products": [
            {
                "id": product.pk,
                "name": product.name,
                "price": str(product.price),
                "image": product.local_image_url,
                "category": product.category.name if product.category else "General",
            }
            for product in products
        ],
    })