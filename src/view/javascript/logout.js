console.log("Run")
import {baseUrl} from './config.js';

const logoutBtn = document.getElementById("logout");
logoutBtn.addEventListener("click", logout);

async function logout() {
    const url = `${baseUrl}/api/auth/logout`;
    const token = localStorage.getItem("accessToken");

    const requestOptions = {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`
        }
    };

    try {
        const response = await fetch(url, requestOptions);
        const data = await response.json();
        window.location.href = "/templates/logout.html";
        localStorage.clear()
    } catch (error) {
        console.log("Error:", error);
    }
}
