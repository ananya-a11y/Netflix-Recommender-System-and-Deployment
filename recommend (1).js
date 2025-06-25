$(function() {
  $('.movie-button').on('click', function() {
    var my_api_key = '7fee067b60fd14ed0bd0013b0863045f';
    var title = $('.movie').val();
    if (title.trim() === "") {
      $('.results').hide();
      $('.fail').show();
    } else {
      load_details(my_api_key, title);
    }
  });
});

function recommendcard(e) {
  var my_api_key = '7fee067b60fd14ed0bd0013b0863045f';
  var title = e.getAttribute('title'); 
  load_details(my_api_key, title);
}

function load_details(my_api_key, title) {
  $.ajax({
    type: 'GET',
    url: 'https://api.themoviedb.org/3/search/movie?api_key=' + my_api_key + '&query=' + title,
    success: function(movie) {
      if (movie.results.length < 1) {
        $('.fail').show();
        $('.results').hide();
        $("#loader").fadeOut(500);
      } else {
        $("#loader").fadeIn();
        $('.fail').hide();
        $('.results').delay(1000).show();
        var movie_id = movie.results[0].id;
        var movie_title = movie.results[0].original_title;
        movie_recs(movie_title, movie_id, my_api_key);
      }
    },
    error: function() {
      alert('Invalid Request');
      $("#loader").fadeOut(500);
    }
  });
}

function movie_recs(movie_title, movie_id, my_api_key) {
  $.ajax({
    type: 'POST',
    url: "/similarity",
    data: { 'name': movie_title },
    success: function(recs) {
      if (recs.error) {
        $('.fail').show();
        $('.results').hide();
        $("#loader").fadeOut(500);
      } else {
        $('.fail').hide();
        $('.results').show();
        get_movie_details(movie_id, my_api_key, recs.recommendations, movie_title);
      }
    },
    error: function() {
      alert("Error in fetching recommendations.");
      $("#loader").fadeOut(500);
    }
  }); 
}

function get_movie_details(movie_id, my_api_key, arr, movie_title) {
  $.ajax({
    type: 'GET',
    url: 'https://api.themoviedb.org/3/movie/' + movie_id + '?api_key=' + my_api_key,
    success: function(movie_details) {
      show_details(movie_details, arr, movie_title, my_api_key, movie_id);
    },
    error: function() {
      alert("API Error!");
      $("#loader").fadeOut(500);
    }
  });
}

// (other functions like show_details, get_movie_cast, get_movie_posters, etc.) remain the same.

