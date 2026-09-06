const API_URL = "";

function showLogin() {

    document
        .getElementById("loginForm")
        .classList.remove("hidden");

    document
        .getElementById("registerForm")
        .classList.add("hidden");

    document
        .getElementById("loginTab")
        .classList.add("active");

    document
        .getElementById("registerTab")
        .classList.remove("active");

    clearMessage();
}


function showRegister() {

    document
        .getElementById("loginForm")
        .classList.add("hidden");

    document
        .getElementById("registerForm")
        .classList.remove("hidden");

    document
        .getElementById("loginTab")
        .classList.remove("active");

    document
        .getElementById("registerTab")
        .classList.add("active");

    clearMessage();
}


function showMessage(message) {

    document
        .getElementById("message")
        .textContent = message;
}


function clearMessage() {

    document
        .getElementById("message")
        .textContent = "";
}


async function register(event) {

    event.preventDefault();

    const name =
        document.getElementById("registerName").value;

    const email =
        document.getElementById("registerEmail").value;

    const password =
        document.getElementById("registerPassword").value;


    try {

        const response = await fetch(
            "/api/auth/register",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    name: name,
                    email: email,
                    password: password
                })
            }
        );


        const data = await response.json();


        if (!response.ok) {

            showMessage(
                data.error || "Registration failed"
            );

            return;
        }


        showMessage(
            "Registration successful. Please login."
        );


        showLogin();


        document.getElementById(
            "loginEmail"
        ).value = email;


    } catch (error) {

        showMessage(
            "Server connection failed"
        );

        console.error(error);
    }
}


async function login(event) {

    event.preventDefault();

    const email =
        document.getElementById("loginEmail").value;

    const password =
        document.getElementById("loginPassword").value;


    try {

        const response = await fetch(
            "/api/auth/login",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    email: email,
                    password: password
                })
            }
        );


        const data = await response.json();


        if (!response.ok) {

            showMessage(
                data.error || "Login failed"
            );

            return;
        }


        localStorage.setItem(
            "access_token",
            data.access_token
        );


        showMessage(
            "Login successful!"
        );

        setTimeout(()=> {
            window.location.href ="/dashboard";
        },500)


        console.log(
            "Login response:",
            data
        );


    } catch (error) {

        showMessage(
            "Server connection failed"
        );

        console.error(error);
    }
}