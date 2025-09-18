const genreButtons = document.querySelectorAll('.genre-button');
const startButton = document.querySelector('.start-button');
const hiddenField = document.getElementById('auswahl-feld');

let deaktivierteGenres = [];

genreButtons.forEach(button => {
    button.addEventListener('click', () => {
        const genre = button.querySelector('img').alt;

        if (deaktivierteGenres.includes(genre)) {
            deaktivierteGenres = deaktivierteGenres.filter(g => g !== genre);
        } else {
            deaktivierteGenres.push(genre);
        }

        button.classList.toggle('deaktiviert');
    });
});

startButton.addEventListener('click', (event) => {
    event.preventDefault();

    hiddenField.value = JSON.stringify(deaktivierteGenres);

    const buttonImage = document.getElementById('start-button-image');
    buttonImage.src = "/static/pictures/filmklappe_zu.png";  // <-- Direktes Pfad statt Jinja-Ausdruck!

    setTimeout(() => {
        hiddenField.form.submit();
    }, 1300);
});
