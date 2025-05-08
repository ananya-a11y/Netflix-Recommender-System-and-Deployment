$(function() {
  // Button will be disabled until we type anything inside the input field
  const source = document.getElementById('autoComplete');
  const inputHandler = function(e) {
    if (e.target.value == "") {
      $('.movie-button').attr('disabled', true);
    } else {
      $('.movie-button').attr('disabled', false);
    }
  }
  source.addEventListener('input', inputHandler);

  $('.movie-button').on('click', function() {
    var my_api_key = 'YOUR_TMDB_API_KEY'; // Replace with your actual API key
    var title = $('#autoComplete').val(); // Corrected selector
    if (title == "") {
      $('.results').css('display', 'none');
      $('.fail').css('display', 'block');
    } else {
      load_details(my_api_key, title);
    }
  });
});

// will be invoked when clicking on the recommended movies
function recommendcard(e) {
  var my_api_key = 'YOUR_TMDB_API_KEY'; // Replace with your actual API key
  var title = e.getAttribute('title');
  load_details(my_api_key, title);
}

// get the basic details of the movie from the API (based on the name of the movie)
function load_details(my_api_key, title) {
  $("#loader").fadeIn();
  $('.fail').css('display', 'none');
  $('.results').css('display', 'none');
  $.ajax({
    type: 'GET',
    url: 'https://api.themoviedb.org/3/search/movie?api_key=' + my_api_key + '&query=' + encodeURIComponent(title),
    dataType: 'json',
    success: function(movie) {
      console.log("Movie API Response:", movie);
      if (movie.results && movie.results.length > 0) { // added check for movie.results
        var movie_id = movie.results[0].id;
        var movie_title = movie.results[0].original_title;
        movie_recs(movie_title, movie_id, my_api_key);
      } else {
        $('.fail').css('display', 'block');
        $('.results').css('display', 'none');
        $("#loader").fadeOut();
      }
    },
    error: function(xhr, status, error) {
      console.error("Movie API Error:", status, error, xhr.responseText);
      $("#loader").fadeOut();
      $('#error-message').text("Error: " + status + ". Please check your network connection and try again.").show(); // added error message
    },
  });
}

// passing the movie name to get the similar movies from python's flask
function movie_recs(movie_title, movie_id, my_api_key) {
  $.ajax({
    type: 'POST',
    url: "/similarity",
    data: {
      'name': movie_title
    },
    dataType: 'json',
    success: function(recs) {
      console.log("Similarity API Response:", recs);
      if (recs.error) {
        $('.fail').css('display', 'block');
        $('.results').css('display', 'none');
        $("#loader").fadeOut();
      } else {
        $('.fail').css('display', 'none');
        $('.results').css('display', 'block');

        var movie_arr = recs.recommendations;
        var arr = [];
        for (const movie of movie_arr) {
          arr.push(movie);
        }

        get_movie_details(movie_id, my_api_key, arr, movie_title);
      }
    },
    error: function(xhr, status, error) {
      console.error("Similarity API Error:", status, error, xhr.responseText);
      $("#loader").fadeOut();
      $('#error-message').text("Error: " + status + ". Please check the server and try again.").show(); // added error message
    },
  });
}
// get all the details of the movie using the movie id.
function get_movie_details(movie_id, my_api_key, arr, movie_title) {
  $.ajax({
    type: 'GET',
    url: 'https://api.themoviedb.org/3/movie/' + movie_id + '?api_key=' + my_api_key,
    dataType: 'json',
    success: function(movie_details) {
      console.log("Movie Details API Response:", movie_details);
      show_details(movie_details, arr, movie_title, my_api_key, movie_id);
    },
    error: function(xhr, status, error) {
      console.error("Movie Details API Error:", status, error, xhr.responseText);
      $("#loader").fadeOut();
      $('#error-message').text("Error: " + status + ". Please check the API key and movie ID.").show(); // added error message
    },
  });
}

// passing all the details to python's flask for displaying and scraping the movie reviews using imdb id
function show_details(movie_details, arr, movie_title, my_api_key, movie_id) {
  var imdb_id = movie_details.imdb_id;
  var poster = 'https://image.tmdb.org/t/p/original' + movie_details.poster_path;
  var overview = movie_details.overview;
  var genres = movie_details.genres;
  var rating = movie_details.vote_average;
  var vote_count = movie_details.vote_count;
  var release_date = new Date(movie_details.release_date);
  var runtime = parseInt(movie_details.runtime);
  var status = movie_details.status;
  var genre_list = []
  for (var genre in genres) {
    genre_list.push(genres[genre].name);
  }
  var my_genre = genre_list.join(", ");
  if (runtime % 60 == 0) {
    runtime = Math.floor(runtime / 60) + " hour(s)"
  } else {
    runtime = Math.floor(runtime / 60) + " hour(s) " + (runtime % 60) + " min(s)"
  }
  arr_poster = get_movie_posters(arr, my_api_key);

  movie_cast = get_movie_cast(movie_id, my_api_key);

  ind_cast = get_individual_cast(movie_cast, my_api_key);

  details = {
    'title': movie_title,
    'cast_ids': JSON.stringify(movie_cast.cast_ids),
    'cast_names': JSON.stringify(movie_cast.cast_names),
    'cast_chars': JSON.stringify(movie_cast.cast_chars),
    'cast_profiles': JSON.stringify(movie_cast.cast_profiles),
    'cast_bdays': JSON.stringify(ind_cast.cast_bdays),
    'cast_bios': JSON.stringify(ind_cast.cast_bios),
    'cast_places': JSON.stringify(ind_cast.cast_places),
    'imdb_id': imdb_id,
    'poster': poster,
    'genres': my_genre,
    'overview': overview,
    'rating': rating,
    'vote_count': vote_count.toLocaleString(),
    'release_date': release_date.toDateString().split(' ').slice(1).join(' '),
    'runtime': runtime,
    'status': status,
    'rec_movies': JSON.stringify(arr),
    'rec_posters': JSON.stringify(arr_poster),
  }

  $.ajax({
    type: 'POST',
    data: details,
    url: "/recommend", // changed url
    dataType: 'html',
    complete: function() {
      $("#loader").delay(500).fadeOut();
    },
    success: function(response) {
      $('.results').html(response);
      $('#autoComplete').val('');
      $(window).scrollTop(0);
    },
    error: function(xhr, status, error) {
      console.error("Recommendation Display Error:", status, error, xhr.responseText);
      $('#error-message').text("Error: " + status + ".  Failed to display recommendations.").show(); // added error message
    },
  });
}

// get the details of individual cast
function get_individual_cast(movie_cast, my_api_key) {
  const cast_ids = movie_cast.cast_ids;
  const cast_details_promises = cast_ids.map(cast_id => {
    return $.ajax({
      type: 'GET',
      url: `https://api.themoviedb.org/3/person/${cast_id}?api_key=${my_api_key}`,
      dataType: 'json'
    });
  });

  return Promise.all(cast_details_promises)
    .then(cast_details_array => {
      const cast_bdays = cast_details_array.map(cast_detail => {
        const birthday = cast_detail.birthday ? new Date(cast_detail.birthday).toDateString().split(' ').slice(1).join(' ') : "N/A"; // added null check
        return birthday;
      });
      const cast_bios = cast_details_array.map(cast_detail => cast_detail.biography || "N/A"); // added null check
      const cast_places = cast_details_array.map(cast_detail => cast_detail.place_of_birth || "N/A"); // added null check
      return {
        cast_bdays,
        cast_bios,
        cast_places
      };
    })
    .catch(error => {
      console.error("Error fetching cast details:", error);
      $('#error-message').text("Error fetching cast details.  Please check API.").show(); // added error message
      return {
        cast_bdays: [],
        cast_bios: [],
        cast_places: []
      }; // Return empty arrays to prevent further errors
    });
}

// getting the details of the cast for the requested movie
function get_movie_cast(movie_id, my_api_key) {
  let cast_ids = [];
  let cast_names = [];
  let cast_chars = [];
  let cast_profiles = [];

  $.ajax({
    type: 'GET',
    url: "https://api.themoviedb.org/3/movie/" + movie_id + "/credits?api_key=" + my_api_key,
    async: false,
    dataType: 'json',
    success: function(my_movie) {
      console.log("Movie Cast API Response:", my_movie);
      if (my_movie.cast && my_movie.cast.length > 0) { // added check for my_movie.cast
        const topCastCount = Math.min(my_movie.cast.length, 10);
        for (let i = 0; i < topCastCount; i++) {
          const castMember = my_movie.cast[i];
          cast_ids.push(castMember.id);
          cast_names.push(castMember.name);
          cast_chars.push(castMember.character);
          cast_profiles.push(castMember.profile_path ?
            "https://image.tmdb.org/t/p/original" + castMember.profile_path :
            "/path/to/placeholder.jpg" // added placeholder
          );
        }
      }
    },
    error: function(xhr, status, error) {
      console.error("Error fetching movie cast:", error);
      $('#error-message').text("Error fetching movie cast. Please check the API.").show(); // added error message
    },
  });

  return {
    cast_ids: cast_ids,
    cast_names: cast_names,
    cast_chars: cast_chars,
    cast_profiles: cast_profiles
  };
}

// getting posters for all the recommended movies
function get_movie_posters(arr, my_api_key) {
  var arr_poster_list = []
  for (var m in arr) {
    $.ajax({
      type: 'GET',
      url: 'https://api.themoviedb.org/3/search/movie?api_key=' + my_api_key + '&query=' + arr[m],
      async: false,
      dataType: 'json',
      success: function(m_data) {
        if (m_data.results && m_data.results.length > 0 && m_data.results[0].poster_path) {  // added checks
          arr_poster_list.push('https://image.tmdb.org/t/p/original' + m_data.results[0].poster_path);
        }
        else{
          arr_poster_list.push('/path/to/placeholder.jpg'); // Added a placeholder image path
        }
      },
      error: function(xhr, status, error) {
        console.error("Error fetching movie posters:", error);
        $('#error-message').text("Error fetching movie posters.  Please check the API.").show(); // added error message
        arr_poster_list.push('/path/to/placeholder.jpg');  //push placeholder in case of error
      },
    })
  }
  return arr_poster_list;
}

