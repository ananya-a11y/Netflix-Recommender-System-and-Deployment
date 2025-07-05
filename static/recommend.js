$(function () {
  $('.movie-button').on('click', function () {
    const my_api_key = '7fee067b60fd14ed0bd0013b0863045f';
    const title = $('.movie').val().trim();
    if (title === "") {
      $('.results').hide();
      $('.fail').show();
    } else {
      load_details(my_api_key, title);
    }
  });
});

function recommendcard(e) {
  const title = e.getAttribute('title');
  const my_api_key = '7fee067b60fd14ed0bd0013b0863045f';
  load_details(my_api_key, title);
}

function load_details(my_api_key, title) {
  $.ajax({
    type: 'GET',
    url: 'https://api.themoviedb.org/3/search/movie?api_key=' + my_api_key + '&query=' + title,
    success: function (movie) {
      if (movie.results.length < 1) {
        $('.fail').show();
        $('.results').hide();
        $("#loader").fadeOut(500);
      } else {
        $("#loader").fadeIn();
        $('.fail').hide();
        $('.results').hide();
        const movie_id = movie.results[0].id;
        const movie_title = movie.results[0].original_title;
        movie_recs(movie_title, movie_id, my_api_key);
      }
    },
    error: function () {
      alert('Invalid Request');
      $("#loader").fadeOut(500);
    }
  });
}

function movie_recs(movie_title, movie_id, my_api_key) {
  $.ajax({
    type: 'POST',
    url: "/similarity",
    data: { name: movie_title },
    success: function (recs) {
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
    error: function () {
      alert("Error fetching recommendations.");
      $("#loader").fadeOut(500);
    }
  });
}

function get_movie_details(movie_id, my_api_key, rec_titles, movie_title) {
  $.ajax({
    type: 'GET',
    url: 'https://api.themoviedb.org/3/movie/' + movie_id + '?api_key=' + my_api_key,
    success: function (movie_details) {
      show_details(movie_details, rec_titles, movie_title, my_api_key, movie_id);
    },
    error: function () {
      alert("Movie details API error");
      $("#loader").fadeOut(500);
    }
  });
}

function get_movie_posters(titles, my_api_key) {
  const posters = [];
  titles.forEach(title => {
    $.ajax({
      type: 'GET',
      url: 'https://api.themoviedb.org/3/search/movie?api_key=' + my_api_key + '&query=' + title,
      async: false,
      success: function (m) {
        posters.push('https://image.tmdb.org/t/p/original' + m.results[0]?.poster_path);
      }
    });
  });
  return posters;
}

function get_movie_cast(movie_id, my_api_key) {
  let cast_ids = [], cast_names = [], cast_chars = [], cast_profiles = [];
  $.ajax({
    type: 'GET',
    url: 'https://api.themoviedb.org/3/movie/' + movie_id + '/credits?api_key=' + my_api_key,
    async: false,
    success: function (credits) {
      const top_cast = credits.cast.slice(0, 10);
      top_cast.forEach(cast => {
        cast_ids.push(cast.id);
        cast_names.push(cast.name);
        cast_chars.push(cast.character);
        cast_profiles.push("https://image.tmdb.org/t/p/original" + cast.profile_path);
      });
    }
  });
  return { cast_ids, cast_names, cast_chars, cast_profiles };
}

function get_individual_cast(cast_ids, my_api_key) {
  let cast_bdays = [], cast_bios = [], cast_places = [];
  cast_ids.forEach(id => {
    $.ajax({
      type: 'GET',
      url: 'https://api.themoviedb.org/3/person/' + id + '?api_key=' + my_api_key,
      async: false,
      success: function (person) {
        cast_bdays.push(new Date(person.birthday).toDateString());
        cast_bios.push(person.biography);
        cast_places.push(person.place_of_birth);
      }
    });
  });
  return { cast_bdays, cast_bios, cast_places };
}

function show_details(movie_details, rec_titles, movie_title, my_api_key, movie_id) {
  const imdb_id = movie_details.imdb_id;
  const poster = 'https://image.tmdb.org/t/p/original' + movie_details.poster_path;
  const overview = movie_details.overview;
  const rating = movie_details.vote_average;
  const vote_count = movie_details.vote_count.toLocaleString();
  const release_date = new Date(movie_details.release_date).toDateString();
  const runtime = `${Math.floor(movie_details.runtime / 60)} hr ${movie_details.runtime % 60} min`;
  const status = movie_details.status;
  const genres = movie_details.genres.map(g => g.name).join(', ');

  const rec_posters = get_movie_posters(rec_titles, my_api_key);
  const cast = get_movie_cast(movie_id, my_api_key);
  const cast_details = get_individual_cast(cast.cast_ids, my_api_key);

  const payload = {
    title: movie_title,
    cast_ids: JSON.stringify(cast.cast_ids),
    cast_names: JSON.stringify(cast.cast_names),
    cast_chars: JSON.stringify(cast.cast_chars),
    cast_profiles: JSON.stringify(cast.cast_profiles),
    cast_bdays: JSON.stringify(cast_details.cast_bdays),
    cast_bios: JSON.stringify(cast_details.cast_bios),
    cast_places: JSON.stringify(cast_details.cast_places),
    imdb_id,
    poster,
    genres,
    overview,
    rating,
    vote_count,
    release_date,
    runtime,
    status,
    rec_movies: JSON.stringify(rec_titles),
    rec_posters: JSON.stringify(rec_posters),
  };

  $.ajax({
    type: 'POST',
    url: '/recommend',
    data: payload,
    success: function (html) {
      $('.results').html(html);
      $('#autoComplete').val('');
      $(window).scrollTop(0);
    },
    complete: function () {
      $("#loader").fadeOut(500);
    }
  });
}


