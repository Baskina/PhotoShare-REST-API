console.log("Run")
import {baseUrl} from './config.js';

const form = document.forms[0]

const urlParams = new URLSearchParams(window.location.search);
const message = urlParams.get("message");

const returnMessage = document.getElementById("return_message")

if (message) {
    returnMessage.innerHTML = "";

    const lines = message.split("\n");
    const returnMessageContainer = document.createElement("div");
    returnMessageContainer.className = "text-center bright-primary-color";

    lines.forEach((line) => {
        const lineElement = document.createElement("p");
        lineElement.textContent = line;
        returnMessageContainer.appendChild(lineElement);

    });

    returnMessage.appendChild(returnMessageContainer);
    returnMessage.classList.add("text-center");
}


form.addEventListener("submit", async (e) => {
    e.preventDefault()
    const username = form.username.value
    const password = form.password.value

    const myHeaders = new Headers();
    myHeaders.append("Content-Type", "application/x-www-form-urlencoded");

    const urlencoded = new URLSearchParams();
    urlencoded.append("username", username);
    urlencoded.append("password", password);

    var requestOptions = {
        method: 'POST',
        headers: myHeaders,
        body: urlencoded,
        redirect: 'follow'
    };

    const response = await fetch(
        `${baseUrl}/api/auth/login`,
        requestOptions);
    const result = await response.json()
    if (response.status == 200) {
        localStorage.setItem("accessToken", result.access_token);
        localStorage.setItem("refreshToken", result.refresh_token);
        window.location = '/templates/index.html'
    } else {
        returnMessage.textContent = result.detail || result.message;
    }

    if (response.status === 401) {
        returnMessage.textContent = result.detail || result.message;
        returnMessage.style.color = "red";
    }
})