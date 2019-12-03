window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

const venueDeleteButtons = document.querySelectorAll('.venue-delete');
venueDeleteButtons.forEach(button => {
  button.onclick = e => {
      const venue_id = e.target.dataset['id'];
      console.log(venue_id)
      fetch(`/venues/${venue_id}/delete`, {
          method: 'POST',
      })
      .then(() => {
          console.log('delete successful')
      })
      .catch((e) => {
          console.log(e) ;
      })
  }
});
