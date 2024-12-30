import {baseUrl} from './config.js';

const token = localStorage.getItem("refreshToken")

if (!token) {
    window.location.href = "/templates/login.html";
}

const images = document.getElementById("images")

const urlParams = new URLSearchParams(window.location.search);
const message = urlParams.get("message");

const returnAnswer = document.getElementById("return_answer")

if (message) {
  returnAnswer.innerHTML = ""
  const returnAnswerDiv2 = document.createElement('div')
  returnAnswerDiv2.className = "modal-content rounded-4 shadow mb-2 mt-2"
  const returnAnswerDiv1 = document.createElement('div')
  returnAnswerDiv1.className = "col-md-12 py-2 align-items-centerv"
  const returnAnswerP = document.createElement('p')
  returnAnswerP.textContent = message;
  returnAnswerDiv1.appendChild(returnAnswerP)
  returnAnswerDiv2.appendChild(returnAnswerDiv1)
  returnAnswer.appendChild(returnAnswerDiv2)

}

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

  const response = await fetch(`${baseUrl}/api/users/users_id/${user_id}`, requestOptions)
  if (response.status === 200) {
    const result = await response.json()
    return result;
  }
}

const getUserByUserName = async (username) => {
  const myHeaders = new Headers();
  myHeaders.append(
    "Authorization",
    `Bearer ${token}`);

  const requestOptions = {
    method: 'GET',
    headers: myHeaders,
    redirect: 'follow'
  };

  const response = await fetch(`${baseUrl}/api/users/${username}`, requestOptions)
  if (response.status === 200) {
    const result = await response.json()
    return result;
  }
}

// const form = document.forms[0]
//
// form.addEventListener("submit", async (e) => {
//   e.preventDefault()
//   const searchValue = form.search_info.value
//   if (searchValue) {
//     const encodedSearchValue = encodeURIComponent(searchValue);
//     window.location = `/static/client_rest/search_info.html?search=${encodedSearchValue}`;
//   }
// })

//const form1 = document.forms[1];
//
//form1.addEventListener("submit", async (e) => {
//  e.preventDefault()
//  const openAiQuestion = form1.open_ai_form.value
//  if (openAiQuestion) {
//    const getAnswer = async () => {
//      const myHeaders = new Headers();
//      myHeaders.append(
//        "Authorization",
//        `Bearer ${token}`);
//
//      const requestOptions = {
//        method: 'GET',
//        headers: myHeaders,
//        redirect: 'follow'
//      };
//
//      const respons = await fetch(`${baseUrl}/api/openai/?data=${openAiQuestion}`, requestOptions)
//      if (respons.status == 200) {
//        answerAi = await respons.json()
//
//        const message = encodeURIComponent(answerAi)
//        window.location = `/static/client_rest/images.html?message=${message}`
//      }
//    }
//    getAnswer()
//  }
//
//})

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
    window.location = `/templates/image.html/${photo_id}`;
  }
};

const getImages = async () => {
  const myHeaders = new Headers();
  myHeaders.append(
    "Authorization",
    `Bearer ${token}`);

  const requestOptions = {
    method: 'GET',
    headers: myHeaders,
    redirect: 'follow'
  };


  const response = await fetch(`${baseUrl}/api/photos`, requestOptions)
  if (response.status === 200) {
    const result = await response.json()
    images.innerHTML = ""
    for (const image of result) {
      console.log('image', image)
      const img = document.createElement('img');
      img.src = image?.url;
      const user = image?.user_id ? await getUserById(image?.user_id) : null;

      const avatar = document.createElement('img');
      avatar.src = user?.avatar;
      avatar.style.borderRadius = '20%';
      avatar.style.width = '30px';
      avatar.style.height = '30px';

      const el = document.createElement('div');
      el.className = 'modal-content rounded-2 shadow link-style';

      el.addEventListener('click', () => {
        window.location = `/templates/image.html/${image?.url}`
      });

      const avatarUserNameDiv = document.createElement('div');
      avatarUserNameDiv.className = "author mb-2 mt-2"
      const avatarSpan = document.createElement('span');
      avatarSpan.innerHTML = avatar.outerHTML;


      const authorLink = document.createElement('a');
      authorLink.className = 'author';
      authorLink.textContent = user?.username;
      authorLink.href = `user_profile.html?username=${user?.username}`
      avatarUserNameDiv.appendChild(avatarSpan);
      avatarUserNameDiv.appendChild(authorLink);

      const photoDiv = document.createElement('div');
      const photoLink = document.createElement('a');
      photoLink.className = 'photo';      
      photoLink.innerHTML = img.outerHTML;
      photoLink.style.width = '200px';
      photoDiv.appendChild(photoLink);

      const imagesDescriptionDiv = document.createElement('div');
      imagesDescriptionDiv.className = "some_class mb-2"
      const descriptionSpan = document.createElement('span');
      descriptionSpan.textContent = image.description;
      imagesDescriptionDiv.appendChild(descriptionSpan)

      const imageRatingDiv = document.createElement('div');
      const imageRating = document.createElement('a');
      const rating = image.avg_rating;

      for (let i = 0; i < Math.round(rating); i++) {
        const star = document.createElement('span');
        star.textContent = '★';
        star.classList.add('star');
        imageRating.appendChild(star);
      }

      imageRatingDiv.textContent = `Rating: ${rating}`;
      imageRatingDiv.appendChild(imageRating);
      imagesDescriptionDiv.appendChild(imageRatingDiv);

      const topicsDiv = document.createElement('div');
      topicsDiv.className = 'node__topics';
      topicsDiv.textContent = 'Tags: ';

      if(image?.tags) {
        for (const tag of image.tags) {
          const tagLink = document.createElement('a');
          tagLink.className = 'btn mb-2 mb-md-0 btn-outline-danger btn-sm';
          tagLink.textContent = tag.name;
          topicsDiv.appendChild(tagLink);
        }
      }

      imagesDescriptionDiv.appendChild(topicsDiv)

      el.appendChild(avatarUserNameDiv);
      el.appendChild(photoDiv);
      el.appendChild(imagesDescriptionDiv);

      images.appendChild(el);

    }
  }

  if (response.status === 401) {
    window.location = '/templates/login.html';
  }
}
getImages();

