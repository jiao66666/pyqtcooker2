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
            }
            addMessage(`返回信息 : ${data.message}`);  // 将收到的消息保存并显示
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage("抛出异常");
        });
}


function disconnect() {
       // 获取 select 元素
        var portSelect = document.getElementById("port_select");
        console.log("选中的端口是:", portSelect.value);
        var baudrateSelect = document.getElementById("baud_select");
        console.log("选中的波特率是:", baudrateSelect.value);

        fetch('/disconnect', {
            method: 'POST', 
            headers: {
                'Content-Type': 'application/json'  
            },
            body: JSON.stringify({
                boardtype: '1',  // 五轴板
            })
        })
        .then(response => response.json())
        .then(data => {
            if(data.status === "success"){
                updateConnectStatus("未连接");
            }
            addMessage(`返回信息 : ${data.message}`);  // 将收到的消息保存并显示
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage("Error starting motor.");
        });
}


function startMotor(potnum,directionstr) {
       // 获取 select 元素
        var speed = getSelectedValue("speed");
        console.log("选中速度值是:", speed);
        var motorObj = getMotorInfo(potnum,directionstr);
        if(motorObj == null){
            console.log("获取电机信息失败");
            return;
        }
        fetch('/runlong', {
            method: 'POST', 
            headers: {
                'Content-Type': 'application/json'  
            },
            body: JSON.stringify({
                boardtype: '1',  // 五轴板
                motorid: motorObj.motor,
                direction: motorObj.direction,
                speed: speed
            })
        })
        .then(response => response.json())
        .then(data => {
            if(data.status === "success"){
                addMessage(`返回信息 : ${data.message}`);  // 将收到的消息保存并显示
            }else if(data.status === "error"){
                addMessage(`返回信息 : ${data.message}`);  // 将收到的消息保存并显示
            }
            
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage("Error starting motor.");
        });
}



function runMotor(potnum,directionstr) {

       var speed = getSelectedValue("speed");
        console.log("选中速度值是:", speed);
       // 获取 select 元素
        var circle = document.getElementById("circleval");
        console.log("选中圈数值是:", circle);
        if(circle.value == "" || isNaN(circle.value)){
            alert("请输入有效的绝对位置值！");
            return;
        }
        var motorObj = getMotorInfo(potnum,directionstr);
        if(motorObj == null){
            console.log("获取电机信息失败");
            return;
        }
        fetch('/run', {
            method: 'POST', 
            headers: {
                'Content-Type': 'application/json'  
            },
            body: JSON.stringify({
                boardtype: '1',  // 五轴板
                motorid: motorObj.motor,
                direction: motorObj.direction,
                circle: circle.value,
                speed: speed
            })
        })
        .then(response => response.json())
        .then(data => {
            if(data.status === "success"){
                addMessage(`返回信息 : ${data.message}`);  // 将收到的消息保存并显示
            }else if(data.status === "error"){
                addMessage(`返回信息 : ${data.message}`);  // 将收到的消息保存并显示
            }
            
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage("Error starting motor.");
        });
}


function runMotorabs(potnum,directionstr) {

       var speed = getSelectedValue("speed");
        console.log("选中速度值是:", speed);
       // 获取 select 元素
        var circle = document.getElementById("circlevalabs");
        console.log("选中圈数值是:", circle);

        if(circle.value == "" || isNaN(circle.value)){
            alert("请输入有效的绝对位置值！");
            return;
        }
        var motorObj = getMotorInfo(potnum,directionstr);
        if(motorObj == null){
            console.log("获取电机信息失败");
            return;
        }
        fetch('/runabs', {
            method: 'POST', 
            headers: {
                'Content-Type': 'application/json'  
            },
            body: JSON.stringify({
                boardtype: '1',  // 五轴板
                motorid: motorObj.motor,
                direction: motorObj.direction,
                circle: circle.value,
                speed: speed
            })
        })
        .then(response => response.json())
        .then(data => {
             addMessage(`返回信息 : ${data.message}`);  // 将收到的消息保存并显示
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage("Error starting motor.");
        });
}


function resetMotor(potnum,directionstr) {
       // 获取 select 元素
        var motorObj = getMotorInfo(potnum,directionstr);
        if(motorObj == null){
            console.log("获取电机信息失败");
            return;
        }
        fetch('/resetmotor', {
            method: 'POST', 
            headers: {
                'Content-Type': 'application/json'  
            },
            body: JSON.stringify({
                boardtype: '1',  // 五轴板
                motorid: motorObj.motor,
                direction: motorObj.direction,
            })
        })
        .then(response => response.json())
        .then(data => {
            if(data.status === "success"){
                addMessage(`返回信息 : ${data.message}`);  // 将收到的消息保存并显示
            }else if(data.status === "error"){
                addMessage(`返回信息 : ${data.message}`);  // 将收到的消息保存并显示
            }
            
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage("Error starting motor.");
        });
}
// 停止电机
function pauseMotor(potnum,directionstr) {
     // 获取 select 元素

        var motorObj = getMotorInfo(potnum,directionstr);
        if(motorObj == null){
            console.log("获取电机信息失败");
            return;
        }
        fetch('/pause', {
            method: 'POST', 
            headers: {
                'Content-Type': 'application/json'  
            },
            body: JSON.stringify({
                boardtype: '1',  // 五轴板
                motorid: motorObj.motor
            })
        })
        .then(response => response.json())
        .then(data => {
            if(data.status === "success"){
                addMessage(`返回信息 : ${data.message}`);  // 将收到的消息保存并显示
            }
            
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage("Error starting motor.");
        });
}

function stopMotor(potnum,directionstr) {
     // 获取 select 元素

        var motorObj = getMotorInfo(potnum,directionstr);
        if(motorObj == null){
            console.log("获取电机信息失败");
            return;
        }
        fetch('/stop', {
            method: 'POST', 
            headers: {
                'Content-Type': 'application/json'  
            },
            body: JSON.stringify({
                boardtype: '1',  // 五轴板
                motorid: motorObj.motor
            })
        })
        .then(response => response.json())
        .then(data => {
            if(data.status === "success"){
                addMessage(`返回信息 : ${data.message}`);  // 将收到的消息保存并显示
            }
            
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage("Error starting motor.");
        });
}


function readMotor(potnum,directionstr) {
     // 获取 select 元素

        var motorObj = getMotorInfo(potnum,directionstr);
        if(motorObj == null){
            console.log("获取电机信息失败");
            return;
        }
        fetch('/readmotor', {
            method: 'POST', 
            headers: {
                'Content-Type': 'application/json'  
            },
            body: JSON.stringify({
                boardtype: '1',  // 五轴板
                motorid: motorObj.motor
            })
        })
        .then(response => response.json())
        .then(data => {
            if(data.status === "success"){
                addMessage(`返回信息 : ${data.message}`);  // 将收到的消息保存并显示
            }
            
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage("Error starting motor.");
        });
}


function testTask(potnum,directionstr) {
     // 获取 select 元素

        var motorObj = getMotorInfo(potnum,directionstr);
        if(motorObj == null){
            console.log("获取电机信息失败");
            return;
        }
        fetch('/testtaskabs', {
            method: 'POST', 
            headers: {
                'Content-Type': 'application/json'  
            },
            body: JSON.stringify({
                boardtype: '1',  // 五轴板
                motorid: motorObj.motor
            })
        })
        .then(response => response.json())
        .then(data => {
            if(data.status === "success"){
                addMessage(`返回信息 : ${data.message}`);  // 将收到的消息保存并显示
            }
            
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage("Error starting motor.");
        });
}


function testTaskabs(potnum,directionstr) {
     // 获取 select 元素

        var motorObj = getMotorInfo(potnum,directionstr);
        if(motorObj == null){
            console.log("获取电机信息失败");
            return;
        }
        fetch('/testtaskabs', {
            method: 'POST', 
            headers: {
                'Content-Type': 'application/json'  
            },
            body: JSON.stringify({
                boardtype: '1',  // 五轴板
                motorid: motorObj.motor
            })
        })
        .then(response => response.json())
        .then(data => {
            if(data.status === "success"){
                addMessage(`返回信息 : ${data.message}`);  // 将收到的消息保存并显示
            }
            
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage("Error starting motor.");
        });
}


function removeLimit(potnum,directionstr) {
     // 获取 select 元素

        var motorObj = getMotorInfo(potnum,directionstr);
        if(motorObj == null){
            console.log("获取电机信息失败");
            return;
        }
        fetch('/removelimit', {
            method: 'POST', 
            headers: {
                'Content-Type': 'application/json'  
            },
            body: JSON.stringify({
                boardtype: '1',  // 五轴板
                motorid: motorObj.motor
            })
        })
        .then(response => response.json())
        .then(data => {
            if(data.status === "success"){
                addMessage(`返回信息 : ${data.message}`);  // 将收到的消息保存并显示
            }
            
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage("Error starting motor.");
        });
}


function recoveryLimit(potnum,directionstr) {
     // 获取 select 元素

        var motorObj = getMotorInfo(potnum,directionstr);
        if(motorObj == null){
            console.log("获取电机信息失败");
            return;
        }
        fetch('/recoverylimit', {
            method: 'POST', 
            headers: {
                'Content-Type': 'application/json'  
            },
            body: JSON.stringify({
                boardtype: '1',  // 五轴板
                motorid: motorObj.motor
            })
        })
        .then(response => response.json())
        .then(data => {
            if(data.status === "success"){
                addMessage(`返回信息 : ${data.message}`);  // 将收到的消息保存并显示
            }
            
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage("Error starting motor.");
        });
}

function test() {
     // 获取 select 元素
        fetch('/test', {
            method: 'POST', 
            headers: {
                'Content-Type': 'application/json'  
            },
            body: JSON.stringify({
                boardtype: '1',  // 五轴板
            })
        })
        .then(response => response.json())
        .then(data => {
              addMessage(`返回信息 : 已发送串口指令`);  // 将收到的消息保存并显示
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage("Error starting motor.");
        });
}

function fixmotor() {
     // 获取 select 元素
        fetch('/fixmotor', {
            method: 'POST', 
            headers: {
                'Content-Type': 'application/json'  
            },
            body: JSON.stringify({
                boardtype: '1',  // 五轴板
            })
        })
        .then(response => response.json())
        .then(data => {
              addMessage(`返回信息 : 已发送串口指令`);  // 将收到的消息保存并显示
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage("Error starting motor.");
        });
}



function stopall() {
     // 获取 select 元素
        fetch('/stopall', {
            method: 'POST', 
            headers: {
                'Content-Type': 'application/json'  
            },
            body: JSON.stringify({
                boardtype: '1',  // 五轴板
            })
        })
        .then(response => response.json())
        .then(data => {
              addMessage(`返回信息 : 已发送串口指令`);  // 将收到的消息保存并显示
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage("Error starting motor.");
        });
}



function testMultiTask() {
     // 获取 select 元素
        fetch('/testmultitask', {
            method: 'POST', 
            headers: {
                'Content-Type': 'application/json'  
            },
            body: JSON.stringify({
                boardtype: '1',  // 五轴板
            })
        })
        .then(response => response.json())
        .then(data => {
              addMessage(`返回信息 : 已发送串口指令`);  // 将收到的消息保存并显示
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage("Error starting motor.");
        });
}

function testMultiTaskabs() {
     // 获取 select 元素
        fetch('/testmultitaskabs', {
            method: 'POST', 
            headers: {
                'Content-Type': 'application/json'  
            },
            body: JSON.stringify({
                boardtype: '1',  // 五轴板
            })
        })
        .then(response => response.json())
        .then(data => {
              addMessage(`返回信息 : `+data.message);  // 将收到的消息保存并显示
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage("Error starting motor.");
        });
}


function testMultiTaskabs2() {
     // 获取 select 元素
        fetch('/testmultitaskabs2', {
            method: 'POST', 
            headers: {
                'Content-Type': 'application/json'  
            },
            body: JSON.stringify({
                boardtype: '1',  // 五轴板
            })
        })
        .then(response => response.json())
        .then(data => {
              addMessage(`返回信息 : `+data.message);  // 将收到的消息保存并显示
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage("Error starting motor.");
        });
}

function enableall() {
     // 获取 select 元素
        fetch('/enableall', {
            method: 'POST', 
            headers: {
                'Content-Type': 'application/json'  
            },
            body: JSON.stringify({
                boardtype: '1',  // 五轴板
            })
        })
        .then(response => response.json())
        .then(data => {
              addMessage(`返回信息 : 已发送串口指令`);  // 将收到的消息保存并显示
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage("Error starting motor.");
        });
}



function getSelectedValue(name) {
    const radios = document.getElementsByName(name);
    for (let i = 0; i < radios.length; i++) {
        if (radios[i].checked) {
            console.log("选择的速度档位是:"+radios[i].value);
            return radios[i].value;
        }
    }
    alert("没有选择速度！");
    return null;
}

//转换为具体电机和方向
function getMotorInfo(potnum, directionstr){
     if(potnum == 1){
        if(directionstr == "up"){
            return { motor: 1, direction: 1 };
        }else if(directionstr == "down"){
            return { motor: 1, direction: -1 };
        }else if(directionstr == "left"){
            return { motor: 2, direction: 1 };
        }else if(directionstr == "right"){
            return { motor: 2, direction: -1 };
        }
    }else if(potnum == 2){
        if(directionstr == "up"){
            return { motor: 3, direction: -1 };
        }else if(directionstr == "down"){
            return { motor: 3, direction: 1 };
        }else if(directionstr == "left"){
            return { motor: 4, direction: 1 };
        }else if(directionstr == "right"){
            return { motor: 4, direction: -1 };
        }
    }
    return null
}


function showTab(tabNumber, buttonElement) {
  // 隐藏所有内容
  document.querySelectorAll('.tab-content').forEach(c => c.style.display = 'none');
  // 移除所有按钮 active 样式
  document.querySelectorAll('.tab-buttons button').forEach(b => b.classList.remove('active'));
  // 显示选中内容
  document.getElementById('tab' + tabNumber).style.display = 'block';
  // 高亮选中按钮
  buttonElement.classList.add('active');
}