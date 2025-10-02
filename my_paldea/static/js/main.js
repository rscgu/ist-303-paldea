document.addEventListener("DOMContentLoaded", () => {
    console.log("main.js loaded!");

    // Example: simple alert for demonstration
    const alertButton = document.getElementById("alertButton");
    if (alertButton) {
        alertButton.addEventListener("click", () => {
            alert("Button clicked!");
        });
    }

    // Example: toggle visibility of an element with id 'toggleDiv'
    const toggleButton = document.getElementById("toggleButton");
    const toggleDiv = document.getElementById("toggleDiv");
    if (toggleButton && toggleDiv) {
        toggleButton.addEventListener("click", () => {
            toggleDiv.style.display = toggleDiv.style.display === "none" ? "block" : "none";
        });
    }
});