console.log("Good Bingo Game loaded");


async function updateBoard() {

    try {

        const response = await fetch("/api/game");

        const data = await response.json();


        if (data.called_numbers) {

            document.getElementById("called").innerHTML =
                "🎱 Called: " + data.called_numbers.join(", ");

        }


    } catch (error) {

        console.log("Waiting for game data...");

    }

}


// Refresh board every 5 seconds
setInterval(updateBoard, 5000);


// Load once
updateBoard();
