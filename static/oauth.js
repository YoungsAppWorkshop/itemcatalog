// Google Sign In
var google_client_id = $('#google-sign-in-btn').data('google-client-id');
var redirect_uri = $('#google-sign-in-btn').data('redirect');
var state = $('#google-sign-in-btn').data('state');

// Initialize google API
function start() {
  gapi.load('auth2', function() {
    auth2 = gapi.auth2.init({
      client_id: google_client_id
    });
  });
}

$('#google-sign-in-btn').click(function() {
  auth2.grantOfflineAccess().then(googleSignInCallback);
});

function googleSignInCallback(authResult) {
  console.log(authResult);
  if (authResult.code) {

    // Hide the sign-in button now that the user is authorized, for example:
    $('#google-sign-in-btn').attr('disabled', true);

    // Send the code to the server
    $.ajax({
      type: 'POST',
      url: '/gconnect?state=' + state,
      processData: false,
      data: authResult.code,
      contentType: 'application/octet-stream; charset=utf-8',
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      },
      success: function(result) {
        // Handle the server response.
        if (result) {
          $('#result').html('Login Successful!</br>' + result + '</br>Redirecting...');
          setTimeout(function() {
            window.location.href = redirect_uri;
          }, 4000);

        } else if (authResult.error) {
          console.log('There was an error: ' + authResulterror);
        } else {
          $('#result').html('Failed to make a server-side call. Check your configuration and console.');
        }
      }
    });
  }
}
