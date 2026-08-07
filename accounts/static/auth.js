const loginForm = document.getElementById("login-form");
const registerForm = document.getElementById("register-form");

function showRegister() {
    loginForm.style.display = "none";
    registerForm.style.display = "block";
}

function showLogin() {
    registerForm.style.display = "none";
    loginForm.style.display = "block";
}