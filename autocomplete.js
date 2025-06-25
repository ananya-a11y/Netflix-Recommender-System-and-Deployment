$(function() {
  let films = [];

  $.ajax({
    type: 'GET',
    url: '/api/movies',
    dataType: 'json',
    success: function(response) {
      films = response.movies;

      new autoComplete({
        data: {
          src: films,
        },
        selector: "#autoComplete",
        threshold: 2,
        debounce: 100,
        searchEngine: "strict",
        resultsList: {
          render: true,
          container: (source) => {
            source.setAttribute("id", "movie_list");
          },
          destination: document.querySelector("#autoComplete"),
          position: "afterend",
          element: "ul"
        },
        maxResults: 5,
        highlight: true,
        resultItem: {
          content: (data, source) => {
            source.innerHTML = data.match;
          },
          element: "li"
        },
        noResults: () => {
          const result = document.createElement("li");
          result.setAttribute("class", "no_result");
          result.setAttribute("tabindex", "1");
          result.innerHTML = "No Results";
          document.querySelector("#movie_list").appendChild(result);
        },
        onSelection: feedback => {
          document.getElementById('autoComplete').value = feedback.selection.value;
          $('.movie-button').prop('disabled', false); // Enable button after selection
        }
      });
    },
    error: function() {
      console.error("Error loading movie list.");
    }
  });

  $('#autoComplete').on('input', function() {
    if (this.value.trim() === '') {
      $('.movie-button').attr('disabled', true);
    } else {
      $('.movie-button').attr('disabled', false);
    }
  });
});
