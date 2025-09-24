let color_ascii;
let color;
function init() {
  script = window.location.pathname.split("/").pop();
  initTable(script);
  color_ascii = [];
  color = [];
}

async function initTable(script) {
  fetch("http://127.0.0.1:8000/" + script + "/initTable", {
    method: "POST",
    headers: {"Content-Type": "application/json"}})
  .then(res => res.json())
  .then(data => {
    if (script == "script") {
      const resultDiv = document.getElementById("verse");
      resultDiv.innerHTML = data.verse;
      const result = document.getElementById("movie");
      result.innerHTML = data.movie;
    }
    else {
      const headerRow = document.getElementById("tableHeader");
      data.lieux.forEach(col => {
        if (col != 'id') {
          const th = document.createElement("th");
          th.textContent = col;
          headerRow.appendChild(th);
        }
      });
    }
    autocomplete(document.getElementById("guessInput"), get_name(data.name));
    updateHistoryTable(script);
    DisplayOldGuess(script);
    return 0;
  })
}

function checkGuess() {
  script = window.location.pathname.split("/").pop();
  const guessInput = document.getElementById("guessInput");
  const guess = guessInput.value.trim();
  const resultDiv = document.getElementById("result");
  resultDiv.textContent = "";
  const gues = Array.isArray(guess) ? guess : [guess];
  FetchAndAnswer(gues, resultDiv, 1, script);
  guessInput.value = "";
}

function handleKey(event) {
  if (event.key === "Enter") {
    checkGuess();
  }
}

function SaveAndHistory(guess, foundText, script) {
  const today = new Date().toLocaleDateString("fr-FR");
  let guessTable = getCookie("guess_" + script);
  guessTable += guess + ',';
  let guess_let = guessTable.split("\\").join('');
  guess_let = guess_let.split("\"").join('');
  setCookie("guess_" + script, JSON.stringify(guess_let), 1);
  let guessCount = (getCookie("guess_" + script).split(',')).length - 1;
  saveDailyAttempt(today, guessCount, foundText, script);
  document.getElementById("tentative").innerHTML = "<br>Nombre de tentatives : " + guessCount;
  updateHistoryTable(script);
}

async function FetchAndAnswer(guess, resultDiv, sigle_guess, script) {
  let foundText = "non trouvé";
  const fetchpromises = guess.map(i => fetch("http://127.0.0.1:8000/" + script + "/checkGuess", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({'name':i})}).then(res => res.json()).catch(err => `Erreur ${i}: ${err}`));
  Promise.all(fetchpromises).then(results => {
    results.forEach((result, index) => {
      const tbody = document.querySelector("#dynamicTable tbody");
      const tr = document.createElement("tr");
      if (tbody.childNodes.length > 1)
        tbody.insertBefore(tr, tbody.childNodes[0]);
      else
        tbody.appendChild(tr);
      if (!result || !result.columns || result.columns.length == 0)
        return;
      result.columns.forEach(col => {
        const td = document.createElement("td");
        td.innerHTML = col;
        tr.appendChild(td);
      });
      calcul_color(result.color);
      if (result.found == 1) {
        resultDiv.innerHTML = "<span style='color:#3af821;'>BRAVO !</span>";
        guessInput.disabled = true;
        document.getElementById("share").disabled = false;
        if (script == "script")
          console.log(guess)
          console.log(guess.length)
          if (guess.length == 1)
            searchYouTubeVideo(result.verse + " " + guess[0] + " " + result.movie);
          else
            searchYouTubeVideo(result.verse + " " + guess[guess.length-2] + " " + result.movie);
      }
      foundText = result.found == 1 ? "trouve" : "non trouve";
      if (sigle_guess)
        SaveAndHistory(guess, foundText, script);
    });
  });
}

function minutesUntilMidnight(days) {
    var midnight = new Date();
    midnight.setHours( 24 * days);
    midnight.setMinutes( 0 );
    midnight.setSeconds( 0 );
    midnight.setMilliseconds( 0 );
    return midnight;
}
function setCookie(name, value, days) {
  const mid = minutesUntilMidnight(days);
  const expires = "expires=" + mid;
  document.cookie = name + "=" + value + ";" + expires + ";path=/";
}

function getCookie(name) {
  const cname = name + "=";
  const decodedCookie = decodeURIComponent(document.cookie);
  const ca = decodedCookie.split(';');
  for(let i = 0; i < ca.length; i++) {
    let c = ca[i].trim();
    if (c.indexOf(cname) === 0) {
      return c.substring(cname.length, c.length);
    }
  }
  return "";
}

function saveDailyAttempt(date, attempts, result, script) {
  let history = JSON.parse(getCookie("history_" + script) || "[]");
  history = history.filter(entry => entry.date !== date);
  history.push({ date, attempts, result });
  history = history.slice(-7);
  setCookie("history_" + script, JSON.stringify(history), 7);
}
function DisplayOldGuess(script) {
  const resultDiv = document.getElementById("result");
  const guess = (getCookie("guess_" + script)).split(',');
  FetchAndAnswer(guess, resultDiv, 0, script);

}
function updateHistoryTable(script) {
  const tbody = document.querySelector("#historyTable tbody");
  tbody.innerHTML = "";
  const history = JSON.parse(getCookie("history_" + script) || "[]");
  if (history.length == 0)
    return;
  history.forEach(entry => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${entry.date}</td>
      <td>${entry.attempts}</td>
      <td>${entry.result}</td>
    `;
    tbody.appendChild(tr);
  });
}
function get_name(data_name) {
  let name = [];
  for (let index = 0; index < data_name.length; index++) {
    name.push(data_name[index]);
  }
  return name;
}
function calcul_color(color_guess) {
  for (let index = 0; index < color_guess.length; index++) {
    color.push(color_guess[index]);
  }
  color.sort();
  let counts = {};
  for (const num of color) {
    counts[num] = counts[num] ? counts[num] + 1 : 1;
  }
  color_ascii = "";
  for (let index = 0; index < 10; index++) {
    if (index < Math.floor(10*counts["green"]/color.length))
      color_ascii += "🟩";
    else if (index <= Math.floor((10*counts["green"]/color.length) + Math.floor((10*counts["orange"]/color.length)+1)))
      color_ascii += "🟧";
    else
      color_ascii += "🟥";
  };
  document.getElementById("color").innerHTML = color_ascii;
}
function share() {
  script = window.location.pathname.split("/").pop();
  let guessCount = (getCookie("guess_" + script).split(',')).length - 1;
  let copyText = "Guess: " + color_ascii + "\nNombre de tentatives : " + guessCount
  navigator.clipboard.writeText(copyText);
  alert("Copied the text: " + copyText);
}
function autocomplete(entree, arr) {
  /*the autocomplete function takes two arguments,
  the text field element and an array of possible autocompleted values:*/
  var currentFocus;
  /*execute a function when someone writes in the text field:*/
  entree.addEventListener("input", function(e) {
      var a, b, i, val = this.value;
      /*close any already open lists of autocompleted values*/
      closeAllLists();
      if (!val || val.length < 2) { return false;}
      currentFocus = -1;
      /*create a DIV element that will contain the items (values):*/
      a = document.createElement("DIV");
      a.setAttribute("id", this.id + "autocomplete-list");
      a.setAttribute("class", "autocomplete-items");
      /*append the DIV element as a child of the autocomplete container:*/
      this.parentNode.appendChild(a);
      /*for each item in the array...*/
      for (i = 0; i < arr.length; i++) {
        /*check if the item starts with the same letters as the text field value:*/
        if (arr[i].substr(0, val.length).toUpperCase() == val.toUpperCase()) {
          /*create a DIV element for each matching element:*/
          b = document.createElement("DIV");
          /*make the matching letters bold:*/
          b.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>";
          b.innerHTML += arr[i].substr(val.length);
          /*insert a input field that will hold the current array item's value:*/
          b.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";
          /*execute a function when someone clicks on the item value (DIV element):*/
          b.addEventListener("click", function(e) {
              /*insert the value for the autocomplete text field:*/
              entree.value = this.getElementsByTagName("input")[0].value;
              /*close the list of autocompleted values,
              (or any other open lists of autocompleted values:*/
              closeAllLists();
          });
          a.appendChild(b);
        }
      }
  });
  /*execute a function presses a key on the keyboard:*/
  entree.addEventListener("keydown", function(e) {
      var x = document.getElementById(this.id + "autocomplete-list");
      if (x) x = x.getElementsByTagName("div");
      if (e.keyCode == 40) {
        /*If the arrow DOWN key is pressed,
        increase the currentFocus variable:*/
        currentFocus++;
        /*and and make the current item more visible:*/
        addActive(x);
      } else if (e.keyCode == 38) { //up
        /*If the arrow UP key is pressed,
        decrease the currentFocus variable:*/
        currentFocus--;
        /*and and make the current item more visible:*/
        addActive(x);
      } else if (e.keyCode == 13) {
        /*If the ENTER key is pressed, prevent the form from being submitted,*/
        e.preventDefault();
        if (currentFocus > -1) {
          /*and simulate a click on the "active" item:*/
          if (x) x[currentFocus].click();
        }
      }
  });
  function addActive(x) {
    /*a function to classify an item as "active":*/
    if (!x) return false;
    /*start by removing the "active" class on all items:*/
    removeActive(x);
    if (currentFocus >= x.length) currentFocus = 0;
    if (currentFocus < 0) currentFocus = (x.length - 1);
    /*add class "autocomplete-active":*/
    x[currentFocus].classList.add("autocomplete-active");
  }
  function removeActive(x) {
    /*a function to remove the "active" class from all autocomplete items:*/
    for (var i = 0; i < x.length; i++) {
      x[i].classList.remove("autocomplete-active");
    }
  }
  function closeAllLists(elmnt) {
    /*close all autocomplete lists in the document,
    except the one passed as an argument:*/
    var x = document.getElementsByClassName("autocomplete-items");
    for (var i = 0; i < x.length; i++) {
      if (elmnt != x[i] && elmnt != entree) {
        x[i].parentNode.removeChild(x[i]);
      }
    }
  }
  /*execute a function when someone clicks in the document:*/
  document.addEventListener("click", function (e) {
      closeAllLists(e.target);
      checkGuess();
  });
}

async function searchYouTubeVideo(quote) {
  const resultvideo = document.getElementById("video");
  fetch("http://localhost:8000/youtube-search?q=" + quote)
    .then(res => res.json())
    .then(data => {
      if (data.videoId) {
            const videoUrl = `https://www.youtube.com/watch?v=${data.videoId}`;
            document.getElementById("video-link").innerHTML = `
              <a href="${videoUrl}" target="_blank" style="color: #ffffffff; text-decoration: none;">Voir la vidéo sur YouTube</a>`;
          } else {
            document.getElementById("video-link").innerText = "Vidéo non trouvée.";
          }
    })
}
function showPopup() {
  document.getElementById('popup').style.display = 'flex';
}
function closePopup() {
  document.getElementById('popup').style.display = 'none';
}