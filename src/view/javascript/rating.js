console.log("Run");
import {baseUrl} from "./config.js";


const token = localStorage.getItem("accessToken");
if (!token) {
    window.location.href = "/templates/login.html";
}
const urlParams = new URLSearchParams(window.location.search);
const photo_id = urlParams.get("id");

let stars =
    document.getElementsByClassName("star");

let error = document.getElementById("error");

const star_1 = document.getElementById("star1");
const star_2 = document.getElementById("star2");
const star_3 = document.getElementById("star3");
const star_4 = document.getElementById("star4");
const star_5 = document.getElementById("star5");

star_1.addEventListener("click", () => {
    press_rating(1);
});

star_2.addEventListener("click", () => {
    press_rating(2);
});

star_3.addEventListener("click", () => {
    press_rating(3);
});

star_4.addEventListener("click", () => {
    press_rating(4);
});

star_5.addEventListener("click", () => {
    press_rating(5);
});

// Function to update rating
const press_rating = async (n) => {
    if (!token) {
        window.location.href = "/templates/login.html";
    }
    remove();
    for (let i = 0; i < n; i++) {
        let cls = ''
        if (n == 1) cls = "one";
        else if (n == 2) cls = "two";
        else if (n == 3) cls = "three";
        else if (n == 4) cls = "four";
        else if (n == 5) cls = "five";
        stars[i].className = "star " + cls;
    }

    const myHeaders = new Headers();
    myHeaders.append("Content-Type", "application/json");
    myHeaders.append(
        "Authorization",
        `Bearer ${token}`);


    const requestOptions = {
        method: 'PUT',
        headers: myHeaders
    };


    const response = await fetch(`${baseUrl}/api/photos/${photo_id}/rating?like_value=${n}`, requestOptions);
    if (response.status === 400) {
        const result = await response.json()
        error.style.color = 'red';
        error.textContent = result.detail;
    }
    if (response.status === 401) {
        window.location = '/templates/login.html';
    }
}

// To remove the pre-applied styling
function remove() {
    let i = 0;
    while (i < 5) {
        stars[i].className = "star";
        i++;
    }
}