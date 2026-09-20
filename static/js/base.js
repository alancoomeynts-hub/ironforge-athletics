document.addEventListener('DOMContentLoaded', function() {

    // Initialize Bootstrap tooltips
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        tooltipTriggerList.forEach(function (tooltipTriggerEl) {
            new bootstrap.Tooltip(tooltipTriggerEl)
        });

        /* display toast messages from the server */
        const toast = document.querySelectorAll('.toast');
        toast.forEach(element => {
            bootstrap.Toast.getOrCreateInstance(element).show();
        });

        initialiseRatingRadio();
    });

function showToast(message,type) {
    /* Show a toast message with a custom class.
    * @param {string} message - The message to display in the toast.
    * @param {string} type - The type of toast (success, error, warning, info).
    */

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

function initialiseRatingRadio(){
        /* Update the displayed star rating when a rating radio input changes. */

        const ratingValue = document.getElementById("rating-value");
        const ratingInputs = document.querySelectorAll('input[name="rating"]');

        if (!ratingInputs.length || !ratingValue) {
        return;
        }

        const stars = ratingValue.querySelectorAll("i");

        ratingInputs.forEach((input) => {
            input.addEventListener("change", () => {
                const rating = Number(input.value);
                stars.forEach((star, index) => {
                    star.className= index < rating?"fa-solid fa-star review__star":"fa-regular fa-star";
                });
            });
        });


}