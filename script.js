// script.js

document.addEventListener('DOMContentLoaded', function() {

    const sections = document.querySelectorAll('section');

    sections.forEach(section => {

        section.addEventListener('mouseenter', () => {

            section.style.transform = 'scale(1.02)';

            section.style.transition = 'transform 0.3s ease';

        });

        section.addEventListener('mouseleave', () => {

            section.style.transform = 'scale(1)';

        });

    });

    const contactForm = document.getElementById('contact-form');

    contactForm.addEventListener('submit', function(event) {

        event.preventDefault();

        alert('تم إرسال الرسالة بنجاح!');

        contactForm.reset();

    });

});