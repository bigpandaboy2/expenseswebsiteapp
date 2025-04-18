document.addEventListener("DOMContentLoaded", () => {
    const usernameField = document.querySelector('#usernameField');
    const feedBackArea = document.querySelector('.invalid_feedback');

    const emailField = document.querySelector("#emailField");
    const emailFeedBackArea = document.querySelector(".emailFeedBackArea");

    const usernamesuccessOutput = document.querySelector(".usernamesuccessOutput");
    const showPasswordToggle = document.querySelector(".showPasswordToggle");
    const passwordField = document.querySelector("#passwordField");

    const submitBtn = document.querySelector(".submitBtn");

    if (showPasswordToggle && passwordField) {
        showPasswordToggle.addEventListener("click", () => {
            if (showPasswordToggle.textContent === "SHOW") {
                showPasswordToggle.textContent = "HIDE";
                passwordField.setAttribute("type", "text");
            } else {
                showPasswordToggle.textContent = "SHOW";
                passwordField.setAttribute("type", "password");
            }
        });
    }

    if (emailField && emailFeedBackArea && submitBtn) {
        emailField.addEventListener("keyup", (e) => {
            const emailVal = e.target.value;

            emailField.classList.remove('is-invalid');
            emailFeedBackArea.style.display = "none";

            if (emailVal.length > 0) {
                fetch("/authentication/validate-email", {
                    body: JSON.stringify({ email: emailVal }),
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                })
                .then(res => res.json())
                .then(data => {
                    console.log("data", data);
                    if (data.email_error) {
                        submitBtn.disabled = true;
                        emailField.classList.add('is-invalid');
                        emailFeedBackArea.style.display = "block";
                        emailFeedBackArea.innerHTML = `<p>${data.email_error}</p>`;
                    } else {
                        submitBtn.removeAttribute("disabled");
                    }
                });
            }
        });
    }

    if (usernameField && usernamesuccessOutput && feedBackArea && submitBtn) {
        usernameField.addEventListener("keyup", (e) => {
            const usernameVal = e.target.value;

            usernamesuccessOutput.style.display = 'block';
            usernamesuccessOutput.textContent = `Checking ${usernameVal}`;

            feedBackArea.style.display = "none";
            usernameField.classList.remove('is-invalid');

            if (usernameVal.length > 0) {
                fetch('/authentication/validate-username', {
                    body: JSON.stringify({ username: usernameVal }),
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                })
                .then(res => res.json())
                .then(data => {
                    usernamesuccessOutput.style.display = 'none';
                    if (data.username_error) {
                        usernameField.classList.add('is-invalid');
                        feedBackArea.style.display = "block";
                        feedBackArea.innerHTML = `<p>${data.username_error}</p>`;
                        submitBtn.disabled = true;
                    } else {
                        submitBtn.removeAttribute("disabled");
                    }
                });
            }
        });
    }
});