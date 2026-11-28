// The site's settings, in one place.
window.TFGON_CONFIG = {
  // Where the application form sends applications (a DigitalOcean Function,
  // the next build). While this is empty the form sends nothing: it tells the
  // applicant so and shows the fallback address below.
  applicationEndpoint: '',

  // Shown when the form cannot send. Ed to supply the real address.
  fallbackEmail: '[FALLBACK EMAIL — Ed to supply]'
};
