document.addEventListener("DOMContentLoaded", () => {
    const searchField = document.querySelector("#searchField");
    const tableOutput = document.querySelector(".table-output");
    const appTable = document.querySelector(".app-table");
    const noResults = document.querySelector(".no-results");
  
    if (!searchField || !tableOutput || !appTable || !noResults) return;
  
    searchField.addEventListener("keyup", (e) => {
      const searchValue = e.target.value.trim();
  
      if (searchValue.length > 0) {
        fetch("/search-expenses", {
          body: JSON.stringify({ searchText: searchValue }),
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
          },
        })
          .then((res) => res.json())
          .then((data) => {
            appTable.style.display = "none";
            tableOutput.style.display = "block";
  
            if (data.length === 0) {
              noResults.style.display = "block";
              tableOutput.innerHTML = "";
            } else {
              noResults.style.display = "none";
              let tableData = "";
              data.forEach((item) => {
                tableData += `
                  <tr>
                    <td>${item.amount}</td>
                    <td>${item.category}</td>
                    <td>${item.description}</td>
                    <td>${item.date}</td>
                    <td>
                      <a href="/edit-expense/${item.id}" class="btn btn-secondary btn-sm">Edit</a>
                    </td>
                  </tr>
                `;
              });
  
              tableOutput.innerHTML = `
                <table class="table table-striped table-hover">
                  <thead>
                    <tr>
                      <th>Amount</th>
                      <th>Category</th>
                      <th>Description</th>
                      <th>Date</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    ${tableData}
                  </tbody>
                </table>
              `;
            }
          });
      } else {
        noResults.style.display = "none";
        tableOutput.style.display = "none";
        appTable.style.display = "block";
      }
    });
  
    function getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === name + "=") {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }
  });  