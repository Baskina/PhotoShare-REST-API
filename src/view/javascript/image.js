import {getTags} from "./tag.js";

console.log("Run");
import {baseUrl} from './config.js';

const form = document.forms[0]

const token = localStorage.getItem("accessToken")

if (!token) {
    window.location.href = "/templates/login.html";
}


const urlParams = new URLSearchParams(window.location.search);
const photo_id = urlParams.get("id");

const container = document.getElementById("image")

const commentsContainer = document.getElementById("comments")

const message = document.getElementById("message");


const getUserById = async (user_id) => {
    const myHeaders = new Headers();
    myHeaders.append(
        "Authorization",
        `Bearer ${token}`);

    const requestOptions = {
        method: 'GET',
        headers: myHeaders,
        redirect: 'follow'
    };

    const response = await fetch(`${baseUrl}/api/users/${user_id}`, requestOptions);
    if (response.status === 200) {
        return await response.json();
    }
    if (response.status === 401) {
        window.location = '/templates/login.html';
    }
}


const getImage = async (photo_id) => {
    const myHeaders = new Headers();
    myHeaders.append(
        "Authorization",
        `Bearer ${token}`);

    const requestOptions = {
        method: 'GET',
        headers: myHeaders,
        redirect: 'follow'
    };


    const response = await fetch(`${baseUrl}/api/photos/${photo_id}`, requestOptions)
    if (response.status === 200) {
        const image = await response.json()
        container.innerHTML = ""
        const img = document.createElement('img');
        img.src = image?.image;
        img.className = 'w-100 mb-5';
        const user = await getUserById(image?.user_id);

        const avatar = document.createElement('img');
        avatar.src = user?.avatar;
        avatar.style.borderRadius = '20%';
        avatar.style.width = '30px';
        avatar.style.height = '30px';

        const el = document.createElement('div');
        el.className = 'mb-5';

        const avatarUserNameDiv = document.createElement('div');
        avatarUserNameDiv.className = "author mb-2 mt-2"
        const avatarSpan = document.createElement('span');
        avatarSpan.innerHTML = avatar.outerHTML;


        const photoDiv = document.createElement('div');
        const photoLink = document.createElement('a');
        photoLink.className = 'photo';
        photoLink.innerHTML = img.outerHTML;
        photoDiv.appendChild(photoLink);

        const imagesDescriptionDiv = document.createElement('div');
        imagesDescriptionDiv.className = "some_class mb-2"
        const descriptionSpan = document.createElement('span');
        descriptionSpan.textContent = `Description: ${image.description}`;
        imagesDescriptionDiv.appendChild(descriptionSpan)

        const imageRatingDiv = document.createElement('div');
        const imageRating = document.createElement('a');
        const rating = image.rating;

        for (let i = 0; i < Math.round(rating); i++) {
            const star = document.createElement('span');
            star.textContent = '★';
            star.classList.add('star-small');
            imageRating.appendChild(star);
        }
        let unrated = ''
        if (rating === null) {
            unrated = ' unrated'
        }
        imageRatingDiv.textContent = `Rating: ${unrated}`;
        imageRatingDiv.appendChild(imageRating);
        imagesDescriptionDiv.appendChild(imageRatingDiv);

        const topicsDiv = document.createElement('div');
        topicsDiv.textContent = 'Tags: ';

        const tags = await getTags(image.id);
        if (tags) {
            for (const tag of tags) {
                const tagLink = document.createElement('span');
                tagLink.style.color = 'gray';
                tagLink.textContent = `#${tag.name} `;
                topicsDiv.appendChild(tagLink);
            }
        }

        imagesDescriptionDiv.appendChild(topicsDiv)

        el.appendChild(avatarUserNameDiv);
        el.appendChild(photoDiv);
        el.appendChild(imagesDescriptionDiv);

        container.appendChild(el);

    }

    if (response.status === 401) {
        window.location = '/templates/login.html';
    }
}


const getCurrentUser = async () => {
    const myHeaders = new Headers();
    myHeaders.append(
        "Authorization",
        `Bearer ${token}`);

    const requestOptions = {
        method: 'GET',
        headers: myHeaders,
        redirect: 'follow'
    };

    const response = await fetch(`${baseUrl}/api/users/me`, requestOptions)
    if (response.status === 200) {
        const result = await response.json()
        return result;
    }
    if (response.status === 401) {
        window.location = '/templates/login.html';
    }
}

form.addEventListener("submit", async (e) => {
    e.preventDefault()

    const comment = form.comment.value;
    const user = await getCurrentUser();

    const myHeaders = new Headers();
    myHeaders.append("Content-Type", "application/json");
    myHeaders.append(
        "Authorization",
        `Bearer ${token}`);

    const data = {
        text: comment,
        photo_id: photo_id
    }

    const requestOptions = {
        method: 'POST',
        headers: myHeaders,
        body: JSON.stringify(data),
        redirect: 'follow'
    };

    const response = await fetch(
        `${baseUrl}/api/comments/?user_id=${user.id}`,
        requestOptions);
    if (response.status == 200) {
        const result = await response.json();
        message.textContent = 'Comment was added successfully';
        message.className = "text-success";
    }
    if (response.status === 401) {
        window.location = '/templates/login.html';
    }
});

const getComments = async (photo_id) => {
    const myHeaders = new Headers();
    myHeaders.append(
        "Authorization",
        `Bearer ${token}`);

    const requestOptions = {
        method: 'GET',
        headers: myHeaders,
        redirect: 'follow'
    };

    const response = await fetch(`${baseUrl}/api/comments/${photo_id}`, requestOptions);
    if (response.status === 200) {
        const result = await response.json();
        commentsContainer.innerHTML = "";
        if (result.length === 0) {
            const el = document.createElement('div');
            el.textContent = 'No comments yet';
            el.className = 'mb-4'
            commentsContainer.appendChild(el)
        }
        for (const element of result) {
            const el = document.createElement('div');
            const time = document.createElement('span');
            const comment = document.createElement('p');
            time.textContent = element.created_at;
            time.style.color = 'gray';
            comment.textContent = element.text;


            commentsContainer.appendChild(time)
            commentsContainer.appendChild(comment)
        }
    }
    if (response.status === 401) {
        window.location = '/templates/login.html';
    }
}

getImage(photo_id);
getComments(photo_id)