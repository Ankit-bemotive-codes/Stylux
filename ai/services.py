import json
import re
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.db.models import Q
from django.utils.text import slugify
from google import genai
from google.genai import types

from core.models import Category, Product

def search_catalog(keywords: str, max_price: float = None) -> str:
    """
    Search available products in the catalog by keyword and optional maximum price.
    """
    qs = Product.objects.filter(is_active=True)

    if max_price is not None:
        qs = qs.filter(price__lte=max_price)

    keywords_list = [term for term in re.findall(r"[a-zA-Z0-9]+", (keywords or "").lower()) if len(term) > 2]
    if not keywords_list:
        return json.dumps({"status": "no_results", "items": []})

    query = Q()
    for term in keywords_list:
        query |= Q(name__icontains=term) | Q(description__icontains=term) | Q(category__name__icontains=term)

    matched = qs.filter(query).distinct()[:6]
    if not matched.exists():
        return json.dumps({"status": "no_results", "items": []})

    results = []
    for item in matched:
        results.append({
            "id": item.id,
            "name": item.name,
            "price": float(item.price),
            "category": item.category.name if item.category else "General",
            "description": (item.description or "")[:120],
            "image": item.local_image_url,
        })

    return json.dumps({"status": "found", "items": results})


def get_ai_stylist_recommendation(user_prompt: str, chat_history: list = None) -> dict:
    """
    Use Gemini with a tool-based catalog search to recommend products.
    """
    if not settings.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    client = genai.Client(
        api_key=settings.GEMINI_API_KEY,
        http_options=types.HttpOptions(timeout=settings.GEMINI_TIMEOUT),
    )

    system_instruction = """
You are an expert personal shopping stylist for a jewelry e-commerce platform.
Your goal is to understand the customer's occasion, taste, and budget and curate a matching recommendation using products from the catalog.

Rules:
1. ALWAYS call search_catalog to inspect what items actually exist in inventory.
2. NEVER invent fake product IDs or fake products that are not returned by search_catalog.
3. Stay strictly within the user's budget if one is stated.
4. Keep your advice stylish, concise, and professional.
5. Use plain text and short paragraphs.
"""

    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=[search_catalog],
                temperature=0.7,
            ),
        )
        answer = getattr(response, "text", None)
        if isinstance(answer, str) and answer.strip():
            return {"answer": answer.strip()}
    except Exception:
        pass

    chat = client.chats.create(model=settings.GEMINI_MODEL)
    prompt = f"{system_instruction}\n\nUser request: {user_prompt}"
    response = chat.send_message(prompt)
    answer = getattr(response, "text", None)
    if isinstance(answer, str) and answer.strip():
        return {"answer": answer.strip()}

    raise RuntimeError("Gemini returned an empty response")


def get_jewelry_recommendation(product_name, product_description):
    if not settings.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    client = genai.Client(
        api_key=settings.GEMINI_API_KEY,
        http_options=types.HttpOptions(timeout=settings.GEMINI_TIMEOUT),
    )

    prompt = f"""
You are an expert jewelry stylist and assistant.
Talk to the user in a professional and concise manner.
Analyze this jewelry product:

Product name:
{product_name}

Product description:
{product_description}

Give useful advice and recommendations.
Don't use emojis or special characters in your response. Always write in a professional and concise manner in new lines.
Return the answer with these sections:

1. Styling Tip
2. Related Jewelry Recommendations with some image URLs

"""
    chat = client.chats.create(model=settings.GEMINI_MODEL)
    response = chat.send_message(prompt)
    answer = (response.text or "").strip()
    if not answer:
        raise RuntimeError("Gemini returned an empty response")
    return answer


def find_matching_products(message, limit=4):
    if not message:
        return []

    text = message.strip()
    if not text:
        return []

    terms = [term for term in re.findall(r"[a-zA-Z0-9]+", text.lower()) if len(term) > 2]
    if not terms:
        return []

    query = Q()
    for term in terms:
        query |= Q(name__icontains=term) | Q(description__icontains=term) | Q(category__name__icontains=term)

    return list(Product.objects.filter(is_active=True).filter(query).distinct()[:limit])


def create_product_from_chat_message(message):
    if not message:
        return None

    text = message.strip()
    lower_text = text.lower()

    if not re.search(r"\b(?:add|create|new|make)\b", lower_text):
        return None

    patterns = [
        r"(?i)\b(?:add|create|new|make)\s+(?:a\s+)?(?:product|jewellery|jewel)\s+(.+?)(?:\s+(?:for|at|price|worth|cost|costs|rs|inr|₹)\s*[:=]?\s*|\s+)([0-9][0-9,]*(?:\.\d+)?)\b",
        r"(?i)\b(?:add|create|new|make)\s+(?:a\s+)?(.+?)(?:\s+(?:for|at|price|worth|cost|costs|rs|inr|₹)\s*[:=]?\s*|\s+)([0-9][0-9,]*(?:\.\d+)?)\b",
        r"(?i)\b(?:add|create|new|make)\s+(?:a\s+)?(.+?)\s+([0-9][0-9,]*(?:\.\d+)?)\b",
    ]

    match = None
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            break

    if not match:
        return None

    product_name = match.group(1).strip().strip("'\"")
    product_name = re.sub(r"\s+", " ", product_name)
    price_text = match.group(2).replace(",", "").strip()

    try:
        price = Decimal(price_text)
    except InvalidOperation:
        return None

    if not product_name:
        return None

    keyword_to_category = {
        "ring": "Rings",
        "necklace": "Necklaces",
        "bracelet": "Bracelets",
        "earring": "Earrings",
        "pendant": "Pendants",
        "chain": "Chains",
        "bangle": "Bangles",
        "anklet": "Anklets",
        "set": "Jewellery Sets",
        "ear": "Earrings",
        "gold": "Gold Jewellery",
        "silver": "Silver Jewellery",
        "diamond": "Diamond Jewellery",
    }

    product_name_lower = product_name.lower()
    category_name = "General"
    for keyword, mapped_name in keyword_to_category.items():
        if keyword in product_name_lower:
            category_name = mapped_name
            break

    category, _ = Category.objects.get_or_create(
        name=category_name,
        defaults={"slug": slugify(category_name) or "general"},
    )

    existing_product = Product.objects.filter(name__iexact=product_name).first()
    if existing_product:
        existing_product.category = category
        existing_product.price = price
        existing_product.description = f"Created from chat: {text}"
        existing_product.is_active = True
        existing_product.save(update_fields=["category", "price", "description", "is_active"])
        product = existing_product
        created = False
    else:
        product = Product.objects.create(
            name=product_name,
            category=category,
            price=price,
            description=f"Created from chat: {text}",
            is_active=True,
        )
        created = True

    return {
        "product": product,
        "created": created,
        "answer": f"Product '{product.name}' has been {'updated' if not created else 'created'} for {product.price}.",
    }


'''response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents= prompt,
        
    )
'''

    
