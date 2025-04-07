const sign_in_btn = document.querySelector("#sign-in-btn");
const sign_up_btn = document.querySelector("#sign-up-btn");
const container = document.querySelector(".container");

sign_up_btn.addEventListener("click", () => {
    container.classList.add("sign-up-mode");
});

sign_in_btn.addEventListener("click", () => {
    container.classList.remove("sign-up-mode");
});

function onSigninClicked() {
    const usernameInput = document.getElementById("sign-in-username-holder");
    const passwordInput = document.getElementById("sign-in-password-holder");
    const username = document.getElementById("sign-in-username").value;
    const password = document.getElementById("sign-in-password").value;
    const err_msg = document.getElementById("sign-in-error-msg");

    fetch(`/verify/${username}/${password}`, {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            window.location.href = '../../templates/camera_manager.html';
        } else {
            usernameInput.classList.add('input-error');
            passwordInput.classList.add('input-error');
            err_msg.style.opacity = 1;

            setTimeout(() => {
                usernameInput.classList.remove('input-error');
                passwordInput.classList.remove('input-error');
            }, 500);
            setTimeout(() => {
                err_msg.style.opacity = 0;
            }, 3000);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function onSignupClicked(){
    alert("function under construction")
}

function onFacebookClicked(){
    alert("function under construction")
}

function onGoogleClicked(){
    alert("function under construction")
}

function onTwitterClicked(){
    alert("function under construction")
}

function onLinkedinClicked(){
    alert("function under construction")
}
