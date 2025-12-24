document.addEventListener("DOMContentLoaded", () => {
    const input = document.querySelector("input[type=file]");
    const box = document.querySelector(".upload-box");

    if (input) {
        input.addEventListener("change", () => {
            if (input.files.length > 0) {
                const p = document.createElement("p");
                p.innerText = "Selected: " + input.files[0].name;
                box.appendChild(p);
            }
        });
    }
});
