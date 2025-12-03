// адрес твоего бэкенда
const apiBase = "http://127.0.0.1:8000";

function getUserIdFromUrl() {
  const params = new URLSearchParams(window.location.search);
  return params.get("uid") || "1"; // для теста по умолчанию uid=1
}

const userId = getUserIdFromUrl();

const balanceEl = document.getElementById("balance");
const energyEl = document.getElementById("energy");
const statusEl = document.getElementById("status");
const factoryEl = document.getElementById("factory");

async function fetchState() {
  try {
    const res = await fetch(`${apiBase}/state?user_id=${userId}`);
    const data = await res.json();
    if (data.ok) {
      balanceEl.textContent = data.balance;
      energyEl.textContent = data.energy;
      statusEl.textContent = "";
    } else {
      statusEl.textContent = data.error || "Ошибка загрузки состояния";
    }
  } catch (e) {
    console.error(e);
    statusEl.textContent = "Сервер недоступен";
  }
}

async function tapFactory() {
  try {
    const res = await fetch(`${apiBase}/tap`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: Number(userId) })
    });

    const data = await res.json();

    if (data.ok) {
      balanceEl.textContent = data.balance;
      energyEl.textContent = data.energy;
      statusEl.textContent = "";
    } else {
      statusEl.textContent = data.error || "Нет энергии";
    }
  } catch (e) {
    console.error(e);
    statusEl.textContent = "Сервер недоступен";
  }
}

factoryEl.addEventListener("click", tapFactory);

// при загрузке – подтянуть стейт
fetchState();
