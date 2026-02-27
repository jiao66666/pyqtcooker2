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


function updateConnectStatus(msg, newClass) {
    var statusDiv = document.getElementById('connect_status');
    statusDiv.textContent = msg;  // 更新内容为传入的 msg
    statusDiv.className = newClass;  // 更新 class 为传入的 newClass
}


//连接炒菜机串口
function connect() {
        fetch('/connect', {
            method: 'POST', 
            headers: {
                'Content-Type': 'application/json'  
            },
            body: JSON.stringify({
            })
        })
        .then(response => response.json())
        .then(data => {
            if(data.status === "success"){
                updateConnectStatus("已连接","connect_status_connected");
                startWebSocket();
            }
            addMessage(`返回信息 : ${data.message}`);  // 将收到的消息保存并显示
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage("抛出异常");
        });
}

//断开连接炒菜机串口
function disconnect() {
        fetch('/disconnect', {
            method: 'POST', 
            headers: {
                'Content-Type': 'application/json'  
            },
            body: JSON.stringify({
              
            })
        })
        .then(response => response.json())
        .then(data => {
            if(data.status === "success"){
                updateConnectStatus("未连接","connect_status");
            }
            addMessage(`返回信息 : ${data.message}`);  // 将收到的消息保存并显示
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage("Error starting motor.");
        });
}


function testTastBoardPing() {
        fetch('/testtastboardping', {
            method: 'POST', 
            headers: {
                'Content-Type': 'application/json'  
            },
            body: JSON.stringify({
              
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


function runTastMotor() {
        var tastMotorIDSelect = document.getElementById("tastmotorid");
        if(tastMotorIDSelect.value == "" || isNaN(tastMotorIDSelect.value)){
            addMessage("请选择电机ID");
            return;
        }

        var tastMotorOvertime = document.getElementById("tastmotorovertime");
        if(tastMotorOvertime.value == "" || isNaN(tastMotorOvertime.value)){
            addMessage("请输入超时时间");
            return;
        }

        fetch('/runtastmotor', {
            method: 'POST', 
            headers: {
                'Content-Type': 'application/json'  
            },
            body: JSON.stringify({
                 motorid: tastMotorIDSelect.value,
                 overtime: tastMotorOvertime.value
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


function getTastMotorFb(mode) {
        var tastMotorIDSelect = document.getElementById("tastmotorid");
        if(tastMotorIDSelect.value == "" || isNaN(tastMotorIDSelect.value)){
            addMessage("请选择电机ID");
            return;
        }

        fetch('/gettastmotorfb', {
            method: 'POST', 
            headers: {
                'Content-Type': 'application/json'  
            },
            body: JSON.stringify({
                 motorid: tastMotorIDSelect.value,
                 mode: mode
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
             addMessage(`返回信息 : ${data.message}`);  // 将收到的消息保存并显示
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

function resetMotorPot(potnum) {
     // 获取 select 元素
        fetch('/resetmotorpot', {
            method: 'POST', 
            headers: {
                'Content-Type': 'application/json'  
            },
            body: JSON.stringify({
                potnum: potnum,      
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
              addMessage(`返回信息 : ${data.message}`);  // 将收到的消息保存并显示
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
      var speed_level = document.getElementById("speed_level");
        if(speed_level.value == "" || isNaN(speed_level.value) || parseInt(speed_level.value) <= 0){
            alert("请输入有效的水平移动速度值！");
            return;
        }

       var speed_flip = document.getElementById("speed_flip");
        if(speed_flip.value == "" || isNaN(speed_flip.value) || parseInt(speed_flip.value) <= 0){
            alert("请输入有效的翻转移动速度值！");
            return;
        }

      console.log("选中水平移动速度值是:", speed_level.value);
      console.log("选中翻转移动速度值是:", speed_flip.value);

     // 获取 select 元素
        fetch('/testmultitaskabs', {
            method: 'POST', 
            headers: {
                'Content-Type': 'application/json'  
            },
            body: JSON.stringify({
                 speed_level: speed_level.value,  
                 speed_flip: speed_flip.value,  
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

function goPos(potnum,postype) {
        var speed = getSelectedValue("speed");
        console.log("选中速度值是:", speed);
     // 获取 select 元素
        fetch('/gopos', {
            method: 'POST', 
            headers: {
                'Content-Type': 'application/json'  
            },
            body: JSON.stringify({
               potnum: potnum,
               postype: postype,
               speed: speed
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


function readPulse(mode) {
        var motorid = document.getElementById("tastmotorid");

     // 获取 select 元素
        fetch('/readpulse', {
            method: 'POST', 
            headers: {
                'Content-Type': 'application/json'  
            },
            body: JSON.stringify({
               mode: mode,
               motorid: motorid.value
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


function testMultiAxis() {
     var speed_level = document.getElementById("speed_level");
        if(speed_level.value == "" || isNaN(speed_level.value) || parseInt(speed_level.value) <= 0){
            alert("请输入有效的水平移动速度值！");
            return;
        }

       var speed_flip = document.getElementById("speed_flip");
        if(speed_flip.value == "" || isNaN(speed_flip.value) || parseInt(speed_flip.value) <= 0){
            alert("请输入有效的翻转移动速度值！");
            return;
        }

      console.log("选中水平移动速度值是:", speed_level.value);
      console.log("选中翻转移动速度值是:", speed_flip.value);


        var exitpos = document.getElementById("exitposabs");
        console.log("退出数值是:", exitpos.value);

        if(exitpos.value == "" || isNaN(exitpos.value)){
            alert("请输入有效的退出位置值！");
            return;
        }


     // 获取 select 元素
        fetch('/testmultiaxis', {
            method: 'POST', 
            headers: {
                'Content-Type': 'application/json'  
            },
            body: JSON.stringify({
                speed_level: speed_level.value,  
                speed_flip: speed_flip.value,  
                exit_pos:exitpos.value
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


function testMultiAxis2() {
     var speed_level = document.getElementById("speed_level");
        if(speed_level.value == "" || isNaN(speed_level.value) || parseInt(speed_level.value) <= 0){
            alert("请输入有效的水平移动速度值！");
            return;
        }

       var speed_flip = document.getElementById("speed_flip");
        if(speed_flip.value == "" || isNaN(speed_flip.value) || parseInt(speed_flip.value) <= 0){
            alert("请输入有效的翻转移动速度值！");
            return;
        }

      console.log("选中水平移动速度值是:", speed_level.value);
      console.log("选中翻转移动速度值是:", speed_flip.value);

        var exitpos = document.getElementById("exitposabs");
        console.log("退出值是:", exitpos.value);

        if(exitpos.value == "" || isNaN(exitpos.value)){
            alert("请输入有效的退出位置值！");
            return;
        }



     // 获取 select 元素
        fetch('/testmultiaxis2', {
            method: 'POST', 
            headers: {
                'Content-Type': 'application/json'  
            },
            body: JSON.stringify({
                speed_level: speed_level.value,  
                speed_flip: speed_flip.value,  
                exit_pos:exitpos.value
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




function testVarSpeedSingle() {
     var speed_target = document.getElementById("varspeed_target");
        if(speed_target.value == "" || isNaN(speed_target.value) || parseInt(speed_target.value) <= 0){
            alert("请输入有效的变速运动目标值！");
            return;
        }

        var speed_params = document.getElementById("varspeed_params");

        // 检查字符串是否为空
        if (!speed_params.value.trim()) {
            console.log("输入不能为空");
            return;
        } else {
            // 正则表达式：匹配 [(数字,数字), (数字,数字), ...]
            var regex = /^\[\((\d+(\.\d+)?),(\d+)\)(,\((\d+(\.\d+)?),(\d+)\))*\]$/;
            // 使用正则表达式测试字符串
            if (regex.test(speed_params.value)) {
                console.log("参数串格式正确");
            } else {
                console.log("格式不正确");
                return;
            }
        }

       
      console.log("变速运动目标值是:", speed_target.value);
      console.log("变速运动参数值是:", speed_params.value);

     // 获取 select 元素
        fetch('/testvarspeedsingle', {
            method: 'POST', 
            headers: {
                'Content-Type': 'application/json'  
            },
            body: JSON.stringify({
                speed_target: speed_target.value,  
                speed_params: speed_params.value
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



function createMotorStatusApp(el) {
  return new Vue({
    el: el,
    delimiters: ['${', '}'],
    template: '#motor-status-template',
    data: {
      motor1_flip: 0.0,
      motor1_level: 0.0,
      motor2_flip: 0.0,
      motor2_level: 0.0
    },
    methods: {
      updateMotorData(motor_id, position) {
        if (motor_id == 1) {
          this.motor1_flip = position;
        } else if (motor_id == 2) {
          this.motor1_level = position;
        } else if (motor_id == 3) {
          this.motor2_flip = position;
        } else if (motor_id == 4) {
          this.motor2_level = position;
        }
      }
    }
  });
}

// 创建两个实例（变量互不影响）
const app1 = createMotorStatusApp('#motor_status_1');
const app2 = createMotorStatusApp('#motor_status_2');
const app3 = createMotorStatusApp('#motor_status_3');


// 将 WebSocket 实例提升到全局作用域
let ws;

// WebSocket 初始化方法
function setupWebSocket(url) {
    ws = new WebSocket(url);  // 创建 WebSocket 连接

    // 连接打开时的回调
    ws.onopen = () => {
        console.log('Connected to WebSocket server');
    };


    ws.onmessage = (event) => {
        const arr = JSON.parse(event.data); // [{motor_id, position}, ...]
        for (const item of arr) {
            app1.updateMotorData(item.motor_id, item.position);
            app2.updateMotorData(item.motor_id, item.position);
            app3.updateMotorData(item.motor_id, item.position);
        }
    };

    // 处理错误的回调
    ws.onerror = (error) => {
        console.error('WebSocket Error: ', error);
    };

    // 连接关闭时的回调
    ws.onclose = () => {
        console.log('WebSocket connection closed');
    };
}



// 点击按钮启动 WebSocket 连接
function startWebSocket() {
    if (!ws || ws.readyState === WebSocket.CLOSED) {
        setupWebSocket('ws://192.168.31.188:8765');  // 如果 WebSocket 没有连接，才启动连接
        console.log('WebSocket connection established');
    } else {
        console.log('WebSocket is already connected.');
    }
}