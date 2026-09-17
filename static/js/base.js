document.addEventListener('DOMContentLoaded', function() {

    // Initialize Bootstrap tooltips
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        tooltipTriggerList.forEach(function (tooltipTriggerEl) {
            new bootstrap.Tooltip(tooltipTriggerEl)
        });

        const toast = document.querySelectorAll('.toast');
        toast.forEach(element => {
            bootstrap.Toast.getOrCreateInstance(element).show();
        });

        initialiseRatingSlider();
    });

function showToast(message,type) {
    const toastContainer=document.getElementById('js-toast-container');
       if (!toastContainer) {
        console.error("Toast element not found.");
        return;
    }
    if(type===null){
        type="success";
    }

    const toastElement=document.createElement("div");
    toastElement.className=`toast align-items-center custom__toast--${type}`;

    toastElement.setAttribute("role", "alert");
    toastElement.setAttribute("aria-live", "assertive");
    toastElement.setAttribute("aria-atomic", "true");

    toastElement.innerHTML = `
        <div class="d-flex">
            <div class="toast-body"></div>
            <button
                type="button"
                class="btn-close btn-close-dark me-2 m-auto"
                data-bs-dismiss="toast"
                aria-label="Close"
            ></button>
        </div>
    `;

    toastElement.querySelector(".toast-body").textContent = message;
    toastContainer.appendChild(toastElement);

    const toast=bootstrap.Toast.getOrCreateInstance(toastElement,{delay:3000});
    toast.show();

    toastElement.addEventListener('hidden.bs.toast', function () {
        toastElement.remove();
    });
}

function initialiseRatingSlider(){
    const ratingInput = document.getElementById("id_rating");
        const ratingValue = document.getElementById("rating-value");

        if (!ratingInput || !ratingValue) {
        return;
        }

        function updateRatingValue() {
            ratingValue.textContent = ratingInput.value;
        }

        ratingInput.addEventListener("input", updateRatingValue);
        updateRatingValue();

}