import {baseUrl} from './config.js';

const token = localStorage.getItem("accessToken");

if (!token) {
    window.location.href = "/templates/login.html";
}

const tags = document.getElementById("tags")

export const getTags = async (photo_id) => {
    const myHeaders = new Headers();
    myHeaders.append(
        "Authorization",
        `Bearer ${token}`);

    const requestOptions = {
        method: 'GET',
        headers: myHeaders,
        redirect: 'follow'
    };


    const response = await fetch(`${baseUrl}/tags/?photo_id=${photo_id}`, requestOptions);
    if (response.status === 200) {
        const result = await response.json()
        return result
    }

    if (response.status === 401) {
        window.location = '/templates/login.html';
    }
}

