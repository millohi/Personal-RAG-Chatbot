async function sendMessage() {
    const inputField = document.getElementById("user-input");
    const userText = inputField.value.trim();
    const submitButton = document.getElementById("submit");

    if (!userText) return;
    submitButton.disabled = true;

    addMessage(userText, "user");
    inputField.value = "";
    const params = new URLSearchParams(window.location.search);
    const firma = params.get('firma'); // z.B. "firma1"
    const code = params.get('code');   // z.B. "geheimerCode"

    try {
        const response = await fetch("http://localhost:8000/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({query: userText, firma: firma, code: code})
        });

        const data = await response.json();
        addMessage(data.response || "Fehler bei der Antwort.", "bot");
    } catch (err) {
        addMessage("Fehler beim Verbinden zum Server.", "bot");
    }
    submitButton.disabled = false;
}

function addMessage(text, sender) {
    const chatBox = document.getElementById("chat-box");
    const msg = document.createElement("div");
    msg.classList.add("message", sender);
    msg.textContent = text;
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
}

document.getElementById("user-input").addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
        const submitButton = document.getElementById("submit");
        if (!submitButton.disabled){
            sendMessage();
        }
    }
});
