console.log("Run")

import {baseUrl} from './config.js';


const form = document.forms[0]

const urlParams = new URLSearchParams(window.location.search);
const message = urlParams.get("message");

const returnMessage = document.getElementById("return_message")

if (message) {
    returnMessage.innerHTML = ""
    const returnMessageH = document.createElement('p')
    returnMessageH.textContent = message;
    returnMessageH.classList.add("text-center");
    returnMessage.appendChild(returnMessageH)
}

form.addEventListener("submit", async (e) => {
    e.preventDefault()
    const username = form.username.value
    const email = form.email.value
    const password = form.password.value
    const myHeaders = new Headers();
    myHeaders.append("Content-Type", "application/json")

    const raw = JSON.stringify({
        "username": username,
        "email": email,
        "hash": password
    });

    const requestOptions = {
        method: 'POST',
        headers: myHeaders,
        body: raw,
        redirect: 'follow'
    };

    const response = await fetch(
        `${baseUrl}/api/auth/signup`,
        requestOptions);
    const result = await response.json()
    if (response.status == 201) {
        const message = 'Please, check your email to activate your account'
        window.location = `/templates/login.html/?message=${message}`
    }
    if (response.status == 409) {
        const message = encodeURIComponent(`An account with the same email address or username already exists`)
        window.location = `/templates/signup.html?message=${message}`
    } else {
        returnMessage.textContent = result.detail[0].msg || result.message;
    }

})