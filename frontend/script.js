/*
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
*/

let url = "https://api.camillo-dobrovsky.de";

let accepted = false;
let anrede = "";
let userName = "";

document.getElementById("user-input").addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
        const submitButton = document.getElementById("submit");
        if (!submitButton.disabled) {
            sendMessage();
        }
    }
});

window.addEventListener("DOMContentLoaded", async () => {
    accepted = false;
    await showIntroSequence();
});

async function showIntroSequence() {
    addMessage("Hallo, willkommen beim KI-Chat. Die KI kann Fehler machen. Alle Fragen über ihn oder diese Anwendung beantwortet Camillo auch gerne im persönlichen Gespräch.", "bot");
    await wait(1000);

    addMessage(
        `Ich bin mir bewusst, dass zur Bereitstellung des Chatbots meine Chat-Anfragen sowohl an einen weiteren Server (ZAP-Hosting) in Deutschland als auch die OpenAI-API übermittelt werden. Ich werde keine sensiblen oder anderweitig kritische Daten im Chat verwenden. Weitere Details gibt es in der <a href='datenschutz.html' target='_blank'>Datenschutzerklärung</a>.`,
        "bot"
    );
    await wait(2000);

    askForConsent();
    const submitButton = document.getElementById("submit");
    submitButton.disabled = false;
}

function askForConsent() {
    addMessage("Zum Akzeptieren bitte mit \"JA\" antworten.", "bot");
}

function askForPreferences() {
    addMessage("Kurze Frage zu Ansprache: Duzen oder Siezen? Und mit oder ohne Namen?", "bot");
    show_preferences()
    //document.getElementById("prechat-form").style.display = "flex";
}

function save_preferences() {
    const selected = document.querySelector("input[name='anrede']:checked");
    if (selected.value === "sie") {
        anrede = "Sieze"
    } else {
        anrede = "Duze"
    }
    userName = document.getElementById("name-input").value.trim();
    document.getElementById("prechat-form").style.display = "none";
    document.getElementById("prechat-form-thanks").style.display = "flex";
}

async function sendMessage() {
    const inputField = document.getElementById("user-input");
    const userText = inputField.value.trim();
    const submitButton = document.getElementById("submit");

    if (!userText) return;

    if (!accepted) {
        if (userText.toLowerCase() === "ja") {
            accepted = true;
            inputField.value = "";
            addMessage(userText, "user");
            askForPreferences();
        } else {
            inputField.value = "";
            askForConsent()
        }
        return;
    }

    if (anrede === "") {
        const saveBtn = document.getElementById("save-prechat");
        saveBtn.classList.add("blink");
        setTimeout(() => saveBtn.classList.remove("blink"), 1000);
        return;
    }
    inputField.value = "";
    addMessage(userText, "user");

    submitButton.disabled = true;
    const params = new URLSearchParams(window.location.search);
    const firma = params.get('firma');
    const code = params.get('code');

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                query: userText,
                firma: firma,
                code: code,
                anrede: anrede,
                name: userName
            })
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
    msg.innerHTML = text;
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function show_preferences() {
    const chatBox = document.getElementById("chat-box");
    const msg = document.createElement("div");
    msg.classList.add("message", "bot");
    msg.innerHTML = "<div id='prechat-form'><label><input type=\"radio\" name=\"anrede\" value=\"du\" id='='> Geduzt</label>&emsp;" +
        "<label><input type=\"radio\" name=\"anrede\" value=\"sie\" checked> Gesiezt</label>&emsp;|&emsp;" +
        "<label for=\"name-input\">Name (wird an OpenAI gesendet!): </label>" +
        "<input type=\"text\" id=\"name-input\" placeholder=\"Name (optional)\" />&emsp;" +
        "<button id=\"save-prechat\" onclick=\"save_preferences()\">Speichern</button></div>"+
        "<div id='prechat-form-thanks' style='display:none'>Danke, die Wünsche wurden gespeichert und es kann losgehen!</div>"
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
