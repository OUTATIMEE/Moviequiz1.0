const Movies = document.querySelectorAll(".Poster");

let clickOrder = [];
let counter = 1

Movies.forEach(poster => {
    poster.addEventListener('click', () => {
        const movieId = poster.id;

        const wrapper = poster.parentElement

        if(wrapper.querySelector(".nummer-overlay")) return; // wenn ein Poster schon durchnummeriert ist dann wird es nicht ein zweites mal der Liste hinzugefügt und nicht nocheinmal nummeriert

        const nummer = document.createElement("div");
        nummer.classList.add("nummer-overlay");
        nummer.innerText = counter;

        wrapper.appendChild(nummer);
        clickOrder.push(movieId);
        counter++;
    });

    const wrapper = poster.parentElement;

    wrapper.addEventListener('contextmenu', (event) => {
    event.preventDefault();


    const nummer = wrapper.querySelector(".nummer-overlay");


    if (!nummer) return;

    if (nummer.innerText == counter - 1) {
        nummer.remove();
        counter--;
        clickOrder.pop();
    }
    });
});

const formular = document.getElementById("auswahlForm");
const auswahlInput = document.getElementById("auswahlInput");

formular.addEventListener("submit", async (event) => {
  event.preventDefault();


  auswahlInput.value = JSON.stringify(clickOrder);


  const resp = await fetch("/runde-pruefen", {
    method: "POST",
    body: new FormData(formular)
  });


const result = await resp.json();

const scoreAnzeiger = document.getElementById("score-anzeige");
let aktuellePunktzahl = 0;


result.ergebnisse.forEach(eintrag => {
    const poster = document.getElementById(eintrag.poster_number);
    const wrapper = poster.parentElement;

    // Vorherige Nummern-Overlays entfernen
    const alteNummer = wrapper.querySelector(".nummer-overlay");
    if (alteNummer) alteNummer.remove();

    // Neues Ergebnis-Overlay erstellen
    const overlay = document.createElement("div");
    overlay.classList.add("nummer-overlay");
    overlay.innerHTML = `${eintrag.release_date} <br> ${eintrag.punkte} Punkte`;

    overlay.classList.add(eintrag.korrekt ? "erfolg" : "fehler");


    wrapper.appendChild(overlay);


    if (eintrag.korrekt) {
        aktuellePunktzahl += eintrag.punkte;
        scoreAnzeiger.innerText = `Gesamtpunktzahl: ${result.gesamt}`;
    }
});


document.getElementById("neue-runde-button").style.display = "block";
const neueRundeButton = document.getElementById("neue-runde-button");

neueRundeButton.addEventListener("click", () => {
    window.location.href = "/neue_runde";
});

});


