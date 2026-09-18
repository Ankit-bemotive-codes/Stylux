from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Address, Category, Product


class ProductStorefrontTests(TestCase):
    def setUp(self):
        self.gold_category = Category.objects.create(name="Gold Jewellery", slug="gold_jewellery")
        self.gold_category_alt = Category.objects.create(name="Gold", slug="gold")
        self.diamond_category = Category.objects.create(name="Diamond Jewellery", slug="diamond_jewellery")

        self.featured = Product.objects.create(
            name="Test Gold Necklace",
            category=self.gold_category,
            price=25000,
            image_url="https://example.com/necklace.jpg",
            is_featured=True,
        )
        self.gold_alt_product = Product.objects.create(
            name="Gold Bangles",
            category=self.gold_category_alt,
            price=18000,
            image_url="https://example.com/bangles.jpg",
            is_featured=False,
        )
        Product.objects.create(
            name="Inactive Ring",
            category=self.diamond_category,
            price=50000,
            image_url="https://example.com/ring.jpg",
            is_active=False,
        )

    def test_home_shows_active_featured_products(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.featured.name)
        self.assertNotContains(response, "Inactive Ring")

    def test_collection_filters_products_by_category(self):
        response = self.client.get(reverse("gold_jewellery"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.featured.name)
        self.assertContains(response, self.gold_alt_product.name)
        self.assertNotContains(response, "Inactive Ring")

    def test_search_finds_active_products_and_excludes_inactive_products(self):
        response = self.client.get(reverse("search"), {"q": "gold"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.featured.name)
        self.assertNotContains(response, "Inactive Ring")

    def test_all_storefront_routes_render(self):
        route_names = (
            "new_arrivals", "gold_jewellery", "diamond_jewellery",
            "bridal", "collections", "offers", "cart",
        )
        for route_name in route_names:
            with self.subTest(route_name=route_name):
                self.assertEqual(self.client.get(reverse(route_name)).status_code, 200)

    def test_product_is_registered_in_admin(self):
        self.assertIn(Product, admin.site._registry)

    def test_product_images_only_use_existing_local_media_files(self):
        response = self.client.get(reverse("home"))

        self.assertNotContains(response, "https://example.com/necklace.jpg")
        self.assertNotContains(response, "https://example.com/bangles.jpg")

    def test_navigation_includes_local_product_search_index(self):
        response = self.client.get(reverse("home"))

        self.assertContains(response, 'data-search-product')
        self.assertContains(response, 'data-name="Test Gold Necklace"')

    def test_checkout_shows_saved_addresses_for_logged_in_user(self):
        user = get_user_model().objects.create_user(username="checkoutuser", password="pass1234")
        Address.objects.create(
            user=user,
            address_line1="12 Market Street",
            city="Mumbai",
            state="Maharashtra",
            postal_code="400001",
            country="India",
        )

        self.client.force_login(user)
        response = self.client.get(reverse("checkout"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Saved addresses")
        self.assertContains(response, "12 Market Street")

    def test_checkout_saves_new_address_for_logged_in_user(self):
        user = get_user_model().objects.create_user(username="newaddressuser", password="pass1234")
        self.client.force_login(user)

        response = self.client.post(reverse("checkout"), {
            "address_mode": "new",
            "address_line1": "45 Golden Lane",
            "address_line2": "Near Temple",
            "city": "Jaipur",
            "state": "Rajasthan",
            "postal_code": "302001",
            "country": "India",
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Address.objects.filter(user=user, address_line1="45 Golden Lane").exists())

    def test_checkout_preselects_default_saved_address(self):
        user = get_user_model().objects.create_user(username="defaultaddressuser", password="pass1234")
        first = Address.objects.create(
            user=user,
            address_line1="1 First Street",
            city="Delhi",
            state="Delhi",
            postal_code="110001",
            country="India",
        )
        second = Address.objects.create(
            user=user,
            address_line1="2 Second Street",
            city="Mumbai",
            state="Maharashtra",
            postal_code="400002",
            country="India",
            is_default=True,
        )

        self.client.force_login(user)
        response = self.client.get(reverse("checkout"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="' + str(second.id) + '" checked')
        self.assertNotContains(response, 'value="' + str(first.id) + '" checked')

    def test_new_address_can_be_set_as_default(self):
        user = get_user_model().objects.create_user(username="defaultnewaddressuser", password="pass1234")
        existing = Address.objects.create(
            user=user,
            address_line1="Old House",
            city="Pune",
            state="Maharashtra",
            postal_code="411001",
            country="India",
            is_default=True,
        )

        self.client.force_login(user)
        response = self.client.post(reverse("checkout"), {
            "address_mode": "new",
            "address_line1": "New House",
            "city": "Bengaluru",
            "state": "Karnataka",
            "postal_code": "560001",
            "country": "India",
            "set_as_default": "on",
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Address.objects.filter(user=user, address_line1="New House", is_default=True).exists())
        self.assertFalse(Address.objects.get(pk=existing.pk).is_default)
