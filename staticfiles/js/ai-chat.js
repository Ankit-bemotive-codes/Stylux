(function () {
  document.addEventListener("DOMContentLoaded", function () {
    var widget = document.querySelector("[data-ai-chat]");
    if (!widget) return;

    var panel = widget.querySelector("#aiChatPanel");
    var form = widget.querySelector("[data-ai-form]");
    var input = widget.querySelector("[name='user_input']");
    var messages = widget.querySelector("[data-ai-messages]");
    var status = widget.querySelector("[data-ai-status]");
    if (!panel || !form || !input || !messages || !status) return;

    widget.querySelectorAll("[data-ai-toggle]").forEach(function (button) {
      button.addEventListener("click", function () {
        var isClosed = panel.hidden;
        panel.hidden = !isClosed;
        widget.querySelectorAll("[data-ai-toggle]").forEach(function (toggle) {
          toggle.setAttribute("aria-expanded", String(isClosed));
        });
        if (isClosed) input.focus();
      });
    });

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var userInput = input.value.trim();
      if (!userInput) return;

      var userMessage = document.createElement("div");
      userMessage.className = "ai-chat-message ai-chat-message-user";
      userMessage.textContent = userInput;
      messages.appendChild(userMessage);
      var formData = new FormData(form);
      input.value = "";
      input.disabled = true;
      status.textContent = "Finding a thoughtful recommendation...";

      fetch(form.action, {
        method: "POST",
        body: formData,
        headers: { "X-Requested-With": "XMLHttpRequest" }
      })
        .then(function (response) {
          return response.text().then(function (answer) {
            if (!response.ok) throw new Error(answer || "Request failed");
            return answer;
          });
        })
        .then(function (answer) {
          var botMessage = document.createElement("div");
          botMessage.className = "ai-chat-message ai-chat-message-bot";
          botMessage.textContent = answer;
          messages.appendChild(botMessage);
          status.textContent = "";
        })
        .catch(function (error) {
          status.textContent = error.message || "The assistant is unavailable right now. Please try again shortly.";
        })
        .finally(function () {
          input.disabled = false;
          input.focus();
          messages.scrollTop = messages.scrollHeight;
        });
    });
  });
})();