from unittest.mock import Mock, patch

from django.test import TestCase, override_settings
from django.urls import reverse

from core.models import Category, Product


class AIChatTests(TestCase):
	@override_settings(GEMINI_API_KEY="test-key")
	@patch("ai.services.genai.Client")
	def test_chat_can_create_product_from_name(self, client_class):
		response = Mock(text="Product added successfully.")
		client_class.return_value.chats.create.return_value.send_message.return_value = response

		result = self.client.post(reverse("ai_chat"), {"user_input": "Add product Diamond Bracelet for 25000"})

		self.assertEqual(result.status_code, 200)
		self.assertTrue(Product.objects.filter(name="Diamond Bracelet").exists())
		self.assertEqual(Product.objects.get(name="Diamond Bracelet").price, 25000)

	def test_get_is_not_allowed(self):
		response = self.client.get(reverse("ai_chat"))

		self.assertEqual(response.status_code, 405)

	def test_empty_question_is_rejected(self):
		response = self.client.post(reverse("ai_chat"), {"user_input": "  "})

		self.assertEqual(response.status_code, 400)
		self.assertEqual(response.json()["error"], "Please ask a jewellery question.")

	@override_settings(GEMINI_API_KEY="test-key")
	@patch("ai.services.genai.Client")
	def test_question_returns_gemini_answer(self, client_class):
		category = Category.objects.create(name="Gold Jewellery", slug="gold_jewellery")
		product = Product.objects.create(
			name="Gold Ring",
			category=category,
			price=12000,
			is_featured=True,
		)
		response = Mock(text="Styling Tip\nPair it with a simple chain.")
		client_class.return_value.chats.create.return_value.send_message.return_value = response

		result = self.client.post(reverse("ai_chat"), {"user_input": "What goes with a gold ring?"})

		self.assertEqual(result.status_code, 200)
		self.assertEqual(result.json()["answer"], response.text)
		self.assertEqual(result.json()["products"][0]["id"], product.pk)
		self.assertEqual(result.json()["products"][0]["price"], "12000.00")

	@override_settings(GEMINI_API_KEY="")
	def test_missing_api_key_returns_service_unavailable(self):
		result = self.client.post(reverse("ai_chat"), {"user_input": "Suggest a necklace."})

		self.assertEqual(result.status_code, 503)
