const fileInput = document.querySelector('input[type="file"]');
const uploadBox = document.querySelector('.upload-box');
const form = document.querySelector('form');
const button = document.querySelector('button');

if (fileInput) {
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            uploadBox.innerHTML = `
                <p>📄 Selected file</p>
                <strong>${fileInput.files[0].name}</strong>
            `;
        }
    });
}

if (form) {
    form.addEventListener('submit', () => {
        button.disabled = true;
        button.innerText = "⏳ Processing dataset…";
    });
}

window.onload = () => {
    const dashboard = document.querySelector('.dashboard');
    if (dashboard) {
        dashboard.scrollIntoView({ behavior: "smooth" });
    }
};
