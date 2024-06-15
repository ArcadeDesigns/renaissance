function scrollShadow() {
    let header = document.querySelector("nav");
    window.addEventListener("scroll", () => {
      header.classList.toggle("shadow", window.scrollY > 0);
    });
  }
  
  function OpenMenu() {
      const menuButton = document.querySelector('.menu-button');
      const closeButton = document.querySelector('.toggle-main-menu-close');
      const menu = document.querySelector('.toggle-menu-transparent');
  
      // Add event listener to the menu button
      menuButton.addEventListener('click', () => {
          menu.classList.add('active');
      });
  
      // Add event listener to the close button
      closeButton.addEventListener('click', () => {
          menu.classList.remove('active');
      });
  }

  function OpenResponsiveMenu() {
      const responsiveMenuButton = document.querySelector('.open-responsive-nav-view');
      const responsiveMenu = document.querySelector('.responsive-nav-view');
      const responsiveCloseButton = document.querySelector('.close-responsive-nav-view');
  
      // Add event listener to the menu button
      responsiveMenuButton.addEventListener('click', () => {
          responsiveMenu.classList.add('active');
      });
  
      // Add event listener to the close button
      responsiveCloseButton.addEventListener('click', () => {
          responsiveMenu.classList.remove('active');
      });
  }

function DropDownFunction() {
    // Select all header elements
    const headers = document.querySelectorAll('.drop-down-content-container-box-header');

    headers.forEach(header => {
        header.addEventListener('click', function() {
            // Toggle the active class on the content
            const content = this.nextElementSibling.nextElementSibling;
            content.classList.toggle('active');

            // Toggle the icons
            const downIcon = this.querySelector('.drop-down-btn:nth-child(2)');
            const upIcon = this.querySelector('.drop-down-btn:nth-child(3)');

            downIcon.classList.toggle('active');
            upIcon.classList.toggle('active');

            // If there is another open content, close it
            headers.forEach(otherHeader => {
                if (otherHeader !== this) {
                    const otherContent = otherHeader.nextElementSibling.nextElementSibling;
                    const otherDownIcon = otherHeader.querySelector('.drop-down-btn:nth-child(2)');
                    const otherUpIcon = otherHeader.querySelector('.drop-down-btn:nth-child(3)');
                    
                    if (otherContent.classList.contains('active')) {
                        otherContent.classList.remove('active');
                        otherDownIcon.classList.add('active');
                        otherUpIcon.classList.remove('active');
                    }
                }
            });
        });
    });
};
