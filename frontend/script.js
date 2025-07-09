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

let url = "https://bot.camillo-dobrovsky.de/chat";

let accepted = false;
let salutation = "";
let userName = "";
let first_message = true;
const params = new URLSearchParams(window.location.search);
const firma = params.get('firma');
const code = params.get('code');

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
    if (!firma || !code) {
        addMessage("Fehler, leider konnte die Session nicht autorisiert werden", "bot");
    }
    else {
        await showIntroSequence();
    }
});

async function showIntroSequence() {
    addMessage("Hallo, willkommen beim KI-Chat. Die KI kann Fehler machen. Alle Fragen über ihn oder diese Anwendung beantwortet Camillo auch gerne im persönlichen Gespräch.", "bot");
    await wait(2000);

    addMessage(
        `Ich bin mir bewusst, dass zur Bereitstellung des Chatbots meine Chat-Anfragen sowohl an einen weiteren Server (ZAP-Hosting) in Deutschland als auch die OpenAI-API übermittelt werden. Ich werde keine sensiblen oder anderweitig kritische Daten im Chat verwenden. Weitere Details gibt es in der <a href='datenschutz.html' target='_blank'>Datenschutzerklärung</a>.`,
        "bot"
    );
    await wait(3000);

    askForConsent();
    const submitButton = document.getElementById("submit");
    submitButton.disabled = false;
}

function askForConsent() {
    addMessage("Zum Akzeptieren bitte mit \"JA\" antworten.", "bot");
}

function askForPreferences() {
    addMessage("Danke. Noch zwei kurze Fragen zum Thema Anrede:", "bot");
    show_preferences()
    //document.getElementById("prechat-form").style.display = "flex";
}

function save_preferences() {
    const selected = document.querySelector("input[name='salutation']:checked");
    if (selected.value === "sie") {
        salutation = "Sieze"
    } else {
        salutation = "Duze"
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

    if (salutation === "") {
        const saveBtn = document.getElementById("save-prechat");
        saveBtn.classList.add("blink");
        setTimeout(() => saveBtn.classList.remove("blink"), 1000);
        return;
    }
    inputField.value = "";
    addMessage(userText, "user");

    submitButton.disabled = true;
    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                query: userText,
                company: firma,
                code: code,
                salutation: salutation,
                username: userName,
                first_time: first_message,
            })
        });
        const data = await response.json();
        if (!response.ok) {
            // Hole die Fehlermeldung aus "answer", oder fallback
            const errorMsg = data.answer || "Unbekannter Fehler vom Server.";
            throw new Error(errorMsg);
        }
        addMessage(data.answer || "Fehler bei der Antwort.", "bot");
        first_message = false;
    } catch (err) {
        addMessage(err.message || "Fehler beim Verbinden zum Server.", "bot");
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
    msg.innerHTML = "<div id='prechat-form'><label><input type=\"radio\" name=\"salutation\" value=\"du\" id='='> Ich möchte geduzt werden.</label>&emsp;" +
        "<label><input type=\"radio\" name=\"salutation\" value=\"sie\" checked> Ich möchte gesiezt werden.</label><br/><br/>" +
        "<label for=\"name-input\">Name (falls gewünscht, wird an OpenAI gesendet): </label>" +
        "<input type=\"text\" id=\"name-input\" placeholder=\"Name (optional)\" /></br><br/>" +
        "<button id=\"save-prechat\" onclick=\"save_preferences()\">Speichern</button></div>"+
        "<div id='prechat-form-thanks' style='display:none'>Danke, die Wünsche wurden gespeichert und es kann losgehen!</br>Ich kann verschiedenste Fragen beantworten, z.B.: Was hat Camillo studiert? | Was ist Camillo am Arbeitsumfeld besonders wichtig? | Kannst du eine lustige Geschichte über Camillo erzählen?</div>"
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
