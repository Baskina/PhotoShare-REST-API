import {getTags} from "./tag.js";

const token = localStorage.getItem("accessToken");
if (!token) {
    window.location.href = "/templates/login.html";
}
const aboutUser = document.getElementById("about_user")
const userImages = document.getElementById("user_images")
import {baseUrl} from './config.js';


const urlParams = new URLSearchParams(window.location.search);
const username = urlParams.get('username');

const getInfoUser = async () => {
    const myHeaders = new Headers();
    myHeaders.append(
        "Authorization",
        `Bearer ${token}`);

    const requestOptions = {
        method: 'GET',
        headers: myHeaders,
        redirect: 'follow'
    };

    const response = await fetch(`${baseUrl}/api/users/me`, requestOptions);
    if (response.status === 200) {
        const result = await response.json();
        aboutUser.innerHTML = ""
        const img = document.createElement('img');
        img.src = result.avatar;
        const avatar = document.createElement('img')
        avatar.src = result.avatar;
        avatar.style.borderRadius = '20%';
        avatar.style.width = '150px';
        avatar.style.height = 'auto';


        const el1 = document.createElement('div')
        el1.className = ""

        const el2 = document.createElement('div')
        el2.className = "mb-4"
        el2.style.display = "flex";

        const avatarDiv = document.createElement('div')
        avatarDiv.className = ""

        const avatarSpan = document.createElement('span');
        avatarSpan.innerHTML = avatar.outerHTML;
        avatarDiv.appendChild(avatarSpan)

        const aboutUserDiv = document.createElement('div')
        aboutUserDiv.className = "col-lg-6 pl-5 text-body-secondary"

        const userNameH = document.createElement('h4')
        userNameH.className = "text-left"
        userNameH.textContent = result.username

        aboutUserDiv.appendChild(userNameH)


        const userInfoUl = document.createElement("div");

        const userEmailLi = document.createElement("div");
        userEmailLi.textContent = `Email: ${result.email}`;
        userEmailLi.classList.add("text-left");
        userInfoUl.appendChild(userEmailLi)


        const userRoleLi = document.createElement("div");
        userRoleLi.textContent = `Role: ${result.role}`;
        userRoleLi.classList.add("text-left");
        userInfoUl.appendChild(userRoleLi)

        aboutUserDiv.appendChild(userInfoUl)
        el2.appendChild(avatarDiv)
        el2.appendChild(aboutUserDiv)
        el1.appendChild(el2)
        aboutUser.appendChild(el1)
        return result;
    }
    if (response.status === 401) {
        window.location = '/templates/login.html';
    }

}
const user = await getInfoUser();

const getUserImages = async (user) => {
    const user_id = user?.id;
    const myHeaders = new Headers();
    myHeaders.append(
        "Authorization",
        `Bearer ${token}`);

    const requestOptions = {
        method: 'GET',
        headers: myHeaders,
        redirect: 'follow'
    };

    const response = await fetch(`${baseUrl}/api/photos/search/${user_id}/?limit=50`, requestOptions);
    if (response.status === 200) {
        const result = await response.json();
        userImages.innerHTML = ""
        for (const image of result) {
            const img = document.createElement('img');
            img.src = image?.image;

            const el = document.createElement('div');
            el.className = 'card-content rounded-2 shadow link-style';

            el.addEventListener('click', () => {
                window.location = `/templates/image.html?id=${image?.id}`
            });

            const avatarUserNameDiv = document.createElement('div');
            avatarUserNameDiv.className = "author mb-2 mt-2"

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
            topicsDiv.className = '';
            topicsDiv.textContent = 'Tags: ';

            const tags = await getTags(image.id);
            if (tags) {
                for (const tag of tags) {
                    const tagLink = document.createElement('span');
                    tagLink.style.color = 'blue';
                    tagLink.textContent = `#${tag.name} `;
                    topicsDiv.appendChild(tagLink);
                }
            }


            imagesDescriptionDiv.appendChild(topicsDiv)

            el.appendChild(avatarUserNameDiv);
            el.appendChild(photoDiv);
            el.appendChild(imagesDescriptionDiv);

            userImages.appendChild(el);
        }
    }
    if (response.status === 401) {
        window.location = '/templates/login.html';
    }
}

getUserImages(user);

