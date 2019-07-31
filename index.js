const app = require("express")();
const http = require("http").createServer(app);
const io = require("socket.io")(http);
const loki = require("lokijs");
const fs = require("fs");
const spawn = require("child_process").spawn;
const validator = require("email-validator");
const bodyParser = require("body-parser");
const uuid = require("uuid/v4");

const TimeAgo = require("javascript-time-ago");
const en = require("javascript-time-ago/locale/en");
TimeAgo.addLocale(en);

const timeAgo = new TimeAgo("en-US");

app.use(bodyParser.urlencoded());

const couponIds = [15229, 15233, 15230, 15231, 15232, 15234, 15236, 15235, 15237, 15336, 15337, 15338, 15339, 15340, 15341, 15342, 15343, 15344, 15345, 15346, 15347, 15348, 15349, 15350, 15328];

const db = new loki("loki.json");
let attemptsCollection;

io.on("connection", socket => {
    socket.on("generate-coupon", msg => {
        const auth = msg.auth;
        const username = msg.username;
        const password = msg.password;
        const coupon = msg.coupon;
        const users = JSON.parse(fs.readFileSync("auth-keys.json"));

        const state = Validate(msg, users);

        if (!state.success) {
            socket.emit("server-error", state.error);
            return null;
        }

        const userAttempts = users[auth].attempts;

        let attempts = attemptsCollection.find({ auth: auth });
        let attemptsToday = GetTodaysAttempts(attempts);

        if (attemptsToday < userAttempts) {
            attemptsCollection.insert({
                auth: auth,
                username: username,
                created: new Date().toISOString()
            });

            db.saveDatabase();

            const python = spawn("python", ["main.py", username, password, couponIds[coupon]]);

            python.stdout.on("data", data => {
                socket.emit("server-data", data.toString());
            });
        } else {
            socket.emit("server-error", "You have used all your attempts the last 24 hours. Try again after midnight.");
            return null;
        }
    });
});

Validate = (msg, users) => {
    const auth = msg.auth;
    const username = msg.username;
    const coupon = msg.coupon;

    if (!validator.validate(username)) {
        return {
            error: "Email looks invalid. Are you sure you entered a valid email?",
            success: false
        };
    }

    if (!couponIds[coupon]) {
        return {
            error: "Coupon id out of bounce. Did you or we fuck up?",
            success: false
        };
    }

    if (!users[auth]) {
        return {
            error: "Auth key not found. Are you sure it's correct?",
            success: false
        };
    }

    return { success: true };
};

GetTodaysAttempts = attempts => {
    let attemptsToday = 0;

    attempts.forEach(attempt => {
        let created = new Date(attempt.created);
        let now = new Date(new Date().toISOString());

        if (created.getDate() == now.getDate() && created.getMonth() == now.getMonth() && created.getFullYear() && now.getFullYear()) {
            attemptsToday++;
        }
    });

    return attemptsToday;
};

db.loadDatabase({}, () => {
    attemptsCollection = db.getCollection("attempts");
});

app.get("/", function(req, res) {
    res.sendFile(__dirname + "/index.html");
});

http.listen(3000, function() {
    console.log("listening on *:3000");
});

