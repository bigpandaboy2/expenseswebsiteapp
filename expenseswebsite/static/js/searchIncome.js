document.addEventListener("DOMContentLoaded", () => {
    const searchField = document.querySelector("#searchField");
    const tableOutput = document.querySelector(".table-output");
    const appTable = document.querySelector(".app-table");
    const paginationContainer = document.querySelector(".pagination-container");
    const noResults = document.querySelector(".no-results");
    const tbody = document.querySelector(".table-body");
  
    if (!searchField) return;
  
    tableOutput.style.display = "none";
  
    searchField.addEventListener("keyup", (e) => {
      const searchValue = e.target.value.trim();
  
      if (searchValue.length > 0) {
        if (paginationContainer) paginationContainer.style.display = "none";
        tbody.innerHTML = "";
        fetch("/income/search-income", {
          body: JSON.stringify({ searchText: searchValue }),
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        })
          .then((res) => res.json())
          .then((data) => {
            appTable.style.display = "none";
            tableOutput.style.display = "block";
  
            if (data.length === 0) {
              if (noResults) noResults.style.display = "block";
              tableOutput.style.display = "none";
            } else {
              if (noResults) noResults.style.display = "none";
              data.forEach((item) => {
                tbody.innerHTML += `
                  <tr>
                    <td>${item.amount}</td>
                    <td>${item.source}</td>
                    <td>${item.description}</td>
                    <td>${item.date}</td>
                    <td>
                      <a href="/income/edit-income/${item.id}" class="btn btn-sm btn-secondary">Edit</a>
                    </td>
                  </tr>
                `;
              });
            }
          });
      } else {
        tableOutput.style.display = "none";
        appTable.style.display = "block";
        if (paginationContainer) paginationContainer.style.display = "block";
      }
    });
  });  