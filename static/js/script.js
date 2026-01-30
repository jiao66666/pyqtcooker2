// 保存历史消息的数组
let messageHistory = [];

// 显示历史消息的函数
function displayMessageHistory() {
    const historyContainer = document.getElementById("status-history");
    historyContainer.innerHTML = "";  // 清空历史消息区域

    // 倒序显示消息：最新的消息在最上面
    messageHistory.forEach(msg => {
        const msgDiv = document.createElement("div");
        msgDiv.classList.add("message");

        const timestampDiv = document.createElement("div");
        timestampDiv.classList.add("timestamp");
        timestampDiv.textContent = msg.timestamp;

        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message-text");
        messageDiv.textContent = msg.message;

        msgDiv.appendChild(timestampDiv);
        msgDiv.appendChild(messageDiv);
        historyContainer.appendChild(msgDiv);
    });

    // 确保滚动条始终位于顶部
    historyContainer.scrollTop = 0;
}

// 记录收到的消息并显示
function addMessage(message) {
    const timestamp = new Date().toLocaleString();  // 获取当前时间戳
    messageHistory.unshift({ message, timestamp });  // 将新消息插入到历史记录的头部
    displayMessageHistory();  // 更新页面上显示的消息
}


function updateConnectStatus(msg) {
    var statusDiv = document.querySelector('.connect_status');
    statusDiv.textContent = msg;  // 更新内容为“已连接”
}
// 启动电机
function connect() {
       // 获取 select 元素
        var portSelect = document.getElementById("port_select");
        console.log("选中的端口是:", portSelect.value);
        var baudrateSelect = document.getElementById("baud_select");
        console.log("选中的波特率是:", baudrateSelect.value);

        fetch('/connect', {
            method: 'POST', 
            headers: {
                'Content-Type': 'application/json'  
            },
            body: JSON.stringify({
                boardtype: '1',  // 五轴板
                port: portSelect.value,  
                baudrate: baudrateSelect.value 
            })
        })
        .then(response => response.json())
        .then(data => {
            if(data.status === "success"){
                updateConnectStatus("已连接");
            } else{
                updateConnectStatus("连接失败");
            }
            addMessage(`返回信息 : ${data.message}`);  // 将收到的消息保存并显示
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage("Error starting motor.");
        });
}

// 停止电机
function stopMotor() {
    fetch('/stop_motor')
        .then(response => response.json())
        .then(data => {
            addMessage(`Motor stopped: ${data.message}`);  // 将收到的消息保存并显示
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage("Error stopping motor.");
        });
}
