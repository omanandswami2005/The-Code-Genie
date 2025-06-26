document.addEventListener("DOMContentLoaded", () => {
    const chatWindow = document.getElementById("chat-window");
    const promptInput = document.getElementById("prompt-input");
    const sendButton = document.getElementById("send-button");
    const approveButton = document.getElementById("approve-button");
    const srsDisplay = document.getElementById("srs-display");

    // Establish WebSocket connection
    const socket = new WebSocket(`ws://${window.location.host}/ws`);

    socket.onopen = () => {
        console.log("WebSocket connection established.");
        addMessage("System", "🔗 Connected to CodeGenie agent server.", "system-status");
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log("Received from server:", data);

        switch(data.type) {
            case "partial_text":
                // Handle streaming text responses
                appendToLastMessage(data.data);
                break;
                
            case "srs_draft":
                // Display the generated SRS
                displaySRS(data.content);
                addMessage("Agent", "📋 SRS draft generated. Please review and approve to continue.", "agent-response");
                approveButton.style.display = "inline-block";
                enableInput();
                break;
                
            case "status":
                addMessage("System", data.content, "system-status");
                break;
                
            case "workflow_update":
                addMessage("Agent", data.content, "agent-response");
                break;
                
            case "turn_complete":
                // Agent turn is complete
                console.log("Agent turn completed");
                break;
                
            case "error":
                addMessage("System", `❌ Error: ${data.content}`, "error-message");
                enableInput();
                break;
                
            default:
                console.log("Unknown message type:", data.type);
        }
    };

    socket.onclose = () => {
        console.log("WebSocket connection closed.");
        addMessage("System", "🔌 Connection to server lost.", "system-status");
    };

    socket.onerror = (error) => {
        console.error("WebSocket error:", error);
        addMessage("System", "❌ Connection error occurred.", "error-message");
    };

    function sendMessage(type, content = "") {
        const message = JSON.stringify({ type, content });
        socket.send(message);
    }

    function addMessage(sender, text, cssClass) {
        const messageElement = document.createElement("div");
        messageElement.className = "message";
        messageElement.innerHTML = `<strong>${sender}:</strong>`;
        
        const textElement = document.createElement("div");
        textElement.textContent = text;
        textElement.className = cssClass;
        messageElement.appendChild(textElement);
        
        chatWindow.appendChild(messageElement);
        chatWindow.scrollTop = chatWindow.scrollHeight;
        
        // Store reference for potential streaming updates
        messageElement.textElement = textElement;
    }

    function appendToLastMessage(text) {
        const messages = chatWindow.querySelectorAll(".message");
        if (messages.length > 0) {
            const lastMessage = messages[messages.length - 1];
            if (lastMessage.textElement) {
                lastMessage.textElement.textContent += text;
                chatWindow.scrollTop = chatWindow.scrollHeight;
            }
        }
    }

    function displaySRS(srsContent) {
        if (srsDisplay) {
            // Convert markdown to HTML for better display
            srsDisplay.innerHTML = `<pre>${srsContent}</pre>`;
        }
    }

    function disableInput() {
        promptInput.disabled = true;
        sendButton.disabled = true;
        sendButton.textContent = "Processing...";
    }

    function enableInput() {
        promptInput.disabled = false;
        sendButton.disabled = false;
        sendButton.textContent = "Generate SRS";
    }

    // Event listeners
    sendButton.addEventListener("click", () => {
        const prompt = promptInput.value.trim();
        if (prompt) {
            addMessage("You", prompt, "user-prompt");
            sendMessage("prompt", prompt);
            promptInput.value = "";
            disableInput();
            approveButton.style.display = "none";
        }
    });

    promptInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendButton.click();
        }
    });

    approveButton.addEventListener("click", () => {
        addMessage("You", "✅ [Approved SRS - Continuing workflow]", "user-approval");
        sendMessage("approve");
        approveButton.style.display = "none";
    });
});