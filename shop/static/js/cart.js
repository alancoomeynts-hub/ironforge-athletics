document.addEventListener('DOMContentLoaded', function() {

    const updateForms=document.querySelectorAll('.shop__update-form');

    updateForm(updateForms);

    });

function updateForm(updateForms) {
    updateForms.forEach(form => {
        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            const productId = form.dataset.productId;
            const submitButton = form.querySelector('button[type="submit"]');
            submitButton.disabled = true;

            try {
                const response = await fetch(form.action, {
                    method: "POST",
                    body: new FormData(form),
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                    },
                    credentials: "same-origin",

                });

                const data = await response.json();

                if (!response.ok || !data.success) {
                    throw new Error(data.error || "Unable to update the cart.");
                }

                const lineTotal = document.querySelector(
                    `#line-total-${productId}`
                );

                if (lineTotal) {
                    lineTotal.textContent = `€${data.line_total}`;
                }

                const cartTotal = document.querySelector(
                    `#cart-total`
                );
                if (cartTotal) {
                    cartTotal.textContent = `€${data.cart_total}`;
                }

                const cartCount=document.querySelector('#cart-count');
                if(cartCount){
                    cartCount.textContent=`${data.cart_item_count}`;
                }

                showToast(data.message,data.type);

            } catch (error) {
                console.error(error);
            } finally {
                if (submitButton) {
                    submitButton.disabled = false;
                }
            }
        });
    });
}