const registration = new URLSearchParams(window.location.hash.slice(1));
const bookingCode = registration.get('code');

if (bookingCode) {
  document.querySelector('#booking-code').textContent = bookingCode;
  document.querySelector('#booking-code-row').hidden = false;
}

if (registration.get('from') === 'home') {
  document.querySelector('#register-again').href = './index.html?dat-lich=1';
}
