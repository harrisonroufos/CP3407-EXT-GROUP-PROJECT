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

function toggleFields() {
    let userType = document.getElementById("userType").value;
    let cleanerFields = document.querySelectorAll(".cleaner-only");

    if (userType === "cleaner") {
        cleanerFields.forEach(field => field.style.display = "block");
    } else {
        cleanerFields.forEach(field => field.style.display = "none");
    }
}

document.addEventListener("DOMContentLoaded", function () {
    toggleFields(); // Ensure correct visibility on load
});
document.addEventListener("DOMContentLoaded", function () {
    let userTypeDropdown = document.getElementById("userType");
    let experienceField = document.getElementById("experienceField");

    function toggleFields() {
        if (userTypeDropdown.value === "cleaner") {
            experienceField.style.display = "block";
        } else {
            experienceField.style.display = "none";
        }
    }

    // Run the function when the page loads
    toggleFields();

    // Add event listener for when dropdown changes
    userTypeDropdown.addEventListener("change", toggleFields);
});
