import {baseUrl} from './config.js';

const form = document.forms[0]

const token = localStorage.getItem("accessToken")

if (!token) {
    window.location.href = "/templates/login.html";
}

const message = document.getElementById("message");

form.addEventListener("submit", async (e) => {
    e.preventDefault()
    const description = form.description.value
    const tags = form.tags.value.split(" ");

    const myHeaders = new Headers();
    myHeaders.append(
        "Authorization",
        `Bearer ${token}`);

    const fileInput = document.getElementById('file');
    const file = fileInput.files[0];

    const formData = new FormData();
    formData.append('description', description);
    formData.append('tags', tags);
    formData.append('file', file);

    const requestOptions = {
        method: 'POST',
        headers: myHeaders,
        body: formData
    };
    const response = await fetch(
        `${baseUrl}/api/photos`,
        requestOptions);

    if (response.status == 200) {
        message.textContent = "Image uploaded successfully";
        message.className = "text-success";
    }
    if (response.status === 401) {
        window.location = '/templates/login.html';
    }


})