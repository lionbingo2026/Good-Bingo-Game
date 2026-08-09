"use strict";

const tg = window.Telegram?.WebApp || null;

let bingoCard = [];
let calledNumbers = [];
let joined = false;
let pollingTimer = null;

function initializeTelegram() {
if (!tg) return;

tg.ready();
tg.expand();

}

function showMessage(text) {
const message = document.getElementById("message");

if (!message) return;

message.textContent = text;
message.classList.add("show");

setTimeout(() => {
    message.classList.remove("show");
}, 3000);

}

function setStatus(text) {
const status = document.getElementById("gameStatus");

if (status) {
    status.textContent = text;
}

}

async function apiRequest(url, options = {}) {
const response = await fetch(url, {
headers: {
"Content-Type": "application/json"
},
...options
});

const data = await response.json().catch(() => ({}));

if (!response.ok) {
    throw new Error(
        data.error ||
        data.message ||
        `Server error: ${response.status}`
    );
}

return data;

}

function getTelegramUser() {
if (tg?.initDataUnsafe?.user) {
return tg.initDataUnsafe.user;
}

return null;
}

async function joinGame() {
const button = document.getElementById("joinButton");

if (button) button.disabled = true;

const user = getTelegramUser();

if (!user || !user.id) {
    showMessage(
        "Please open Good Bingo Game from the Telegram bot."
    );

    setStatus(
        "Telegram user information not available."
    );

    if (button) button.disabled = false;

    return;
}

try {
    const data = await apiRequest("/api/join", {
        method: "POST",
        body: JSON.stringify({
            telegram_id: user.id,
            username: user.username || "",
            first_name: user.first_name || "Player"
        })
    });

    joined = true;

    showMessage(
        data.message || "You joined the Bingo game!"
    );

    setStatus("You joined the game!");

    const bingoButton =
        document.getElementById("bingoButton");

    if (bingoButton) {
        bingoButton.disabled = false;
    }

    if (data.card) {
        bingoCard = normalizeCard(data.card);
        renderCard();
    }

    await refreshGame();

} catch (error) {
    showMessage(
        error.message || "Unable to join game."
    );

    if (button) button.disabled = false;
}

}

function normalizeCard(card) {
if (!Array.isArray(card)) {
return [];
}

if (
    card.length === 25 &&
    !Array.isArray(card[0])
) {
    const result = [];

    for (let i = 0; i < 25; i += 5) {
        result.push(card.slice(i, i + 5));
    }

    return result;
}

return card;

}

function renderCard() {
const board = document.getElementById("bingoBoard");

if (!board) return;

board.innerHTML = "";

if (
    !Array.isArray(bingoCard) ||
    bingoCard.length !== 5
) {
    return;
}

for (let row = 0; row < 5; row++) {
    for (let col = 0; col < 5; col++) {

        const value = bingoCard[row][col];

        const cell = document.createElement("button");

        cell.className = "cell";
        cell.textContent = value;

        if (row === 2 && col === 2) {
            cell.classList.add("free");
            cell.disabled = true;
        }

        const number = Number(value);

        if (
            Number.isInteger(number) &&
            calledNumbers.includes(number)
        ) {
            cell.classList.add("called");
        }

        cell.addEventListener("click", () => {
            if (!joined) {
                showMessage("Join the game first.");
                return;
            }

            cell.classList.toggle("selected");
        });

        board.appendChild(cell);
    }
}

}

async function refreshGame() {
try {
const data = await apiRequest("/api/game");

    updateGame(data);

} catch (error) {
    console.warn(
        "Game API unavailable:",
        error.message
    );

    setStatus("Waiting for game...");
}

}

function updateGame(data) {
if (!data) return;

const players =
    document.getElementById("players");

const cards =
    document.getElementById("cards");

const pot =
    document.getElementById("pot");

if (data.players !== undefined && players) {
    players.textContent = data.players;
}

if (data.cards !== undefined && cards) {
    cards.textContent = data.cards;
}

if (data.prize_pool !== undefined && pot) {
    pot.textContent = `${data.prize_pool} ETB`;
}

if (data.current_number !== undefined) {
    updateCurrentNumber(data.current_number);
}

if (Array.isArray(data.called_numbers)) {
    calledNumbers = data.called_numbers;

    renderCalledNumbers();
    renderCard();
}

if (data.status) {
    setStatus(data.status);
}

if (data.card) {
    bingoCard = normalizeCard(data.card);
    renderCard();
}

}

function updateCurrentNumber(number) {
const element =
document.getElementById("currentNumber");

if (!element) return;

if (
    number === null ||
    number === undefined
) {
    element.textContent = "—";
    return;
}

element.textContent = number;

}

function renderCalledNumbers() {
const container =
document.getElementById("calledNumbers");

if (!container) return;

container.innerHTML = "";

if (
    !calledNumbers ||
    calledNumbers.length === 0
) {
    container.textContent =
        "No numbers called yet.";
    return;
}

[...calledNumbers]
    .reverse()
    .forEach(number => {

        const ball =
            document.createElement("span");

        ball.className = "called-ball";
        ball.textContent = number;

        container.appendChild(ball);
    });

}

async function claimBingo() {
if (!joined) {
showMessage("Join the game first.");
return;
}

const button =
    document.getElementById("bingoButton");

if (button) button.disabled = true;

const user = getTelegramUser();

try {
    const data = await apiRequest("/api/bingo", {
        method: "POST",
        body: JSON.stringify({
            telegram_id: user.id,
            card: bingoCard
        })
    });

    showMessage(
        data.message ||
        data.error ||
        "Bingo claim submitted!"
    );

    if (data.success || data.bingo) {
        setStatus(
            data.message ||
            "🎉 Bingo claim submitted!"
        );
    } else {
        if (button) button.disabled = false;
    }

} catch (error) {
    showMessage(
        error.message ||
        "Unable to claim Bingo."
    );

    if (button) button.disabled = false;
}

}

function startPolling() {
if (pollingTimer) {
clearInterval(pollingTimer);
}

pollingTimer = setInterval(() => {
    refreshGame();
}, 3000);

}

function startApp() {
initializeTelegram();

renderCard();
renderCalledNumbers();

refreshGame();
startPolling();

}

document.addEventListener(
"DOMContentLoaded",
startApp
);
