function notificationClose() {
    var closeButton = document.querySelector('.popup-notification-close');
    closeButton.addEventListener('click', function() {
        var notification = this.closest('.notification-popup');
        notification.remove();
    });
};

function popupClose() {
    var closeButton = document.querySelector('.popup-newsletter-close');
    closeButton.addEventListener('click', function() {
        var notification = this.closest('.newsletter-popup');
        notification.remove();
    });
};

function TitleCount() {
    // Get all input boxes and text areas
    const inputFields = document.querySelectorAll(
      '.content-form-grid-input input[type="text"], .content-textarea-box textarea'
    );

    // Attach event listeners to each input field
    inputFields.forEach((inputField) => {
      // Get the corresponding character count span
      const characterCountSpan = inputField.nextElementSibling;

      // Update character count on input
      inputField.addEventListener("input", () => {
        const characterCount = inputField.value.length;
        const maxLength = inputField.getAttribute("maxlength");
        characterCountSpan.textContent = `${characterCount} / ${maxLength} Characters`;
      });
    });
}
