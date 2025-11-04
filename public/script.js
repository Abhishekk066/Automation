const form = document.getElementById("login");

form.addEventListener("submit", async function(event) {
    event.preventDefault();
    console.log("Form submitted");

    const userInput = document.getElementById("username");
    const passInput = document.getElementById("password");

    const username = userInput.value;
    const password = passInput.value;

    if (!username || !password) {
        alert("Username and password are required.");
        return;
    }

    try {
        const response = await fetch('/login', {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ username, password })
        });

        if (response.ok) {
            const data = await response.json();
            console.log("Login success:", data.message);
            userInput.value = "";
            passInput.value = "";
            
        } else {
            const errorData = await response.json();
            console.error("Login failed:", errorData);
            alert(errorData.message || "Login failed. Please try again.");
        }

    } catch (error) {
        console.error("Error during login:", error);
        alert("An error occurred. Please try again later.");
    }
});
