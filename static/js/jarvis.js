// ============================================================
// JARVIS AI FINANCIAL ASSISTANT
// Smart Finance Insights
// ============================================================

document.addEventListener("DOMContentLoaded", function () {

    loadJarvisDashboard();

    const input = document.getElementById("question");

    if (input) {
        input.addEventListener("keydown", function (event) {
            if (event.key === "Enter") {
                event.preventDefault();
                sendMessage();
            }
        });
    }

    const mic = document.getElementById("mic");

    if (mic) {
        mic.addEventListener("click", startVoice);
    }
});


// ============================================================
// LOAD DASHBOARD DATA
// ============================================================

async function loadJarvisDashboard() {

    try {

        const response = await fetch("/jarvis_dashboard");

        if (!response.ok) {
            console.log("Dashboard API not available");
            return;
        }

        const data = await response.json();

        updateDashboardCards(data);

        updateTips(data);

        updateAlerts(data);

        drawFinanceChart(data);

    } catch (error) {

        console.log("Dashboard loading error:", error);

    }
}


// ============================================================
// UPDATE SUMMARY CARDS
// ============================================================

function updateDashboardCards(data) {

    setText("incomeCard", money(data.total_income));

    setText("expenseCard", money(data.total_expense));

    setText("savingCard", money(data.total_savings));

    setText("healthCard", (data.health_score ?? 0) + "/100");

    setText("roiCard", (data.roi ?? 0) + "%");

    setText("investmentCard", money(data.total_investment));

    setText("currentValueCard", money(data.current_value));

    setText("budgetCard", money(data.total_budget));
}


// ============================================================
// SEND QUESTION
// ============================================================

async function sendMessage() {

    const input = document.getElementById("question");

    if (!input) return;

    const question = input.value.trim();

    if (!question) return;

    addUserMessage(question);

    input.value = "";

    const typing = addTypingMessage();

    try {

        const response = await fetch("/jarvis_chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                question: question
            })

        });

        const data = await response.json();

        removeTypingMessage(typing);

        if (!response.ok) {

            addBotMessage(
                "⚠️ Jarvis could not process your question right now."
            );

            console.error(data);

            return;
        }

        /*
         * Backend can return:
         *
         * reply
         * answer
         * message
         *
         * So we support all three.
         */

        const answer =
            data.reply ||
            data.answer ||
            data.message ||
            "I could not find a suitable answer.";

        addBotMessage(answer);

        // Update cards if backend sends them
        updateDashboardCards(data);

        // Update tips and alerts
        updateTips(data);

        updateAlerts(data);

        // Draw relevant chart
        if (data.chart) {

            createChatChart(data.chart);

        } else {

            createAutomaticChart(data, question);

        }

    } catch (error) {

        removeTypingMessage(typing);

        console.error("JARVIS ERROR:", error);

        addBotMessage(
            "⚠️ Unable to connect with Jarvis. Please check the Flask server."
        );
    }
}


// ============================================================
// USER MESSAGE
// ============================================================

function addUserMessage(message) {

    const chatBox = document.getElementById("chatBox");

    if (!chatBox) return;

    const div = document.createElement("div");

    div.className = "user-message";

    div.innerHTML = `
        <div>
            <b>You</b>
        </div>

        <div>
            ${escapeHTML(message)}
        </div>
    `;

    chatBox.appendChild(div);

    scrollChat();
}


// ============================================================
// BOT MESSAGE
// ============================================================

function addBotMessage(message) {

    const chatBox = document.getElementById("chatBox");

    if (!chatBox) return;

    const div = document.createElement("div");

    div.className = "bot-message";

    div.innerHTML = `
        <div>
            🤖 <b>JARVIS</b>
        </div>

        <div class="jarvis-answer">
            ${formatAnswer(message)}
        </div>
    `;

    chatBox.appendChild(div);

    scrollChat();
}


// ============================================================
// TYPING MESSAGE
// ============================================================

function addTypingMessage() {

    const chatBox = document.getElementById("chatBox");

    if (!chatBox) return null;

    const div = document.createElement("div");

    div.className = "bot-message typing-message";

    div.innerHTML = `
        🤖 <b>JARVIS</b>
        <br>
        <span>Thinking...</span>
    `;

    chatBox.appendChild(div);

    scrollChat();

    return div;
}


function removeTypingMessage(element) {

    if (element && element.parentNode) {
        element.parentNode.removeChild(element);
    }
}


// ============================================================
// FORMAT ANSWER
// ============================================================

function formatAnswer(text) {

    if (!text) return "";

    let answer = escapeHTML(String(text));

    answer = answer.replace(/\n/g, "<br>");

    answer = answer.replace(
        /\*\*(.*?)\*\*/g,
        "<strong>$1</strong>"
    );

    answer = answer.replace(
        /₹([\d,]+(?:\.\d+)?)/g,
        "<strong>₹$1</strong>"
    );

    return answer;
}


// ============================================================
// AUTOMATIC RELEVANT CHART
// ============================================================

function createAutomaticChart(data, question) {

    const q = question.toLowerCase();

    /*
     * Income / Expense / Savings
     */

    if (
        q.includes("income") ||
        q.includes("expense") ||
        q.includes("spending") ||
        q.includes("saving") ||
        q.includes("earn")
    ) {

        createFinancialChart(data);

        return;
    }


    /*
     * Investment / ROI / Portfolio
     */

    if (
        q.includes("investment") ||
        q.includes("portfolio") ||
        q.includes("roi") ||
        q.includes("profit") ||
        q.includes("loss")
    ) {

        createInvestmentChart(data);

        return;
    }


    /*
     * Budget
     */

    if (
        q.includes("budget") ||
        q.includes("overspend")
    ) {

        createBudgetChart(data);

        return;
    }


    /*
     * Category spending
     */

    if (
        q.includes("category") ||
        q.includes("spending most") ||
        q.includes("spending the most")
    ) {

        createCategoryChart(data);

        return;
    }
}


// ============================================================
// FINANCIAL CHART
// ============================================================

function createFinancialChart(data) {

    const chartId = "chart_" + Date.now();

    addChartContainer(
        chartId,
        "📊 Financial Overview"
    );

    const canvas = document.getElementById(chartId);

    if (!canvas) return;

    new Chart(canvas, {

        type: "bar",

        data: {

            labels: [
                "Income",
                "Expense",
                "Savings"
            ],

            datasets: [{

                label: "Amount",

                data: [
                    Number(data.total_income || 0),
                    Number(data.total_expense || 0),
                    Number(data.total_savings || 0)
                ]

            }]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            plugins: {

                legend: {
                    display: true
                }

            }

        }

    });
}


// ============================================================
// INVESTMENT CHART
// ============================================================

function createInvestmentChart(data) {

    const chartId = "chart_" + Date.now();

    addChartContainer(
        chartId,
        "📈 Investment Portfolio"
    );

    const canvas = document.getElementById(chartId);

    if (!canvas) return;

    new Chart(canvas, {

        type: "bar",

        data: {

            labels: [
                "Invested",
                "Current Value"
            ],

            datasets: [{

                label: "Portfolio",

                data: [
                    Number(data.total_investment || 0),
                    Number(data.current_value || 0)
                ]

            }]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false

        }

    });
}


// ============================================================
// BUDGET CHART
// ============================================================

function createBudgetChart(data) {

    const chartId = "chart_" + Date.now();

    addChartContainer(
        chartId,
        "💰 Budget Overview"
    );

    const canvas = document.getElementById(chartId);

    if (!canvas) return;

    new Chart(canvas, {

        type: "doughnut",

        data: {

            labels: [
                "Expense",
                "Remaining Budget"
            ],

            datasets: [{

                data: [

                    Number(data.total_expense || 0),

                    Math.max(
                        Number(data.total_budget || 0)
                        -
                        Number(data.total_expense || 0),
                        0
                    )

                ]

            }]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false

        }

    });
}


// ============================================================
// CATEGORY CHART
// ============================================================

function createCategoryChart(data) {

    if (
        !data.categories ||
        !Array.isArray(data.categories)
    ) {
        return;
    }

    const labels = [];
    const values = [];

    data.categories.forEach(function (item) {

        labels.push(
            item.category || item.name || "Other"
        );

        values.push(
            Number(item.amount || item.value || 0)
        );

    });

    if (!labels.length) return;

    const chartId = "chart_" + Date.now();

    addChartContainer(
        chartId,
        "📊 Spending by Category"
    );

    const canvas = document.getElementById(chartId);

    if (!canvas) return;

    new Chart(canvas, {

        type: "doughnut",

        data: {

            labels: labels,

            datasets: [{

                data: values

            }]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false

        }

    });
}


// ============================================================
// BACKEND PROVIDED CHART
// ============================================================

function createChatChart(chart) {

    if (!chart) return;

    const chartId = "chart_" + Date.now();

    addChartContainer(
        chartId,
        chart.title || "📊 Financial Analysis"
    );

    const canvas = document.getElementById(chartId);

    if (!canvas) return;

    let type = chart.type || "bar";

    let labels = chart.labels || [];

    let values = chart.values || [];

    if (
        chart.data &&
        Array.isArray(chart.data)
    ) {

        labels = chart.data.map(
            x => x.label || x.category || x.name
        );

        values = chart.data.map(
            x => Number(x.value || x.amount || 0)
        );
    }

    new Chart(canvas, {

        type: type,

        data: {

            labels: labels,

            datasets: [{

                label: chart.label || "Financial Data",

                data: values

            }]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false

        }

    });
}


// ============================================================
// CHART CONTAINER
// ============================================================

function addChartContainer(id, title) {

    const chatBox = document.getElementById("chatBox");

    if (!chatBox) return;

    const wrapper = document.createElement("div");

    wrapper.className = "bot-message chart-message";

    wrapper.innerHTML = `

        <div>

            🤖 <b>JARVIS</b>

        </div>

        <div class="chart-title">

            ${escapeHTML(title)}

        </div>

        <div
            style="
                position:relative;
                height:280px;
                width:100%;
                margin-top:10px;
            "
        >

            <canvas id="${id}"></canvas>

        </div>

    `;

    chatBox.appendChild(wrapper);

    scrollChat();
}


// ============================================================
// TIPS
// ============================================================

function updateTips(data) {

    const list = document.getElementById("tipsList");

    if (!list) return;

    list.innerHTML = "";

    let tips = data.tips || [];

    if (!Array.isArray(tips)) {
        tips = [tips];
    }

    if (!tips.length) {

        list.innerHTML =
            "<li>No tips available.</li>";

        return;
    }

    tips.forEach(function (tip) {

        const li = document.createElement("li");

        li.textContent = tip;

        list.appendChild(li);

    });
}


// ============================================================
// ALERTS
// ============================================================

function updateAlerts(data) {

    const list = document.getElementById("alertList");

    if (!list) return;

    list.innerHTML = "";

    let alerts = data.alerts || [];

    if (!Array.isArray(alerts)) {
        alerts = [alerts];
    }

    if (!alerts.length) {

        list.innerHTML =
            "<li>✅ No financial alerts.</li>";

        return;
    }

    alerts.forEach(function (alert) {

        const li = document.createElement("li");

        li.textContent = alert;

        list.appendChild(li);

    });
}


// ============================================================
// QUICK QUESTIONS
// ============================================================

function askSuggestion(question) {

    const input = document.getElementById("question");

    if (!input) return;

    input.value = question;

    sendMessage();
}


// ============================================================
// VOICE INPUT
// ============================================================

function startVoice() {

    const SpeechRecognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;

    if (!SpeechRecognition) {

        alert(
            "Voice recognition is not supported in this browser."
        );

        return;
    }

    const recognition = new SpeechRecognition();

    recognition.lang = "en-IN";

    recognition.interimResults = false;

    recognition.maxAlternatives = 1;

    const status =
        document.getElementById("voiceStatus");

    if (status) {
        status.innerText =
            "🎤 Listening...";
    }

    recognition.start();

    recognition.onresult = function (event) {

        const text =
            event.results[0][0].transcript;

        const input =
            document.getElementById("question");

        if (input) {

            input.value = text;

            sendMessage();

        }

        if (status) {

            status.innerText =
                "Voice question received.";

        }
    };

    recognition.onerror = function () {

        if (status) {

            status.innerText =
                "Voice recognition failed.";

        }

    };
}


// ============================================================
// SCROLL CHAT
// ============================================================

function scrollChat() {

    const chatBox =
        document.getElementById("chatBox");

    if (!chatBox) return;

    setTimeout(function () {

        chatBox.scrollTop =
            chatBox.scrollHeight;

    }, 100);
}


// ============================================================
// MONEY FORMAT
// ============================================================

function money(value) {

    const number =
        Number(value || 0);

    return "₹" +
        number.toLocaleString("en-IN", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
}


// ============================================================
// SET TEXT SAFELY
// ============================================================

function setText(id, value) {

    const element =
        document.getElementById(id);

    if (element) {

        element.innerText = value;

    }
}


// ============================================================
// HTML ESCAPE
// ============================================================

function escapeHTML(text) {

    const div =
        document.createElement("div");

    div.textContent = text;

    return div.innerHTML;
}
// ==========================================================
// JARVIS FINANCIAL OVERVIEW CHART
// ==========================================================

let financeChart = null;


function loadFinancialOverview() {

    fetch("/jarvis_financial_overview")

        .then(response => {

            if (!response.ok) {
                throw new Error(
                    "Financial overview request failed"
                );
            }

            return response.json();

        })

        .then(data => {

            // ----------------------------------------------
            // UPDATE SUMMARY CARDS
            // ----------------------------------------------

            const incomeCard =
                document.getElementById("incomeCard");

            const expenseCard =
                document.getElementById("expenseCard");

            const savingCard =
                document.getElementById("savingCard");

            const healthCard =
                document.getElementById("healthCard");

            const investmentCard =
                document.getElementById("investmentCard");

            const currentValueCard =
                document.getElementById("currentValueCard");

            const roiCard =
                document.getElementById("roiCard");

            const budgetCard =
                document.getElementById("budgetCard");


            if (incomeCard) {

                incomeCard.innerText =
                    "₹" +
                    Number(data.income)
                        .toLocaleString("en-IN");

            }


            if (expenseCard) {

                expenseCard.innerText =
                    "₹" +
                    Number(data.expense)
                        .toLocaleString("en-IN");

            }


            if (savingCard) {

                savingCard.innerText =
                    "₹" +
                    Number(data.savings)
                        .toLocaleString("en-IN");

            }


            if (healthCard) {

                healthCard.innerText =
                    data.health_score + "/100";

            }


            if (investmentCard) {

                investmentCard.innerText =
                    "₹" +
                    Number(data.investment)
                        .toLocaleString("en-IN");

            }


            if (currentValueCard) {

                currentValueCard.innerText =
                    "₹" +
                    Number(data.current_value)
                        .toLocaleString("en-IN");

            }


            if (roiCard) {

                roiCard.innerText =
                    Number(data.roi).toFixed(2) + "%";

            }


            if (budgetCard) {

                budgetCard.innerText =
                    "₹" +
                    Number(data.income * 0.50)
                        .toLocaleString("en-IN");

            }


            // ----------------------------------------------
            // FINANCIAL OVERVIEW CHART
            // ----------------------------------------------

            const canvas =
                document.getElementById("financeChart");


            if (!canvas) {

                console.error(
                    "financeChart canvas not found"
                );

                return;

            }


            const ctx =
                canvas.getContext("2d");


            // Destroy old chart if it exists

            if (financeChart) {

                financeChart.destroy();

            }


            financeChart = new Chart(ctx, {

                type: "bar",

                data: {

                    labels: [

                        "Income",

                        "Expense",

                        "Savings"

                    ],

                    datasets: [

                        {

                            label:
                                "Financial Overview",

                            data: [

                                Number(data.income),

                                Number(data.expense),

                                Number(data.savings)

                            ],

                            borderWidth: 1

                        }

                    ]

                },


                options: {

                    responsive: true,

                    maintainAspectRatio: false,


                    scales: {

                        y: {

                            beginAtZero: true,

                            ticks: {

                                callback:
                                    function(value) {

                                        return "₹" +
                                            Number(value)
                                            .toLocaleString(
                                                "en-IN"
                                            );

                                    }

                            }

                        }

                    },


                    plugins: {

                        legend: {

                            display: true

                        },


                        tooltip: {

                            callbacks: {

                                label:
                                    function(context) {

                                        return "₹" +
                                            Number(
                                                context.raw
                                            ).toLocaleString(
                                                "en-IN"
                                            );

                                    }

                            }

                        }

                    }

                }

            });

        })


        .catch(error => {

            console.error(
                "Financial Overview Error:",
                error
            );

        });

}


// ==========================================================
// LOAD WHEN JARVIS PAGE OPENS
// ==========================================================

document.addEventListener(
    "DOMContentLoaded",
    function() {

        loadFinancialOverview();

    }
);