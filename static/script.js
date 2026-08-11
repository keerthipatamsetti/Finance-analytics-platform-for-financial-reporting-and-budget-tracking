// ==========================================
// JARVIS AI ASSISTANT
// ==========================================

let financeChart = null;


// ==========================================
// SEND MESSAGE
// ==========================================

function sendMessage() {

    const input = document.getElementById("question");
    const question = input.value.trim();

    if (question === "") {
        return;
    }

    addUserMessage(question);

    input.value = "";

    const loadingId = "loading-" + Date.now();

    addBotMessage(
        "🤖 Jarvis is analysing your financial data...",
        loadingId
    );

    fetch("/jarvis_chat", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            question: question
        })

    })

    .then(response => {

        if (!response.ok) {
            throw new Error("Server error");
        }

        return response.json();

    })

    .then(data => {

        const loadingMessage =
            document.getElementById(loadingId);

        if (loadingMessage) {
            loadingMessage.remove();
        }

        updateDashboardCards(data);

        addJarvisResponse(data, question);

    })

    .catch(error => {

        console.error(error);

        const loadingMessage =
            document.getElementById(loadingId);

        if (loadingMessage) {
            loadingMessage.remove();
        }

        addBotMessage(
            "❌ Unable to connect with Jarvis.<br><br>" +
            "Please make sure the Flask server is running.",
            "error-" + Date.now()
        );

    });

}


// ==========================================
// USER MESSAGE
// ==========================================

function addUserMessage(message) {

    const chatBox =
        document.getElementById("chatBox");

    const div =
        document.createElement("div");

    div.className = "user-message";

    div.innerHTML =
        `<div class="message-content">
            ${escapeHTML(message)}
        </div>`;

    chatBox.appendChild(div);

    scrollChat();

}


// ==========================================
// BOT MESSAGE
// ==========================================

function addBotMessage(message, id = null) {

    const chatBox =
        document.getElementById("chatBox");

    const div =
        document.createElement("div");

    div.className = "bot-message";

    if (id) {
        div.id = id;
    }

    div.innerHTML = message;

    chatBox.appendChild(div);

    scrollChat();

}


// ==========================================
// JARVIS RESPONSE
// ==========================================

function addJarvisResponse(data, question) {

    const chatBox =
        document.getElementById("chatBox");

    const div =
        document.createElement("div");

    div.className = "bot-message jarvis-result";

    let html = "";

    html += `
        <div class="jarvis-title">
            🤖 Jarvis
        </div>
    `;


    // ======================================
    // MAIN ANSWER
    // ======================================

    html += `
        <div class="jarvis-answer">
            ${formatAnswer(data.reply)}
        </div>
    `;


    // ======================================
    // CHART
    // ======================================

    if (shouldShowChart(question)) {

        const chartId =
            "jarvisChart_" + Date.now();

        html += `
            <div class="jarvis-chart-container">
                <h6>📊 Financial Analysis</h6>

                <div style="height:280px;">
                    <canvas id="${chartId}"></canvas>
                </div>
            </div>
        `;

        div.innerHTML = html;

        chatBox.appendChild(div);

        createJarvisChart(
            chartId,
            data,
            question
        );

    } else {

        div.innerHTML = html;

        chatBox.appendChild(div);

    }


    scrollChat();

}


// ==========================================
// CHECK WHETHER CHART IS REQUIRED
// ==========================================

function shouldShowChart(question) {

    question =
        question.toLowerCase();

    const chartWords = [

        "income",
        "expense",
        "expenses",
        "spending",
        "saving",
        "savings",
        "investment",
        "investments",
        "portfolio",
        "roi",
        "summary",
        "dashboard",
        "financial health",
        "health"

    ];

    return chartWords.some(
        word => question.includes(word)
    );

}


// ==========================================
// CREATE CHART
// ==========================================

function createJarvisChart(
    chartId,
    data,
    question
) {

    const canvas =
        document.getElementById(chartId);

    if (!canvas) {
        return;
    }

    const ctx =
        canvas.getContext("2d");


    question =
        question.toLowerCase();


    let labels = [];
    let values = [];


    // ======================================
    // INCOME
    // ======================================

    if (
        question.includes("income") &&
        !question.includes("expense")
    ) {

        labels = ["Income"];

        values = [
            Number(data.total_income || 0)
        ];

    }


    // ======================================
    // EXPENSE
    // ======================================

    else if (
        question.includes("expense") ||
        question.includes("spending")
    ) {

        labels = ["Expense"];

        values = [
            Number(data.total_expense || 0)
        ];

    }


    // ======================================
    // SAVINGS
    // ======================================

    else if (
        question.includes("saving")
    ) {

        labels = ["Savings"];

        values = [
            Number(data.total_savings || 0)
        ];

    }


    // ======================================
    // INVESTMENT
    // ======================================

    else if (
        question.includes("investment") ||
        question.includes("portfolio") ||
        question.includes("roi")
    ) {

        labels = [
            "Investment",
            "Current Value"
        ];

        values = [
            Number(data.total_investment || 0),
            Number(data.current_value || 0)
        ];

    }


    // ======================================
    // HEALTH
    // ======================================

    else if (
        question.includes("health")
    ) {

        labels = [
            "Health Score",
            "Remaining"
        ];

        values = [
            Number(data.health_score || 0),
            100 - Number(data.health_score || 0)
        ];

    }


    // ======================================
    // GENERAL SUMMARY
    // ======================================

    else {

        labels = [
            "Income",
            "Expense",
            "Savings",
            "Investment"
        ];

        values = [

            Number(data.total_income || 0),

            Number(data.total_expense || 0),

            Math.max(
                Number(data.total_savings || 0),
                0
            ),

            Number(data.total_investment || 0)

        ];

    }


    new Chart(ctx, {

        type: "bar",

        data: {

            labels: labels,

            datasets: [{

                label: "Amount (₹)",

                data: values,

                borderWidth: 1,

                borderRadius: 8

            }]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            plugins: {

                legend: {
                    display: true
                }

            },

            scales: {

                y: {

                    beginAtZero: true

                }

            }

        }

    });

}


// ==========================================
// UPDATE TOP CARDS
// ==========================================

function updateDashboardCards(data) {

    const incomeCard =
        document.getElementById("incomeCard");

    const expenseCard =
        document.getElementById("expenseCard");

    const savingCard =
        document.getElementById("savingCard");

    const healthCard =
        document.getElementById("healthCard");

    const roiCard =
        document.getElementById("roiCard");

    const investmentCard =
        document.getElementById("investmentCard");

    const currentValueCard =
        document.getElementById("currentValueCard");


    if (incomeCard) {

        incomeCard.innerText =
            "₹" + Number(
                data.total_income || 0
            ).toLocaleString("en-IN");

    }


    if (expenseCard) {

        expenseCard.innerText =
            "₹" + Number(
                data.total_expense || 0
            ).toLocaleString("en-IN");

    }


    if (savingCard) {

        savingCard.innerText =
            "₹" + Number(
                data.total_savings || 0
            ).toLocaleString("en-IN");

    }


    if (healthCard) {

        healthCard.innerText =
            Number(
                data.health_score || 0
            ) + "/100";

    }


    if (roiCard) {

        roiCard.innerText =
            Number(
                data.roi || 0
            ) + "%";

    }


    if (investmentCard) {

        investmentCard.innerText =
            "₹" + Number(
                data.total_investment || 0
            ).toLocaleString("en-IN");

    }


    if (currentValueCard) {

        currentValueCard.innerText =
            "₹" + Number(
                data.current_value || 0
            ).toLocaleString("en-IN");

    }

}


// ==========================================
// FORMAT ANSWER
// ==========================================

function formatAnswer(text) {

    if (!text) {
        return "No response available.";
    }

    return escapeHTML(text)
        .replace(/\n/g, "<br>")
        .replace(
            /•/g,
            "<br>•"
        );

}


// ==========================================
// SUGGESTION BUTTON
// ==========================================

function askSuggestion(question) {

    document.getElementById(
        "question"
    ).value = question;

    sendMessage();

}


// ==========================================
// ENTER KEY
// ==========================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const input =
            document.getElementById("question");

        if (input) {

            input.addEventListener(
                "keydown",
                function (event) {

                    if (
                        event.key === "Enter"
                    ) {

                        event.preventDefault();

                        sendMessage();

                    }

                }
            );

        }


        loadJarvisData();

    }
);


// ==========================================
// LOAD INITIAL DATA
// ==========================================

function loadJarvisData() {

    fetch("/jarvis_chat", {

        method: "POST",

        headers: {

            "Content-Type":
                "application/json"

        },

        body: JSON.stringify({

            question: "dashboard summary"

        })

    })

    .then(response =>
        response.json()
    )

    .then(data => {

        updateDashboardCards(data);

        updateTips(data);

        updateAlerts(data);

        updateGreeting(data);

    })

    .catch(error => {

        console.error(
            "Jarvis loading error:",
            error
        );

    });

}


// ==========================================
// UPDATE GREETING
// ==========================================

function updateGreeting(data) {

    const greeting =
        document.getElementById("greeting");

    if (greeting && data.greeting) {

        greeting.innerText =
            data.greeting +
            " I am Jarvis 🤖";

    }

}


// ==========================================
// UPDATE TIPS
// ==========================================

function updateTips(data) {

    const list =
        document.getElementById("tipsList");

    if (!list) {
        return;
    }

    list.innerHTML = "";

    if (
        !data.tips ||
        data.tips.length === 0
    ) {

        list.innerHTML =
            "<li>No tips available.</li>";

        return;

    }


    data.tips.forEach(tip => {

        const li =
            document.createElement("li");

        li.innerText = tip;

        list.appendChild(li);

    });

}


// ==========================================
// UPDATE ALERTS
// ==========================================

function updateAlerts(data) {

    const list =
        document.getElementById("alertList");

    if (!list) {
        return;
    }

    list.innerHTML = "";

    if (
        !data.alerts ||
        data.alerts.length === 0
    ) {

        list.innerHTML =
            "<li>✅ No financial alerts.</li>";

        return;

    }


    data.alerts.forEach(alert => {

        const li =
            document.createElement("li");

        li.innerText = alert;

        list.appendChild(li);

    });

}


// ==========================================
// SCROLL CHAT
// ==========================================

function scrollChat() {

    const chatBox =
        document.getElementById("chatBox");

    if (!chatBox) {
        return;
    }

    chatBox.scrollTop =
        chatBox.scrollHeight;

}


// ==========================================
// SECURITY
// ==========================================

function escapeHTML(text) {

    const div =
        document.createElement("div");

    div.innerText = text;

    return div.innerHTML;

}


// ==========================================
// VOICE ASSISTANT
// ==========================================

const mic =
    document.getElementById("mic");

if (mic) {

    mic.addEventListener(
        "click",
        function () {

            const SpeechRecognition =
                window.SpeechRecognition ||
                window.webkitSpeechRecognition;

            if (!SpeechRecognition) {

                alert(
                    "Voice recognition is not supported in this browser."
                );

                return;

            }


            const recognition =
                new SpeechRecognition();

            recognition.lang = "en-IN";

            recognition.interimResults =
                false;

            recognition.maxAlternatives =
                1;


            const status =
                document.getElementById(
                    "voiceStatus"
                );


            if (status) {

                status.innerText =
                    "🎤 Listening...";

            }


            recognition.start();


            recognition.onresult =
                function (event) {

                    const text =
                        event.results[0][0].transcript;

                    document.getElementById(
                        "question"
                    ).value = text;

                    if (status) {

                        status.innerText =
                            "Voice received.";

                    }

                    sendMessage();

                };


            recognition.onerror =
                function () {

                    if (status) {

                        status.innerText =
                            "❌ Voice recognition failed.";

                    }

                };

        }
    );

}