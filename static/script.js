// ✅ Fetch Kits
async function fetchKits() {
    try {
        let response = await fetch("/get-kits");
        if (!response.ok) throw new Error("Failed to load kits");

        let kits = await response.json();
        let container = document.getElementById("kits-container");
        container.innerHTML = "";

        kits.forEach(kit => {
            let kitElement = document.createElement("div");
            kitElement.classList.add("bg-white", "p-4", "rounded-lg", "shadow-md", "text-center", "m-2");
            kitElement.innerHTML = `
                <img src="${kit.image}" alt="${kit.name}" class="w-40 mx-auto rounded-lg shadow">
                <h2 class="text-lg font-bold mt-2">${kit.name}</h2>
                <button onclick="customizeKit('${kit.id}')" class="bg-blue-500 text-white px-4 py-2 mt-2 rounded-md hover:bg-blue-600 transition">
                    Customize
                </button>
            `;
            container.appendChild(kitElement);
        });
    } catch (error) {
        console.error("Error loading kits:", error);
    }
}

// ✅ Upload a Kit
async function uploadKit() {
    try {
        let kitName = document.getElementById('kitName').value;
        let kitImage = document.getElementById('kitImage').files[0];

        let formData = new FormData();
        formData.append("name", kitName);
        formData.append("image", kitImage);

        let response = await fetch("/upload-kit", { method: "POST", body: formData });
        if (!response.ok) throw new Error("Failed to upload kit");

        let result = await response.json();
        alert(result.message);
        fetchKits();
    } catch (error) {
        console.error("Error uploading kit:", error);
    }
}

// ✅ Customize a Kit
async function customizeKit(kitId) {
    let newColor = prompt("Enter customization details:");
    if (!newColor) return;

    try {
        let response = await fetch("/customize-kit", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ kit_id: kitId, color: newColor })
        });

        if (!response.ok) throw new Error("Failed to customize kit");

        let result = await response.json();
        alert(result.message);
    } catch (error) {
        console.error("Error customizing kit:", error);
    }
}

// ✅ Fetch Football Players from EC2 API
async function fetchPlayers() {
    try {
        let response = await fetch("http://playersapi.us-east-1.elasticbeanstalk.com/api/players");
        if (!response.ok) throw new Error("Failed to load players from EC2 API");

        let players = await response.json();
        let container = document.getElementById("players-container");
        container.innerHTML = "";

        players.forEach(player => {
            let playerCard = document.createElement("div");
            playerCard.classList.add("bg-white", "p-4", "rounded-lg", "shadow-md", "text-center", "m-2");
            playerCard.innerHTML = `
                <h2 class="text-lg font-bold text-gray-800">${player.name}</h2>
                <p class="text-gray-600">🏆 Team: ${player.team}</p>
                <p class="text-gray-600">📍 Position: ${player.position}</p>
                <p class="text-gray-600">🌍 Nationality: ${player.nationality}</p>
            `;
            container.appendChild(playerCard);
        });
    } catch (error) {
        console.error("Error loading players from EC2:", error);
    }
}

// ✅ Load Kits & Players on Page Load
window.onload = function() {
    fetchKits();
    let playersContainer = document.getElementById("players-container");
    if (playersContainer) {
        fetchPlayers();
    }
};


