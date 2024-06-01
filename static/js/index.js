function ImageSwiper() {
      const images = document.querySelectorAll('.renaissance-img');
      let currentIndex = 0;

      setInterval(() => {
        images[currentIndex].classList.remove('active');
        currentIndex = (currentIndex + 1) % images.length;
        images[currentIndex].classList.add('active');
      }, 5000); // 5 seconds interval
    }

    window.onload = cycleImages;