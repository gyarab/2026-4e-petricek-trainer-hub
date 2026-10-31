document.addEventListener("DOMContentLoaded", () => {
    const dialog = document.getElementById("videoDialog");
    if (!dialog) return;

    const frame = document.getElementById("videoFrame");
    const title = document.getElementById("videoTitle");
    const closeButton = document.getElementById("videoClose");

    document.addEventListener("click", (event) => {
        const target = event.target;
        if (!(target instanceof Element)) return;

        const button = target.closest("[data-video]");
        if (!button) return;
        title.textContent = button.dataset.title;
        frame.src = button.dataset.video;
        dialog.showModal();
    });

    closeButton.addEventListener("click", () => dialog.close());

    dialog.addEventListener("click", (event) => {
        if (event.target === dialog) dialog.close();
    });

    dialog.addEventListener("close", () => {
        frame.src = "";
    });
});
