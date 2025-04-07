const renderChart = (data, labels) => {
    const ctx = document.getElementById("incomeChart").getContext("2d");
  
    new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Income in last 6 months",
            data: data,
            backgroundColor: [
              "rgba(255, 99, 132, 0.2)",
              "rgba(54, 162, 235, 0.2)",
              "rgba(255, 206, 86, 0.2)",
              "rgba(75, 192, 192, 0.2)",
              "rgba(153, 102, 255, 0.2)",
              "rgba(255, 159, 64, 0.2)",
            ],
            borderColor: [
              "rgba(255, 99, 132, 1)",
              "rgba(54, 162, 235, 1)",
              "rgba(255, 206, 86, 1)",
              "rgba(75, 192, 192, 1)",
              "rgba(153, 102, 255, 1)",
              "rgba(255, 159, 64, 1)",
            ],
            borderWidth: 1,
          },
        ],
      },
      options: {
        plugins: {
          title: {
            display: true,
            text: "Income per Source (Last 6 Months)",
          },
        },
      },
    });
  };
  
  const getChartData = () => {
    console.log("fetching");
    fetch(incomeSummaryURL)
      .then((res) => res.json())
      .then((results) => {
        console.log("results", results);
        const source_data = results.income_source_summary;
        const labels = Object.keys(source_data);
        const data = Object.values(source_data);
        renderChart(data, labels);
      })
      .catch((error) => console.error("Error fetching data:", error));
  };
  
  window.addEventListener("DOMContentLoaded", getChartData);  