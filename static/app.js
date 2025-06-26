document.addEventListener("DOMContentLoaded", () => {
    const chatWindow = document.getElementById("chat-window");
    const promptInput = document.getElementById("prompt-input");
    const sendButton = document.getElementById("send-button");
    const approveButton = document.getElementById("approve-button");

    // Establish WebSocket connection with the Flask server
    const socket = new WebSocket(`ws://${window.location.host}/ws`);

    socket.onopen = () => {
        console.log("WebSocket connection established.");
        addMessage("System", "Connected to agent server.", "system-status");
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log("Received from server:", data);

        if (data.type === "srs_draft") {
            addMessage("Agent (SRS Draft)", data.content, "agent-response");
            // Show the approve button only when the draft is ready
            approveButton.style.display = "inline-block";
        } else if (data.type === "status") {
            addMessage("System", data.content, "system-status");
        }
    };

    socket.onclose = () => {
        console.log("WebSocket connection closed.");
        addMessage("System", "Connection to server lost.", "system-status");
    };

    function sendMessage(type, content = "") {
        const message = JSON.stringify({ type, content });
        socket.send(message);
    }

    function addMessage(sender, text, cssClass) {
        const messageElement = document.createElement("div");
        messageElement.innerHTML = `<strong>${sender}:</strong>`;
        const textElement = document.createElement("p");
        textElement.textContent = text;
        textElement.className = cssClass;
        messageElement.appendChild(textElement);
        chatWindow.appendChild(messageElement);
        chatWindow.scrollTop = chatWindow.scrollHeight; // Auto-scroll
    }

    sendButton.addEventListener("click", () => {
        const prompt = promptInput.value;
        if (prompt.trim()) {
            addMessage("You", prompt, "user-prompt");
            sendMessage("prompt", prompt);
            promptInput.value = "";
            promptInput.disabled = true; // Disable input after sending
            sendButton.disabled = true;
        }
    });

    approveButton.addEventListener("click", () => {
        addMessage("You", "[Clicked Approve SRS Button]", "user-prompt");
        sendMessage("approve");
        approveButton.style.display = "none"; // Hide after clicking
    });
});