import {baseUrl} from './config.js';

const form = document.forms[0]

const token = localStorage.getItem("accessToken")

if (!token) {
    window.location.href = "/templates/login.html";
}

console.log('token', token)

form.addEventListener("submit", async(e) => {
    e.preventDefault()
    console.log('here??', form, form.file.value, form.description.value, form.tags.value)
    const description = form.description.value
    const tags = form.tags.value
    const url = form.file.value

    const myHeaders = new Headers();
    myHeaders.append(
        "Authorization",
        `Bearer ${token}`);

    // const urlencoded = new URLSearchParams();
    // urlencoded.append("username", username);
    // urlencoded.append("password", password);

    var requestOptions = {
        method: 'POST',
        headers: myHeaders,
        body: {
            description: description,
            tags: tags,
            url: url
        },
        redirect: 'follow'
    };

    const response = await fetch(
        `${baseUrl}/api/photos`,
        requestOptions);
    if (response.status == 200) {
        const result = await response.json()
    }
})