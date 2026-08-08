let config;
let params;
let results;

let sortColumn = "zscore";
let sortDirection = "desc";

const TEAM_COLORS = {
    "Ferrari": "#ffe5e5",
    "McLaren": "#fff0d9",
    "Mercedes": "#e3f8f8",
    "Red Bull": "#e7ecff",
    "Williams": "#eaf4ff",
    "Renault": "#fff7d6",
    "BMW Sauber": "#eef3ff",
    "Jordan": "#fff8cc",
    "Benetton": "#dff7df",
    "Brawn": "#f1ffe0",
};

const sortCycle = {
    null: "desc",
    desc: "asc",
    asc: null,
};

function compare(a, b) {
    let va = a[sortColumn];
    let vb = b[sortColumn];

    if (typeof va === "string")
        return va.localeCompare(vb);

    return va - vb;
}

function sortedResults() {
    let arr = [...results];

    if (sortDirection !== null) {
        arr.sort(compare);

        if (sortDirection === "desc")
            arr.reverse();
    } else {
        arr.sort((a, b) => b.zscore - a.zscore);
    }

    const query = document
        .getElementById("search")
        .value
        .trim()
        .toLowerCase();
    const tokens = query
        .split(/\s+/)
        .filter(x => x.length);

    if (tokens.length) {
        arr = arr.filter(driver => {
            const haystack =
                `${driver.name} ${driver.team}`
                .toLowerCase();

            return tokens.every(token =>
                haystack.includes(token)
            );
        });
    }

    return arr;
}

function updateSortIndicators() {

    document.querySelectorAll("th[data-column]").forEach(th => {

        const column = th.dataset.column;

        let text = th.dataset.title;

        if (column === sortColumn) {
            if (sortDirection === "desc")
                text += " ↓";
            else if (sortDirection === "asc")
                text += " ↑";
        }

        th.textContent = text;
    });
}

function render() {

    let data = sortedResults();

    const limit = Number(document.getElementById("limit").value);

    data = data.slice(0, limit);

    const tbody = document.querySelector("tbody");

    tbody.innerHTML = "";

    data.forEach((driver, idx) => {

        tbody.insertAdjacentHTML(
            "beforeend",
            `
<tr>
<td class="numeric">${idx + 1}</td>
<td class="driver-name">${driver.name}</td>
<td
    class="team-name"
    style="background:${TEAM_COLORS[driver.team] ?? "transparent"}"
>
    ${driver.team}
</td>
<td class="numeric">${driver.zscore.toFixed(2)}</td>
<td class="numeric">${driver.zscoreRank}</td>
<td class="numeric">${driver.elo.toFixed(0)}</td>
<td class="numeric">${driver.date}</td>
</tr>
`
        );
    });
}

async function load() {

    config = await fetch("config.json").then(r => r.json());

    params = await fetch(config.result + "/params.json")
        .then(r => r.json());

    dataset_stats = await fetch(config.result + "/dataset_stats.json")
        .then(r => r.json());

    results = await fetch(config.result + "/results.json")
        .then(r => r.json());

    results.forEach((driver, index) => {
        driver.zscoreRank = index + 1;
    });

    document.title = config.title;

    document.getElementById("title").innerText = config.title;

    document.getElementById("meta").innerHTML = `
        <div class="label">Algorithm</div>
        <div>Codeforces rating algorithm adapted for Formula&nbsp;1</div>

        <div class="label">Ranking</div>
        <div>Peak ${params.YEARS_BACK}-year rolling z-score of Elo rating</div>

        <div class="label">Dataset</div>
        <div>Kaggle (rohanrao), Formula&nbsp;1 (${dataset_stats.MIN_YEAR}-${dataset_stats.MAX_YEAR})</div>

        <div class="label">Drivers</div>
        <div>${results.length}</div>

        <div class="label">Result</div>
        <div><code>${config.result.split("/").pop()}</code></div>
        `;

    document
        .querySelectorAll("th[data-column]")
        .forEach(th => {

            th.onclick = () => {

                const column = th.dataset.column;

                if (column === "rank")
                    return;

                if (column !== sortColumn) {
                    sortColumn = column;
                    sortDirection = "desc";
                } else {
                    sortDirection = sortCycle[sortDirection];
                }
                updateSortIndicators();

                render();
            };
        });

    document
        .getElementById("limit")
        .onchange = render;

    document
        .getElementById("search")
        .oninput = render;

    render();
}

load();
