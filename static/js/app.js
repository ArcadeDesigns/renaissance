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