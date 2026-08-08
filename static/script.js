// Good Bingo Game - Telegram Mini App
// static/script.js

"use strict";

// ============================================================
// TELEGRAM MINI APP
// ============================================================

const tg = window.Telegram?.WebApp;

if (tg) {
    tg.ready();
    tg.expand();
}

// ============================================================
// GAME STATE
// ============================================================

const state = {
    user: null,
    gameId: null,
    card: [],
    marked: [],
    calledNumbers: [],
    joined: false,
    gameRunning: false,
    loading: false
};

// ============================================================
// DOM HELPERS
// ============================================================

function $(id) {
    return document.getElementById(id);
}

function showMessage(message) {
    const box =
        $("message") ||
        $("status") ||
        $("game-message");

    if (box) {
        box.textContent = message;
        box.style.display = "block";
    } else {
        console.log(message);
    }
}

function setLoading(value) {
    state.loading = value;

    document.querySelectorAll("button").forEach(button => {
        button.disabled = value;
    });
}

// ============================================================
// TELEGRAM USER
// ============================================================

function getTelegramUser() {
    if (!tg || !tg.initDataUnsafe) {
        return null;
    }

    return tg.initDataUnsafe.user || null;
}

function displayUser() {
    const user = state.user;

    if (!user) {
        return;
    }

    const name =
        user.first_name ||
        user.username ||
        "Player";

    const username =
        user.username ? `@${user.username}` : "";

    const userNameElement =
        $("user-name") ||
        $("username") ||
        $("player-name");

    if (userNameElement) {
        userNameElement.textContent =
            username || name;
    }

    const playerElement = $("player");

    if (playerElement) {
        playerElement.textContent = name;
    }
}

// ============================================================
// API REQUEST
// ============================================================

async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            method: options.method || "GET",
            headers: {
                "Content-Type": "application/json",
                ...(options.headers || {})
            },
            body: options.body
                ? JSON.stringify(options.body)
                : undefined
        });

        const text = await response.text();

        let data;

        try {
            data = JSON.parse(text);
        } catch {
            data = {
                success: response.ok,
                message: text
            };
        }

        if (!response.ok) {
            throw new Error(
                data.message ||
                `Request failed: ${response.status}`
            );
        }

        return data;

    } catch (error) {
        console.error("API error:", error);
        throw error;
    }
}

// ============================================================
// CREATE BINGO CARD
// ============================================================

function generateLocalCard() {
    const columns = [
        [1, 15],
        [16, 30],
        [31, 45],
        [46, 60],
        [61, 75]
    ];

    const card = [];

    for (let row = 0; row < 5; row++) {
        const currentRow = [];

        for (let col = 0; col < 5; col++) {

            if (row === 2 && col === 2) {
                currentRow.push("FREE");
                continue;
            }

            const min = columns[col][0];
            const max = columns[col][1];

            let number;

            do {
                number =
                    Math.floor(
                        Math.random() *
                        (max - min + 1)
                    ) + min;
            } while (
                currentRow.includes(number) ||
                card.some(r => r[col] === number)
            );

            currentRow.push(number);
        }

        card.push(currentRow);
    }

    return card;
}

// ============================================================
// RENDER BINGO CARD
// ============================================================

function renderCard() {
    const board =
        $("bingo-card") ||
        $("card") ||
        $("bingo-board");

    if (!board) {
        console.warn("Bingo board element not found.");
        return;
    }

    board.innerHTML = "";

    board.classList.add("bingo-grid");

    state.card.forEach((row, rowIndex) => {

        row.forEach((number, colIndex) => {

            const cell = document.createElement("button");

            cell.type = "button";
            cell.className = "bingo-cell";

            cell.dataset.row = rowIndex;
            cell.dataset.col = colIndex;

            if (number === "FREE") {
                cell.textContent = "FREE";
                cell.classList.add("free");
                cell.classList.add("marked");
            } else {
                cell.textContent = number;
            }

            if (
                state.marked[rowIndex]?.[colIndex]
            ) {
                cell.classList.add("marked");
            }

            cell.addEventListener(
                "click",
                () => markCell(rowIndex, colIndex)
            );

            board.appendChild(cell);
        });
    });
}

// ============================================================
// MARK BINGO CELL
// ============================================================

function markCell(row, col) {
    const number = state.card[row][col];

    if (number === "FREE") {
        return;
    }

    if (!state.calledNumbers.includes(number)) {
        showMessage(
            `Number ${number} has not been called yet.`
        );
        return;
    }

    if (!state.marked[row]) {
        state.marked[row] = [];
    }

    state.marked[row][col] =
        !state.marked[row][col];

    renderCard();

    if (checkBingo()) {
        showMessage("🎉 BINGO! You have a winning card!");

        sendBingoClaim();
    }
}

// ============================================================
// BINGO CHECK
// ============================================================

function checkBingo() {

    // Rows
    for (let row = 0; row < 5; row++) {

        let complete = true;

        for (let col = 0; col < 5; col++) {

            if (
                row === 2 &&
                col === 2
            ) {
                continue;
            }

            if (
                !state.marked[row] ||
                !state.marked[row][col]
            ) {
                complete = false;
                break;
            }
        }

        if (complete) {
            return true;
        }
    }

    // Columns
    for (let col = 0; col < 5; col++) {

        let complete = true;

        for (let row = 0; row < 5; row++) {

            if (
                row === 2 &&
                col === 2
            ) {
                continue;
            }

            if (
                !state.marked[row] ||
                !state.marked[row][col]
            ) {
                complete = false;
                break;
            }
        }

        if (complete) {
            return true;
        }
    }

    // Diagonal 1
    let diagonal1 = true;

    for (let i = 0; i < 5; i++) {

        if (i === 2) {
            continue;
        }

        if (
            !state.marked[i] ||
            !state.marked[i][i]
        ) {
            diagonal1 = false;
            break;
        }
    }

    if (diagonal1) {
        return true;
    }

    // Diagonal 2
    let diagonal2 = true;

    for (let i = 0; i < 5; i++) {

        const col = 4 - i;

        if (
            i === 2
        ) {
            continue;
        }

        if (
            !state.marked[i] ||
            !state.marked[i][col]
        ) {
            diagonal2 = false;
            break;
        }
    }

    return diagonal2;
}

// ============================================================
// JOIN GAME
// ============================================================

async function joinGame() {

    if (state.loading) {
        return;
    }

    setLoading(true);

    try {

        const data = await apiRequest(
            "/api/join",
            {
                method: "POST",
                body: {
                    telegram_user_id:
                        state.user?.id || null
                }
            }
        );

        state.joined = true;

        if (data.game_id) {
            state.gameId = data.game_id;
        }

        if (data.card) {
            state.card = data.card;
        } else {
            state.card = generateLocalCard();
        }

        createMarkedArray();

        renderCard();

        showMessage(
            data.message ||
            "✅ You joined the Bingo game!"
        );

        updateJoinButton();

    } catch (error) {

        showMessage(
            `❌ ${error.message}`
        );

    } finally {

        setLoading(false);
    }
}

// ============================================================
// BINGO CLAIM
// ============================================================

async function sendBingoClaim() {

    try {

        const data = await apiRequest(
            "/api/bingo",
            {
                method: "POST",
                body: {
                    game_id: state.gameId,
                    telegram_user_id:
                        state.user?.id || null,
                    card: state.card,
                    marked: state.marked
                }
            }
        );

        if (data.success) {

            showMessage(
                data.message ||
                "🏆 Bingo claim submitted!"
            );

        } else {

            showMessage(
                data.message ||
                "Bingo claim was not accepted."
            );
        }

    } catch (error) {

        showMessage(
            `❌ ${error.message}`
        );
    }
}

// ============================================================
// MARKED ARRAY
// ============================================================

function createMarkedArray() {

    state.marked = [];

    for (let row = 0; row < 5; row++) {

        state.marked[row] = [];

        for (let col = 0; col < 5; col++) {

            state.marked[row][col] =
                row === 2 && col === 2;
        }
    }
}

// ============================================================
// CALLED NUMBERS
// ============================================================

function renderCalledNumbers() {

    const container =
        $("called-numbers") ||
        $("numbers") ||
        $("called");

    if (!container) {
        return;
    }

    container.innerHTML = "";

    state.calledNumbers.forEach(number => {

        const element =
            document.createElement("span");

        element.className = "called-number";
        element.textContent = number;

        container.appendChild(element);
    });
}

// ============================================================
// CURRENT NUMBER
// ============================================================

function showCurrentNumber(number) {

    const element =
        $("current-number") ||
        $("last-number") ||
        $("drawn-number");

    if (element) {
        element.textContent =
            number ?? "--";
    }
}

// ============================================================
// GET GAME STATUS
// ============================================================

async function getGameStatus() {

    try {

        const data = await apiRequest(
            "/api/game"
        );

        if (data.game_id) {
            state.gameId = data.game_id;
        }

        if (Array.isArray(data.called_numbers)) {

            state.calledNumbers =
                data.called_numbers;

            renderCalledNumbers();

            const last =
                state.calledNumbers[
                    state.calledNumbers.length - 1
                ];

            showCurrentNumber(last);
        }

        if (data.running !== undefined) {
            state.gameRunning = data.running;
        }

        if (data.card) {
            state.card = data.card;

            createMarkedArray();
            renderCard();
        }

        updateGameStatus(data);

    } catch (error) {

        console.warn(
            "Unable to get game status:",
            error
        );
    }
}

// ============================================================
// UPDATE GAME STATUS
// ============================================================

function updateGameStatus(data) {

    const element =
        $("game-status") ||
        $("status");

    if (!element) {
        return;
    }

    if (data.running) {

        element.textContent =
            "🟢 Game is running";

    } else {

        element.textContent =
            "🟡 Waiting for game";
    }
}

// ============================================================
// JOIN BUTTON
// ============================================================

function updateJoinButton() {

    const button =
        $("join-button") ||
        $("join-game") ||
        $("play-button");

    if (!button) {
        return;
    }

    if (state.joined) {

        button.textContent =
            "✅ Joined";

        button.disabled = true;

    } else {

        button.textContent =
            "🎲 Join Game";

        button.disabled = false;
    }
}

// ============================================================
// BUTTON EVENTS
// ============================================================

function setupButtons() {

    const joinButton =
        $("join-button") ||
        $("join-game") ||
        $("play-button");

    if (joinButton) {

        joinButton.addEventListener(
            "click",
            joinGame
        );
    }

    const bingoButton =
        $("bingo-button") ||
        $("claim-bingo") ||
        $("bingo");

    if (bingoButton) {

        bingoButton.addEventListener(
            "click",
            () => {

                if (checkBingo()) {
                    sendBingoClaim();
                } else {
                    showMessage(
                        "❌ You don't have Bingo yet."
                    );
                }
            }
        );
    }

    const refreshButton =
        $("refresh-button") ||
        $("refresh");

    if (refreshButton) {

        refreshButton.addEventListener(
            "click",
            getGameStatus
        );
    }
}

// ============================================================
// TELEGRAM MAIN BUTTON
// ============================================================

function setupTelegramButton() {

    if (!tg) {
        return;
    }

    if (!tg.MainButton) {
        return;
    }

    tg.MainButton.setText(
        "🎲 JOIN BINGO"
    );

    tg.MainButton.show();

    tg.MainButton.onClick(
        joinGame
    );
}

// ============================================================
// AUTO REFRESH
// ============================================================

function startGameUpdates() {

    getGameStatus();

    setInterval(
        getGameStatus,
        3000
    );
}

// ============================================================
// INIT
// ============================================================

function init() {

    console.log(
        "🎲 Good Bingo Game Mini App starting..."
    );

    state.user =
        getTelegramUser();

    displayUser();

    state.card =
        generateLocalCard();

    createMarkedArray();

    renderCard();

    setupButtons();

    updateJoinButton();

    setupTelegramButton();

    startGameUpdates();

    showMessage(
        "🎲 Welcome to Good Bingo Game!"
    );
}

// ============================================================
// START
// ============================================================

if (
    document.readyState === "loading"
) {

    document.addEventListener(
        "DOMContentLoaded",
        init
    );

} else {

    init();
}
