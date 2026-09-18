from django.urls import path
from .views import ai_chat


urlpatterns = [ 
    path("ai_chat/", ai_chat, name="ai_chat"),
]

'''path("airecom/",airecom,name="airecom"),'''