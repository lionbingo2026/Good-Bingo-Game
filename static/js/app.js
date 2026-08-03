// Good Bingo Game Telegram Mini App

const tg = window.Telegram.WebApp;

// Tell Telegram the app is ready
tg.ready();

// Expand Mini App to full screen
tg.expand();


// Get Telegram user information
const user = tg.initDataUnsafe?.user;

if (user) {
    document.getElementById("welcome").innerHTML =
        `Welcome, ${user.first_name}! 🎲`;
}


// Join game button
function startGame() {
    tg.showAlert("🎱 Joining Good Bingo Game...");

    // Later connect this to your Flask game API
    // fetch("/api/join")
}


// Refresh game data
function refreshGame() {
    location.reload();
}
