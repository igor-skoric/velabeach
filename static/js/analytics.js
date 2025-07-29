const { reactive, ref, onMounted } = Vue;

const analytics = createApp({
  setup() {

    const dailyChartInstance = ref(null);
    const monthlyChartInstance = ref(null);

    const revenue = reactive({
      date: "",
      A: "0",
      B: "0",
      C: "0",
      D: "0",
      total_income: "0"
    });


   const currentDate = ref(new Date());
   const todayStr = currentDate.value.toISOString().split('T')[0];

   const start = ref(new Date());
   start.value.setDate(currentDate.value.getDate() - 7);
   const sevenDaysAgoStr = start.value.toISOString().split('T')[0];

   const startDate = ref(sevenDaysAgoStr);
   const endDate = ref(todayStr);

    const fetchData = async (url, params = {}) => {
      try {
        const response = await axios.get(url, { params });
        return response.data;
      } catch (error) {
        console.error(`Greška pri dohvatanju sa ${url}:`, error);
        throw error;
      }
    };
    const fetchRevenue = async () => {
      const date = startDate.value;
      const end_date = endDate.value;

      try {
        const response = await fetchData('/api/daily-revenue-by-date/', {
          date,
          end_date
        });

        return response; // ovde sada VRAĆAŠ response
      } catch (e) {
        console.error('Greška u fetchRevenue:', e);
        return []; // fallback
      }
    };

    function groupDataByMonth(data) {
      const monthlyData = {};

      data.forEach(item => {
        const [year, month] = item.date.split('-');
        const ym = `${year}-${month}`; // npr. "2025-07"
        if (!monthlyData[ym]) {
          monthlyData[ym] = 0;
        }
        monthlyData[ym] += parseFloat(item.total_income);
      });

      // Izvuci labele i vrednosti sortirane po datumu
      const labels2 = Object.keys(monthlyData).sort();
      const totals2 = labels2.map(label => monthlyData[label]);

      return { labels2, totals2 };
    }

    const createDailyChart = async () => {
      if (dailyChartInstance.value) {
        dailyChartInstance.value.destroy();
      }
      if(monthlyChartInstance.value){
        monthlyChartInstance.value.destroy();
      }
      const response = await fetchRevenue(); // sada čekaš i koristiš response

      if (!Array.isArray(response)) return;

      // Puni Chart.js
      const labels = response.map(r => r.date);
      const datasetA = response.map(r => parseFloat(r.A));
      const datasetB = response.map(r => parseFloat(r.B));
      const datasetC = response.map(r => parseFloat(r.C));
      const datasetD = response.map(r => parseFloat(r.D));
      const totalIncome = response.map(r => parseFloat(r.total_income));

      const ctx = document.getElementById('revenueChart').getContext('2d');

      dailyChartInstance.value = new Chart(ctx, {
        type: 'bar',
        data: {
          labels,
          datasets: [
            {
              label: 'A',
              data: datasetA,
              backgroundColor: '#3b82f6'
            },
            {
              label: 'B',
              data: datasetB,
              backgroundColor: '#10b981'
            },
            {
              label: 'C',
              data: datasetC,
              backgroundColor: '#f59e0b'
            },
            {
              label: 'D',
              data: datasetD,
              backgroundColor: '#ef4444'
            },
            {
              label: 'Total Income',
              data: totalIncome,
              type: 'line',
              borderColor: '#000',
              backgroundColor: '#000',
              tension: 0.3,
              yAxisID: 'y'
            }
          ]
        },
        options: {
          responsive: true,
           maintainAspectRatio: false,
          interaction: {
            mode: 'index',
            intersect: false
          },
          stacked: true,
          plugins: {
            title: {
              display: true,
              text: 'Dnevni izveštaj',
              font: {
                size: 18
              }
            },
            legend: {
              position: 'top'
            }
          },
          scales: {
            x: {
              stacked: true
            },
            y: {
              stacked: true,
              beginAtZero: true
            }
          }
        }
      });


          // NEW CHART SORTED MOUNTS
      const { labels2, totals2 } = groupDataByMonth(response);
      const ctxMonthly = document.getElementById('monthlyChart').getContext('2d');

      monthlyChartInstance.value = new Chart(ctxMonthly, {
        type: 'bar',
        data: {
          labels: labels2,          // "2025-07", "2025-08", ...
          datasets: [{
            label: 'Ukupna zarada po mesecu',
            data: totals2,
            backgroundColor: '#3b82f6',
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            title: {
              display: true,
              text: 'Mesečni pregled ',
              font: { size: 18 }
            },
            legend: { display: false }
          },
          scales: {
            y: { beginAtZero: true }
          }
        }
      });
    }

    onMounted(async () => {
        await createDailyChart();

    });

    return { revenue, currentDate, startDate, endDate, createDailyChart  };
  }
});

analytics.config.compilerOptions.delimiters = ['[[', ']]'];
analytics.mount('#analytics');
