<input type="text" id="autoComplete" class="movie" placeholder="Enter movie name..." />
<script>
  $(function() {
    let films = []; // Declare the films array

    $.ajax({
      type: 'GET',
      url: '/api/movies',
      dataType: 'json',
      success: function(response) {
        films = response.movies; // Populate the films array with data from Flask

        // Initialize autoComplete *inside* the success callback
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
          }
        });
      },
      error: function(xhr, status, error) {
        console.error("Error fetching movies:", error);
        // Display an error message to the user in the UI
        $('#error-message').text("Failed to load movie titles. Please check your server connection.").show();
      }
    });
  });
</script>
