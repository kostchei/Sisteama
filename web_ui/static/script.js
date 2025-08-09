document.addEventListener("DOMContentLoaded", () => {
    const messages = document.getElementById("messages");
    const messageInput = document.getElementById("message-input");
    const sendButton = document.getElementById("send-button");

    const ws = new WebSocket(`ws://${window.location.host}/ws`);

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        const messageElement = document.createElement("div");
        messageElement.classList.add("message");

        const senderElement = document.createElement("span");
        senderElement.classList.add("sender");
        if (data.sender === "You") {
            senderElement.classList.add("You");
        }
        senderElement.textContent = `${data.sender}: `;

        const contentElement = document.createElement("span");
        contentElement.textContent = data.message;

        messageElement.appendChild(senderElement);
        messageElement.appendChild(contentElement);
        messages.appendChild(messageElement);
        messages.scrollTop = messages.scrollHeight;
    };

    const sendMessage = () => {
        const message = messageInput.value;
        if (message.trim() !== "") {
            ws.send(message);
            messageInput.value = "";
        }
    };

    sendButton.addEventListener("click", sendMessage);

    messageInput.addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
            sendMessage();
        }
    });
});
