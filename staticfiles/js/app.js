const { createApp, ref, onMounted, onBeforeUnmount, reactive  } = Vue;


    // Funkcija za čitanje CSRF tokena iz kolačića
    function getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
          cookie = cookie.trim();
          if (cookie.startsWith(name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }
    // Postavi CSRF token u Axios default zaglavlje
    const csrfToken = getCookie('csrftoken');
    if (csrfToken) {
      axios.defaults.headers.common['X-CSRFToken'] = csrfToken;
    }


    const app = createApp({
      data() {
        return {
            user: window.user || null,
            prices: {
              I: 25,
              II: 25,
              III: 20,
              IV: 20,
              V: 15,
              VI: 15,
              VII: 15,
              VIII: 15,
              IX: 15,
              X: 15,
              XI: 15,
              baldahin: 20,
            },
            todayDate: new Date(),
            currentDate: new Date(),
            stages: [
              {
                name: 'Reon A',
                symbol: 'A',
                chair: {
                  startingPosition: 1,
                  total: 55,
                  cols: 8,
                  obstacles: [54],
                },
                bed: {
                  startingPosition: 1,
                  total: 39,
                  cols: 9,
                  obstacles: [37, 38, 39, 40, 41],
                }
              },
              {
                name: 'Reon B',
                symbol: 'B',
                chair: {
                  startingPosition: 1,
                  total: 70,
                  cols: 10,
                  obstacles: [],
                },
                bed: {
                  startingPosition: 40,
                  total: 61,
                  cols: 11,
                  obstacles: [9,10],
                }
              },
              {
                name: 'Reon C',
                symbol: 'C',
                chair: {
                  startingPosition: 1,
                  total: 55,
                  cols: 8,
                  obstacles: [55],
                },
                chair2: {
                  startingPosition: 63,
                  total: 32,
                  cols: 9,
                  obstacles: [8,17,26],
                },
              },
              {
                name: 'Reon D',
                symbol: 'D',
                chair: {
                  startingPosition: 1,
                  total: 66,
                  cols: 10,
                  obstacles: [9,19,68,69],
                },
                chair2: {
                  startingPosition: 63,
                  total: 23,
                  cols: 9,
                  obstacles: [7,8,17],
                }
              },
            ],
            selectedStage: null,
            selectedCell: null,
            reservations: [],
            modalOpen: false,
            reservationForm: {
              status: '',
              price: 0,
              dateFrom: '',
              dateTo: '',
              description:''
            },
            logs: [
              'Aplikacija pokrenuta.',
              'Prva rezervacija učitana.'
            ],

            // Default Dialog
            dialogVisible: false,
            dialogType: null,
            dialogTitle: '',
            dialogMessage: '',
            dialogResolve: null,

            //Analitika
            revenue : {
                date: "",
                A: "0",
                B: "0",
                C: "0",
                D: "0",
                total_income: "0"
            },
            showRevenue: false,
            revenueStartDate: this.formatDateDDMMYYYY(new Date()),
            revenueEndDate: this.formatDateDDMMYYYY(new Date()),

            //Notifications
            notification: {
              show: false,
              message: '',
              type: 'success'  // or 'error'
            },

            // Layout iz baze (jedan izvor istine) — za sada reon A
            stageLayouts: {},
        };
      },
      mounted() {
        this.selectedStage = this.stages.find(stage => stage.symbol == user.stage)
        this.datePickerInitialization();
        if (this.selectedStage?.symbol) {
          this.fetchStageLayout(this.selectedStage.symbol);
        }
      },
      methods: {
              toRoman(num) {
                    const romans = [
                        ["M", 1000],
                        ["CM", 900],
                        ["D", 500],
                        ["CD", 400],
                        ["C", 100],
                        ["XC", 90],
                        ["L", 50],
                        ["XL", 40],
                        ["X", 10],
                        ["IX", 9],
                        ["V", 5],
                        ["IV", 4],
                        ["I", 1]
                    ];

                    let result = "";
                    for (let [roman, value] of romans) {
                        while (num >= value) {
                            result += roman;
                            num -= value;
                        }
                    }
                    return result;
                },
              datePickerInitialization(){
                    const startInput = document.getElementById('startDate');
                    const endInput = document.getElementById('endDate');

                    // Inicijalizuj oba datepickera
                    new Datepicker(startInput, {
                      format: 'dd/mm/yyyy',
                      autohide: true,
                      range: true
                    });

                    new Datepicker(endInput, {
                      format: 'dd/mm/yyyy',
                      autohide: true
                    });

                    // Event listeneri za promenu datuma
                    startInput.addEventListener('changeDate', (e) => {
                      this.revenueStartDate = e.target.value;
                      this.fetchRevenue()
                    });

                    endInput.addEventListener('changeDate', (e) => {
                      this.revenueEndDate = e.target.value;
                      this.fetchRevenue()
                    });
              },
              async fetchStageLayout(symbol) {
                try {
                  const data = await this.fetchData(`/api/stages/${symbol}/layout/`);
                  this.stageLayouts = { ...this.stageLayouts, [symbol]: data };
                  const stage = this.stages.find(s => s.symbol === symbol);
                  if (!stage || !data.sections) {
                    return;
                  }
                  if (data.sections.chair && stage.chair) {
                    stage.chair.cols = data.sections.chair.cols;
                  }
                  if (data.sections.chair2 && stage.chair2) {
                    stage.chair2.cols = data.sections.chair2.cols;
                  }
                  if (data.sections.bed && stage.bed) {
                    stage.bed.cols = data.sections.bed.cols;
                  }
                } catch (error) {
                  console.warn(`Layout reona ${symbol} nije učitan iz baze.`, error);
                }
              },
              currentStageLayout() {
                const symbol = this.selectedStage?.symbol;
                return symbol ? this.stageLayouts[symbol] : null;
              },
              sectionCols(sectionKey, fallbackCols) {
                const section = this.currentStageLayout()?.sections?.[sectionKey];
                return section?.cols || fallbackCols;
              },
              usesPlacedCells(sectionKey) {
                const section = this.currentStageLayout()?.sections?.[sectionKey];
                return (
                  this.currentStageLayout()?.from_database &&
                  section?.cells?.length > 0 &&
                  section.cells[0].grid_row != null
                );
              },
              sectionContainerStyle() {
                return {};
              },
              sectionContainerClass(sectionKey, fallbackCols, position = 'first') {
                const cols = this.sectionCols(sectionKey, fallbackCols);
                const topMargin = position === 'afterPath' ? 'mt-2' : 'mt-5';
                return `${topMargin} grid gap-1 grid-cols-${cols}`;
              },
              cellGridStyle(cell) {
                if (cell.grid_row != null && cell.grid_col != null) {
                  return {
                    gridRow: cell.grid_row,
                    gridColumn: cell.grid_col,
                  };
                }
                return {};
              },
              cellKey(cell, index) {
                if (cell.lounger_id) {
                  return `l-${cell.lounger_id}`;
                }
                if (cell.grid_row != null && cell.grid_col != null) {
                  return `r${cell.grid_row}c${cell.grid_col}`;
                }
                return `i-${index}`;
              },
              mergeCellsWithReservations(cells, stageSymbol) {
                const formattedDate = this.currentDate.toLocaleDateString('en-CA');
                return cells.map(cell => {
                  if (cell.isObstacle) {
                    return { ...cell };
                  }
                  const reservation = Array.isArray(this.reservations)
                    ? this.reservations.find(r =>
                        r.lounger_position === cell.label &&
                        r.stage === stageSymbol &&
                        r.date === formattedDate
                      )
                    : null;
                  return {
                    ...cell,
                    status: reservation ? reservation.status : 'available',
                    status_display: reservation ? reservation.status_display : 'Dostupno',
                    reservation: reservation,
                  };
                });
              },
              cellsFromLayout(stage, sectionKey) {
                const cells = this.stageLayouts[stage.symbol]?.sections?.[sectionKey]?.cells;
                if (!cells) {
                  return null;
                }
                return this.mergeCellsWithReservations(cells, stage.symbol);
              },
              ensureStageLayout(symbol) {
                if (!this.stageLayouts[symbol]) {
                  this.fetchStageLayout(symbol);
                }
              },
              generateChairCells(stage, type='first') {
                  const sectionKey = type === 'first' ? 'chair' : 'chair2';
                  const fromDb = this.cellsFromLayout(stage, sectionKey);
                  if (fromDb) {
                    return fromDb;
                  }

                  const result = [];
                  let totalCells, cols, currentIndex, obstacles;
                  if (type==='first'){
                    obstacles = stage.chair.obstacles;
                    currentIndex = 0;
                    totalCells = stage.chair.total + stage.chair.obstacles.length;
                    cols = stage.chair.cols;
                  }else{
                    obstacles = stage.chair2.obstacles;
                    currentIndex = stage.chair2.startingPosition;
                    totalCells = stage.chair2.total + stage.chair2.obstacles.length;
                    cols = stage.chair2.cols;
                  }

                  for (let i = 0; i < totalCells; i++) {
                    if (obstacles.includes(i)) {
                      result.push({ isObstacle: true, label: 'X', price: 0 });
                      currentIndex++;
                    } else {
                      const row = Math.floor(currentIndex / cols);
                      const col = currentIndex % cols + 1;
//                      const rowLetter = String.fromCharCode(65 + row);
                      const rowLetter = this.toRoman(row + 1);
                      const label = `${rowLetter}${col}`;
                      const price = this.prices[rowLetter];

                      // Pretvori datum u string radi poređenja
                      const formattedDate = this.currentDate.toLocaleDateString('en-CA');

                      // Provera da je reservations niz
                      const reservation = Array.isArray(this.reservations)
                        ? this.reservations.find(r =>
                            r.lounger_position === label &&
                            r.stage === stage.symbol &&
                            r.date === formattedDate
                          )
                        : null;

                      result.push({
                        isObstacle: false,
                        label,
                        price,
                        grid_row: row + 1,
                        grid_col: col,
                        status: reservation ? reservation.status : 'available',
                        status_display: reservation ? reservation.status_display : 'Dostupno',
                        reservation: reservation
                      });

                      currentIndex++;
                    }
                  }

                  return result;
              },
              generateBedCells(stage) {
                  const fromDb = this.cellsFromLayout(stage, 'bed');
                  if (fromDb) {
                    return fromDb;
                  }

                  const totalCells = stage.bed.total + stage.bed.obstacles.length;
                  const result = [];
                  const price = this.prices['baldahin'];
                  let currentNumber = stage.bed.startingPosition;

                  const formattedDate = this.currentDate.toLocaleDateString('en-CA');

                  for (let i = 0; i < totalCells; i++) {
                    if (stage.bed.obstacles.includes(i)) {
                      result.push({ isObstacle: true, label: 'X' });
                    } else {
                      const reservation = Array.isArray(this.reservations)
                        ? this.reservations.find(r =>
                            String(r.lounger_position) === String(currentNumber) &&
                            r.stage === stage.symbol &&
                            r.date === formattedDate
                          )
                        : null;

                      const bedRow = Math.floor((currentNumber - stage.bed.startingPosition) / stage.bed.cols) + 1;
                      const bedCol = ((currentNumber - stage.bed.startingPosition) % stage.bed.cols) + 1;
                      result.push({
                        isObstacle: false,
                        label: currentNumber,
                        price: price,
                        grid_row: bedRow,
                        grid_col: bedCol,
                        status: reservation ? reservation.status : 'available',
                        status_display: reservation ? reservation.status_display : 'Dostupno',
                        reservation: reservation
                      });

                      currentNumber++;
                    }
                  }

                  return result;
                },
              changeStage(stage){
                this.selectedStage = stage
                if (!this.stageLayouts[stage.symbol]) {
                  this.fetchStageLayout(stage.symbol);
                }
              },
              prevDay() {
                const date = new Date(this.currentDate);
                date.setDate(date.getDate() - 1);
                this.currentDate = date;
          },
              nextDay() {
                const date = new Date(this.currentDate);
                date.setDate(date.getDate() + 1);
                this.currentDate = date;
          },
              async fetchData(url, params = {}) {
                try {
                  const response = await axios.get(url, { params });
                  return response.data;
                } catch (error) {
                  console.error(`Greška pri dohvatanju sa ${url}:`, error);
                  throw error;
                }
              },
              async postData(url, payload = {}) {
                  try {
                    const response = await axios.post(url, payload);
                    return response.data;
                  } catch (error) {
                    console.error(`Greška pri slanju POST zahteva na ${url}:`, error);
                    throw error;
                  }
                },
              async deleteData(url, params = {}) {
                  try {
                    const response = await axios.delete(url, { params });
                    return response.data;
                  } catch (error) {
                    console.error(`Greška pri brisanju sa ${url}:`, error);
                    throw error;
                  }
                },
              async fetchRevenue(currentDate = null) {
              let date = null;
              let end_date = null;

                  // Ako je prosleđen, koristi ga
                if (currentDate !== null) {
//                    console.log("Parametar:", currentDate);
                    date  = this.convertDDMMYYYYtoYMD(this.formatDateDDMMYYYY(this.currentDate));
                    end_date  = this.convertDDMMYYYYtoYMD(this.formatDateDDMMYYYY(this.currentDate));
                } else {
//                    console.log("Parametar nije prosleđen");
                    date = this.convertDDMMYYYYtoYMD(this.revenueStartDate);
                    end_date = this.convertDDMMYYYYtoYMD(this.revenueEndDate);
                }
                try {

                    const response = await this.fetchData('api/daily-revenue-by-date/', { date, end_date });
                    this.revenue = response[0];
    //                     console.log(response)
                    return response;

                } catch (e) {
                      // Dodatna obrada greške ako je potrebna
                }
              },
              async fetchReservations() {
               let date = this.currentDate.toLocaleDateString('en-CA'); // format YYYY-MM-DD
                const stage = this.selectedStage.symbol;

                try {
                  const response = await this.fetchData('/api/reservations/', { date, stage });

                    this.reservations = response.map(reservation => {
                      const formattedDetails = reservation.details.map(detail => {
                        return {
                          ...detail,
                          reserved_at: new Date(detail.reserved_at).toLocaleString('sr-RS', {
                            dateStyle: 'short',
                            timeStyle: 'short',
                            // timeZone: 'Europe/Belgrade' // možeš dodati ako ti treba lokalna vremenska zona
                          })
                        };
                      });

                      return {
                        ...reservation,
                        details: formattedDetails
                      };
                    });

                } catch (e) {
                  // Dodatna obrada greške ako je potrebna
                }
              },
              async fetchReservationDetails(reservationId) {

                try {
                  this.reservations = await this.fetchData('/api/reservation-details/', { reservationId });
                } catch (e) {
                  // Dodatna obrada greške ako je potrebna
                }
              },
              async postReservation() {
                const reservationFormDate = new Date(this.reservationForm.date_from)

                if (reservationFormDate.getDate() < this.todayDate.getDate() && this.user.role === 'user'){
                    this.showNotification('Greška pri slanju rezervacije, datum ne može biti u prošlosti.', 'error');
                    return;
                }

                const data = {
                  date: this.reservationForm.date_from,
                  end_date: this.reservationForm.date_to,
                  stage: this.selectedStage.symbol,
                  lounger_position: this.selectedCell.label,
                  status: this.reservationForm.status,
                  user: 1,
                  details: [
                    {
                        price: this.reservationForm.price,
                        description: this.reservationForm.description,
                    }
                  ]
                };

                try {
                  const result = await this.postData('/api/reservations/create/', data);
                  this.fetchReservations();
//                  this.fetchRevenue();
                  this.showNotification('Uspešno rezervisano!', 'success');
                } catch (error) {
                  if (error.response && error.response.status === 409) {
                    this.showNotification(error.response.data.error, 'error' );
                  } else {
                    this.showNotification('Greška pri slanju rezervacije.', 'error');
                  }
                }
              },
              openReservationModal(cell) {
                this.selectedCell = cell;
                this.reservationForm = {
                    status: this.selectedCell.status,
                    price: this.selectedCell.price,
                    date_from: this.selectedCell.reservation ? this.selectedCell.reservation.date : '',
                    date_to: this.selectedCell.reservation ? this.selectedCell.reservation.end_date : '',
                  }
                this.modalOpen = true;
              },
              closeReservationModal() {
                this.selectedCell = false;
                this.modalOpen = false;
              },
              async submitReservationForm() {
                  const confirmed = await this.openDialog('save');
                  let date_from = new Date(this.reservationForm.date_from);
                  let date_to = new Date(this.reservationForm.date_to);

                  if (!confirmed) {
                    return;
                  }

                  if (this.reservationForm.status !== 'reserved' && this.reservationForm.status !== 'signature') {
                      const localDate = this.currentDate.toLocaleDateString('en-CA');
                      this.reservationForm.date_from = localDate;
                      this.reservationForm.date_to = localDate;
                    }

                  if (!this.validateDates(date_from, date_to)){
                    return;
                  }

                  this.postReservation();
                  this.closeReservationModal();

              },
              onStatusChange() {
                if (this.reservationForm.status === 'available' || this.reservationForm.status === 'signature') {
                    this.reservationForm.price = 0;
                } else {
                    this.reservationForm.price = this.selectedCell.price
                }
              },
              openDialog(type) {
                let message = ''
                this.dialogType = type;
                this.dialogVisible = true;

                if (type === 'delete') {
                  this.dialogTitle = 'Potvrda brisanja';
                  this.dialogMessage = 'Da li ste sigurni da želite da obrišete?';
                } else if (type === 'add') {
                  this.dialogTitle = 'Potvrda dodavanja';
                  this.dialogMessage = 'Da li želite da dodate ovaj podatak?';
                } else if (type === 'save') {
                  this.dialogTitle = 'Potvrda čuvanja';
                  this.dialogMessage = 'Da li želite da sačuvate izmene?';
                } else if (type === 'logout'){
                  this.dialogTitle = 'Odjava';
                  this.dialogMessage = 'Da li želite da se odjavite?';
                } else{
                  this.dialogTitle = 'Potvrda';
                  this.dialogMessage = 'Da li želite da nastavite?';
                }

                // Vrati Promise da možeš čekati na odgovor korisnika
                return new Promise((resolve) => {
                  this.dialogResolve = resolve;
                });
              },
              confirmDialog() {
                this.dialogVisible = false;
                if (this.dialogResolve) {
                  this.dialogResolve(true);
                }
              },
              cancelDialog() {
                this.dialogVisible = false;
                if (this.dialogResolve) {
                  this.dialogResolve(false);
                }
              },
              async deleteDetails(id){
                  const confirmed = await this.openDialog('delete');
                  if (!confirmed) {
//                    console.log('Korisnik je otkazao brisanje');
                    return;
                  }
                  try {
                      const result = await this.deleteData('/api/reservation-details/' + id +'/delete/');
                      this.fetchReservations();
                      this.closeReservationModal()
    //                  this.fetchRevenue();
                      this.showNotification('Uspešno obrisano!', 'success');
                    } catch (error) {
                        console.log(error)
                      if (error.response && error.response.status === 409) {
                        this.showNotification('Ležaljka je već rezervisana.', 'error');
                      } else {
                        this.showNotification('Greška pri brisanju rezervacije.', 'error');
                      }
                    }
              },
              // Primer korišćenja u nekoj metodi, npr brisanje
              async tryDelete() {
                const confirmed = await this.openDialog('delete');
                if (confirmed) {
                  // Izvrši brisanje
                  console.log('Brisanje potvrđeno');
                } else {
                  console.log('Brisanje otkazano');
                }
              },
              showNotification(message, type = 'success') {
                this.notification.message = message;
                this.notification.type = type;
                this.notification.show = true;

                // Automatski nestane nakon 3 sekunde
                setTimeout(() => {
                  this.notification.show = false;
                }, 3000);
              },
              validateDates(startDate, endDate){
                 if(this.normalizeDate(startDate) > this.normalizeDate(endDate)){
                        this.showNotification('Početni datum ne može biti stariji od datuma završetka.', 'error');
                        return false;
                   }

                  if((this.normalizeDate(startDate) < this.normalizeDate(this.todayDate)) && this.user.role === 'user'){
                        this.showNotification('Rezervacije u prošlosti nisu moguće.', 'error');
                        return false;
                   }
                   return true
              },
              normalizeDate(date) {
                  const d = new Date(date);
                  d.setHours(0, 0, 0, 0);
                  return d;
                },
              async submitLogoutForm(){
                const confirmed = await this.openDialog('logout');
                const form = document.getElementById('logout-form');

                  if (!confirmed) {
                    return;
                  }
                  if (form) {
                    form.submit();
                  } else {
                    console.warn('Logout form not found');
                  }
              },
              convertDDMMYYYYtoYMD(dateStr) {
                  // očekuje dd/mm/yyyy
                  const [day, month, year] = dateStr.split('/');
                  return `${year}-${month}-${day}`;  // ispravan redosled
                },
              formatDateDDMMYYYY(date) {
                const d = date.getDate().toString().padStart(2, '0');
                const m = (date.getMonth() + 1).toString().padStart(2, '0');
                const y = date.getFullYear();
                return `${d}/${m}/${y}`;
              },
          },
      computed: {
          formattedDate() {
            return this.currentDate.toLocaleDateString('sr-Latn-RS', {
              weekday: 'long',
              day: '2-digit',
              month: 'long',
              year: 'numeric',
            });
          },
          getUserStages(){
            let results = [];
            const stages = this.stages;
            if (this.user.role == 'admin' || this.user.role == 'moderator'){
                results = stages
            }else{
                let stage = stages.find(stage => stage.symbol == this.user.stage)
                results.push(stage);
            }
            return results;
          }
        },
      watch: {
        selectedStage(stage) {
          this.fetchReservations();
          if (stage?.symbol && !this.stageLayouts[stage.symbol]) {
            this.fetchStageLayout(stage.symbol);
          }
        },
        currentDate() {
          this.fetchReservations();

          if (this.user.role === 'user' && this.normalizeDate(this.currentDate) < this.normalizeDate(this.todayDate)){
            if(this.showRevenue){
                this.showRevenue = false
                this.showNotification('Prikaz statistike u prošlosti je onemogućen.', 'error');
            }
          }else{
            if (this.revenue){
                this.fetchRevenue(this.currentDate);
            }
          }
        },
        showRevenue(){
            if (this.user.role === 'user' && this.normalizeDate(this.currentDate) < this.normalizeDate(this.todayDate)){
                this.showRevenue = false
                this.showNotification('Prikaz statistike u prošlosti je onemogućen.', 'error');
            }else{
                if (this.revenue){
                    this.fetchRevenue(this.currentDate);
                }
            }
        },


       }
    });

    // 👇 Ovde dodajemo custom delimiters
    app.config.compilerOptions.delimiters = ['[[', ']]'];
    app.mount('#app');

