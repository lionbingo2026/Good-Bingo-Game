"use strict";

const tg = window.Telegram?.WebApp || null;

let bingoCard = [];
let calledNumbers = [];
let joined = false;
let pollingTimer = null;
let selectedCardNumber = null;
let availableCards = [];

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

function createCardPicker() {

const existing = document.getElementById("cardPicker");

if (existing) return;

const joinButton = document.getElementById("joinButton");

if (!joinButton) return;

const section = document.createElement("section");

section.id = "cardPicker";
section.className = "card";

section.innerHTML = `
    <div style="text-align:center;">
        <h3>🎫 Choose Your Bingo Card</h3>

        <p id="selectedCardText">
            Select one card from 1 to 300
        </p>

        <div
            id="cardChoices"
            style="
                display:grid;
                grid-template-columns:
                    repeat(5, minmax(45px, 1fr));
                gap:8px;
                max-height:360px;
                overflow-y:auto;
                padding:8px;
            "
        ></div>
    </div>
`;

joinButton.parentElement.parentElement.insertBefore(
    section,
    joinButton.parentElement
);

}

async function loadAvailableCards() {

createCardPicker();

const container =
    document.getElementById("cardChoices");

if (!container) return;

try {

    const data =
        await apiRequest("/api/cards");

    availableCards =
        Array.isArray(data.cards)
            ? data.cards
            : [];

    container.innerHTML = "";

    availableCards.forEach(cardNumber => {

        const button =
            document.createElement("button");

        button.type = "button";

        button.textContent =
            String(cardNumber).padStart(3, "0");

        button.style.padding = "10px 4px";
        button.style.cursor = "pointer";

        button.addEventListener(
            "click",
            () => {

                document
                    .querySelectorAll(
                        ".card-choice-button"
                    )
                    .forEach(btn => {
                        btn.style.fontWeight = "normal";
                    });

                selectedCardNumber =
                    cardNumber;

                button.style.fontWeight =
                    "bold";

                const selected =
                    document.getElementById(
                        "selectedCardText"
                    );

                if (selected) {

                    selected.textContent =
                        `Selected Card: ${String(
                            cardNumber
                        ).padStart(3, "0")}`;

                }

            }
        );

        button.className =
            "card-choice-button";

        container.appendChild(button);

    });

} catch (error) {

    console.warn(
        "Unable to load available cards:",
        error.message
    );

}

}

async function joinGame() {

const button =
    document.getElementById("joinButton");

if (button) button.disabled = true;

if (!selectedCardNumber) {

    showMessage(
        "Please choose a Bingo card first."
    );

    if (button) button.disabled = false;

    return;
}

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

    const data =
        await apiRequest("/api/join", {

            method: "POST",

            body: JSON.stringify({

                telegram_id: user.id,

                username:
                    user.username || "",

                first_name:
                    user.first_name || "Player",

                card_number:
                    selectedCardNumber

            })

        });

    joined = true;

    showMessage(
        data.message ||
        `You joined with Card ${selectedCardNumber}!`
    );

    setStatus(
        "You joined the game!"
    );

    if (data.card) {

        bingoCard =
            normalizeCard(data.card);

        renderCard();

    }

    const bingoButton =
        document.getElementById(
            "bingoButton"
        );

    if (bingoButton) {
        bingoButton.disabled = false;
    }

    const picker =
        document.getElementById("cardPicker");

    if (picker) {
        picker.style.display = "none";
    }

    if (button) {
        button.textContent =
            `🎫 Card ${String(
                data.card_number ||
                selectedCardNumber
            ).padStart(3, "0")}`;

        button.disabled = true;
    }

    await refreshGame();

} catch (error) {

    showMessage(
        error.message ||
        "Unable to join game."
    );

    if (button) button.disabled = false;

    // Refresh because another player may
    // have taken the selected card.
    await loadAvailableCards();

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

async function startApp() {

initializeTelegram();

renderCard();
renderCalledNumbers();

await loadAvailableCards();

await refreshGame();

startPolling();

}

document.addEventListener(
"DOMContentLoaded",
startApp
);
