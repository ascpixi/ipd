// @ts-check
(() => {
    "use strict";

    /**
     * Stores tuples of score deltas, `(A, B)`. Can be indexed via the turns of both players,
     * first B, then A. This should be synchronized with `/src/run.py`.
     * 
     * @type { [number, number][][] }
     */
    const SCORE_MATRIX = [
        // A defects        // A cooperates
        [ [1, 1],           [0, 5]         ],  // B defects
        [ [5, 0],           [3, 3]         ]   // B cooperates
    ]

    /**
     * @param {string} selector
     * @returns {any}
     */
    const qs = (selector) => {
        const element = document.querySelector(selector);
        if (!element)
            throw new Error(`No matching element: ${selector}`)

        return element;
    }

    const elements = {
        /** @type {HTMLTableSectionElement} */
        leaderboardEntries: qs("#leaderboard-entries"),

        /** @type {HTMLSelectElement} */
        matchupFilter: qs("#matchup-filter"),

        /** @type {HTMLInputElement} */
        shouldFilter: qs("#should-filter"),

        /** @type {HTMLElement} */
        matchupList: qs("#matchup-list"),

        /** @type {HTMLButtonElement} */
        btnOpenResults: qs("#btn-open-results")
    };

    /** @type {Tournament | null} */
    let currentTournament = null;

    /**
     * @typedef {{
     *     name: string,
     *     score: number,
     *     history: string
     * }} StrategyResult
     */

    /**
     * @typedef {{
     *     leaderboard: { [name: string]: number },
     *     matches: {
     *         s1: StrategyResult,
     *         s2: StrategyResult
     *     }[]
     * }} Tournament
     */

    /**
     * @param {Tournament} results 
     */
    const loadResults = (results) => {
        currentTournament = results;

        const sortedScores = new Map(
            [...Object.entries(results.leaderboard)].sort((a, b) => b[1] - a[1])
        );

        elements.leaderboardEntries.innerHTML = "";

        for (let i = 0; i < sortedScores.size; i++) {
            const [name, score] = [...sortedScores.entries()][i];

            elements.leaderboardEntries.innerHTML += /*html*/`
                <tr>
                    <td>${i + 1}</td>
                    <td>${name}</td>
                    <td>${score.toFixed(3)}</td>
                </tr>
            `;
        }

        elements.matchupFilter.innerHTML = "";
        for (const solution of sortedScores.keys()) {
            const option = document.createElement("option");
            option.text = solution;

            elements.matchupFilter.options.add(option);
        }

        updateMatchups();
    }

    const updateMatchups = () => {
        if (!currentTournament)
            throw new Error("Attempted to update the matchups while there is no results file loaded");

        const filterBy = elements.shouldFilter.checked
            ? elements.matchupFilter.options[elements.matchupFilter.selectedIndex].text
            : null;

        const matchups = filterBy != null
            ? currentTournament.matches.filter(x => [x.s1.name, x.s2.name].includes(filterBy))
            : currentTournament.matches;

        elements.matchupList.innerHTML = "";

        for (let { s1, s2 } of matchups) {
            if (s1.history.length != s2.history.length) {
                console.error(`The histories of ${s1.name} and ${s2.name} differ in length!`, s1, s2);
                throw new Error("The histories of two strategies differ in length.");
            }

            if (filterBy && s1.name != filterBy) {
                // Make sure the solution we are filtering by is always at the top
                [s1, s2] = [s2, s1];
            }

            // Compute the average score for each round. For example, if both
            // solutions always cooperated, the average will be 3.00 for both of them.
            let s1Sum = 0;
            let s2Sum = 0;

            for (let i = 0; i < s1.history.length; i++) {
                const scores = SCORE_MATRIX[parseInt(s2.history[i])][parseInt(s1.history[i])];
                s1Sum += scores[0];
                s2Sum += scores[1];
            }

            const s1Avg = s1Sum / s1.history.length;
            const s2Avg = s2Sum / s2.history.length;

            let s1History = "";
            let s2History = "";

            for (let i = 0; i < s1.history.length; i++) {
                let s1Class, s2Class;

                if (s1.history[i] == "0" && s2.history[i] == "0") {
                    s1Class = s2Class = "dfct-tie";
                } else if (s1.history[i] == "1" && s2.history[i] == "0") {
                    s1Class = "coop-lost";
                    s2Class = "dfct-win";
                } else if (s1.history[i] == "0" && s2.history[i] == "1") {
                    s1Class = "dfct-win";
                    s2Class = "coop-lost";
                } else {
                    s1Class = s2Class = "coop-tie";
                }

                s1History += /*html*/`<div class="${s1Class}"></div>`;
                s2History += /*html*/`<div class="${s2Class}"></div>`;
            }

            elements.matchupList.innerHTML += /*html*/`
                <div class="matchup">
                    <div class="header"><b>${s1.name}</b> vs <b>${s2.name}</b></div>
                    <div class="rows">
                        <div>
                            <div class="name">${s1.name}</div>
                            <div class="avg">${s1Avg.toFixed(3)}</div>
                            <div class="history">${s1History}</div>
                        </div>

                        <div>
                            <div class="name">${s2.name}</div>
                            <div class="avg">${s2Avg.toFixed(3)}</div>
                            <div class="history">${s2History}</div>
                        </div>
                    </div>
                </div>
            `;
        }
    };

    elements.btnOpenResults.addEventListener("click", () => {
        const input = document.createElement("input");
        input.type = "file";
        input.accept = "application/json";
        input.onchange = (ev) => {
            if (!ev.target || !(ev.target instanceof HTMLInputElement) || !ev.target.files)
                return;

            /** @type {File} */
            const file = ev.target.files[0];

            const reader = new FileReader();
            reader.readAsText(file, "UTF-8");

            reader.onload = (ev) => {
                try {
                    if (!ev.target)
                        return;

                    const text = ev.target.result;
                    if (typeof text !== "string") {
                        console.log("ev.target.result was of an invalid type:", text);
                        throw new Error("Invalid file object type.")
                    }
    
                    loadResults(JSON.parse(text));
                } catch (err) {
                    alert(`Oops, we couldn't load that file... ${err}`);
                    throw err;
                }
            };
        };

        input.click();
    });

    elements.shouldFilter.addEventListener("change", () => {
        if (currentTournament == null)
            return;

        elements.matchupFilter.disabled = !elements.shouldFilter.checked;
        updateMatchups();
    });

    elements.matchupFilter.addEventListener("change", () => {
        if (currentTournament == null || !elements.shouldFilter.checked)
            return;

        updateMatchups();
    });
})();