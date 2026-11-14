let form_modified = false;

const form = document.getElementById('form');

form.addEventListener('input', () => {
    form_modified = true;
});

form.addEventListener('submit', () => {
    form_modified = false;
});

window.addEventListener('beforeunload', (event) => {
    if (form_modified) {
        event.preventDefault();
        event.returnValue = '';
    }
});