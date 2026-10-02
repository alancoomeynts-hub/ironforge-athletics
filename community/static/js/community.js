document.addEventListener("DOMContentLoaded", () => {

    initialiseModals();

});

function initialiseModals() {
    const editCommentModal = document.getElementById("editCommentModal");
    if (editCommentModal) {
        editCommentModal.addEventListener("show.bs.modal", (event) => {
            const button = event.relatedTarget;

            document.getElementById("editCommentForm").action =
                button.dataset.editUrl;

            document.getElementById("editCommentContent").value =
                button.dataset.commentContent;
        });
    }

    const deleteCommentModal = document.getElementById("deleteCommentModal");

    if (deleteCommentModal) {
        deleteCommentModal.addEventListener("show.bs.modal", (event) => {
            const button = event.relatedTarget;

            document.getElementById("deleteCommentConfirm").action =
                button.dataset.deleteUrl;
        });
    }

    const editPostModal = document.getElementById("editPostModal");

    if (editPostModal) {
        editPostModal.addEventListener("show.bs.modal", (event) => {
            const button = event.relatedTarget;

            document.getElementById("editPostForm").action =
                button.dataset.editUrl;

            document.getElementById("editPostTitle").value =
                button.dataset.postTitle;

            document.getElementById("editPostContent").value =
                document
                    .getElementById("postContentForEdit")
                    .textContent
                    .trim();
        });
    }

    const deletePostModal = document.getElementById("deletePostModal");

    if (deletePostModal) {
        deletePostModal.addEventListener("show.bs.modal", (event) => {
            const button = event.relatedTarget;

            document.getElementById("deletePostConfirm").action =
                button.dataset.deleteUrl;

            document.getElementById("deletePostModalText").textContent =
                button.dataset.postTitle;
        });
    }
}
