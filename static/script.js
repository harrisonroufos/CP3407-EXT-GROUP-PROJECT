// script.js - Basic form validation
document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    form.addEventListener("submit", function (event) {
        let username = document.querySelector("#username").value;
        let password = document.querySelector("#password").value;

        if (username.trim() === "" || password.trim() === "") {
            event.preventDefault();
            alert("Both fields are required.");
        }
    });
});
