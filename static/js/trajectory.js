class TrajectoryViewer {

    constructor(canvasId){

        this.canvas = document.getElementById(canvasId);

        this.canvas.width = this.canvas.clientWidth;
        this.canvas.height = this.canvas.clientWidth;

        this.ctx = this.canvas.getContext("2d");

        this.colors = [
            "red",
            "blue",
            "green",
            "purple",
            "orange",
            "cyan",
            "magenta"
        ];

        this.scale = this.getDynamicScale();

        this.offsetY = this.canvas.height / 2;

        // 两锅初始点距离（坐标单位）
        this.potDistance = 9.2;

        this.pots = {

            1: {
                centerX: 0,

                // 是否已经收到过真实轨迹点
                initialized: false,

                // 当前已经完成的最后一个真实点
                lastPoint: null,

                colorIndex: 0,

                color: "#0066ff",

                // 已经完成的轨迹线
                lines: [],

                // 收到的真实坐标点
                points: [],

                // 当前动画中的点
                movingPoint: null,

                animating: false,

                // 等待播放的动画
                queue: [],

                // 当前动画目标点
                currentTarget: null,

                // 动画版本
                animationVersion: 0
            },

            2: {
                centerX: 0,

                // 是否已经收到过真实轨迹点
                initialized: false,

                // 当前已经完成的最后一个真实点
                lastPoint: null,

                colorIndex: 0,

                color: "#008200",

                // 已经完成的轨迹线
                lines: [],

                // 收到的真实坐标点
                points: [],

                // 当前动画中的点
                movingPoint: null,

                animating: false,

                // 等待播放的动画
                queue: [],

                // 当前动画目标点
                currentTarget: null,

                // 动画版本
                animationVersion: 0
            }

        };

        // 根据距离计算两个锅的中心
        this.updatePotCenters();

    }


    //----------------------------------------
    // 坐标转换
    //----------------------------------------

    transform(potId, x, y){

        const pot = this.pots[potId];

        return {

            x: pot.centerX + x * this.scale,

            y: this.offsetY - y * this.scale

        };

    }


    //----------------------------------------
    // 对外接口
    //----------------------------------------

    addPoint1(x, y){

        this.addPoint(1, x, y);

    }


    addPoint2(x, y){

        this.addPoint(2, x, y);

    }


    //----------------------------------------
    // 通用添加点
    //----------------------------------------

    addPoint(potId, x, y){

        const pot = this.pots[potId];

        if(!pot){
            return;
        }


        //----------------------------------------
        // 当前真实坐标转换成 Canvas 坐标
        //----------------------------------------

        const p = this.transform(
            potId,
            x,
            y
        );


        //----------------------------------------
        // 第一次收到数据
        //
        // 注意：
        // 这里不再人为添加 (0,0)
        //
        // 第一个点是什么，就直接从什么点开始
        //----------------------------------------

        if(!pot.initialized){

            pot.initialized = true;

            pot.lastPoint = p;

            pot.points.push({

                x: x,
                y: y,

                px: p.x,
                py: p.y

            });

            // 第一个点只是确定当前真实位置
            // 不产生任何轨迹线
            this.redraw();

            return;
        }


        //----------------------------------------
        // 保存真实坐标点
        //----------------------------------------

        pot.points.push({

            x: x,
            y: y,

            px: p.x,
            py: p.y

        });


        //----------------------------------------
        // 确定动画起点
        //----------------------------------------

        let start;


        if(pot.queue.length > 0){

            // 如果已经有等待中的动画，
            // 从最后一个等待任务的终点继续
            start = pot.queue[pot.queue.length - 1].end;

        }
        else if(pot.animating){

            // 当前正在播放动画，
            // 从当前动画的目标点继续
            start = pot.currentTarget;

        }
        else{

            // 当前没有动画，
            // 从上一次真实位置继续
            start = pot.lastPoint;

        }


        //----------------------------------------
        // 当前真实点作为动画终点
        //----------------------------------------

        const end = p;


        //----------------------------------------
        // 加入动画队列
        //----------------------------------------

        pot.queue.push({

            start: start,

            end: end

        });


        //----------------------------------------
        // 如果当前没有动画，则立即开始
        //----------------------------------------

        if(!pot.animating){

            this.startNextAnimation(pot);

        }

    }


    //----------------------------------------
    // 播放下一段动画
    //----------------------------------------

    startNextAnimation(pot){

        if(pot.queue.length === 0){

            pot.animating = false;

            pot.currentTarget = null;

            return;

        }


        pot.animating = true;


        const task = pot.queue.shift();


        pot.currentTarget = task.end;


        this.animateMove(

            pot,

            task.start,

            task.end

        );

    }


    //----------------------------------------
    // 重绘
    //----------------------------------------

    redraw(){

        const ctx = this.ctx;


        //----------------------------------------
        // 清空 Canvas
        //----------------------------------------

        ctx.clearRect(

            0,

            0,

            this.canvas.width,

            this.canvas.height

        );


        ctx.font = "14px Arial";

        ctx.textAlign = "center";


        //----------------------------------------
        // 绘制两个中心十字
        //----------------------------------------

        for(let id in this.pots){

            const pot = this.pots[id];


            ctx.strokeStyle = "#CCCCCC";

            ctx.lineWidth = 1;


            // 横线
            ctx.beginPath();

            ctx.moveTo(

                pot.centerX - 15,

                this.offsetY

            );

            ctx.lineTo(

                pot.centerX + 15,

                this.offsetY

            );

            ctx.stroke();


            // 竖线
            ctx.beginPath();

            ctx.moveTo(

                pot.centerX,

                this.offsetY - 15

            );

            ctx.lineTo(

                pot.centerX,

                this.offsetY + 15

            );

            ctx.stroke();


            // 锅名称
            ctx.fillStyle = "black";

            ctx.fillText(

                "锅" + id,

                this.getPotLabelX(Number(id)),

                20

            );

        }


        //----------------------------------------
        // 绘制历史轨迹
        //----------------------------------------

        for(let id in this.pots){

            const pot = this.pots[id];


            for(let line of pot.lines){

                ctx.beginPath();


                ctx.moveTo(

                    line.x1,

                    line.y1

                );


                ctx.lineTo(

                    line.x2,

                    line.y2

                );


                ctx.strokeStyle = line.color;

                ctx.lineWidth = 3;

                ctx.stroke();

            }

        }


        //----------------------------------------
        // 绘制坐标点
        //----------------------------------------

        ctx.textAlign = "left";


        for(let id in this.pots){

            const pot = this.pots[id];


            for(let point of pot.points){

                ctx.beginPath();


                ctx.arc(

                    point.px,

                    point.py,

                    4,

                    0,

                    Math.PI * 2

                );


                ctx.fillStyle = "black";

                ctx.fill();


                //----------------------------------------
                // 坐标文字
                //----------------------------------------

                ctx.fillStyle = "black";

                ctx.fillText(

                    "(" +

                    point.x +

                    "," +

                    point.y +

                    ")",

                    point.px + 8,

                    point.py - 8

                );

            }

        }


        //----------------------------------------
        // 当前运动点
        //----------------------------------------

        for(let id in this.pots){

            const pot = this.pots[id];


            if(pot.lastPoint){

                const drawPoint =

                    pot.movingPoint ||

                    pot.lastPoint;


                if(drawPoint){

                    ctx.beginPath();


                    ctx.arc(

                        drawPoint.x,

                        drawPoint.y,

                        6,

                        0,

                        Math.PI * 2

                    );


                    ctx.fillStyle = "red";

                    ctx.fill();

                }

            }

        }

    }


    //----------------------------------------
    // 动画
    //----------------------------------------

    animateMove(pot, start, end){

        //----------------------------------------
        // 当前动画编号
        //----------------------------------------

        pot.animationVersion++;

        const version = pot.animationVersion;


        let progress = 0;


        const step = () => {


            //----------------------------------------
            // 如果动画已经被取消
            //----------------------------------------

            if(version !== pot.animationVersion){

                return;

            }


            progress += 0.05;


            //----------------------------------------
            // 动画结束
            //----------------------------------------

            if(progress >= 1){

                pot.movingPoint = null;


                //----------------------------------------
                // 保存已经完成的轨迹
                //----------------------------------------

                pot.lines.push({

                    x1: start.x,

                    y1: start.y,

                    x2: end.x,

                    y2: end.y,

                    color: pot.color

                });


                //----------------------------------------
                // 更新当前真实位置
                //----------------------------------------

                pot.lastPoint = end;


                pot.currentTarget = null;


                this.redraw();


                //----------------------------------------
                // 继续播放下一段
                //----------------------------------------

                this.startNextAnimation(pot);


                return;

            }


            //----------------------------------------
            // 动画中的点
            //----------------------------------------

            pot.movingPoint = {

                x:

                    start.x +

                    (end.x - start.x) *

                    progress,


                y:

                    start.y +

                    (end.y - start.y) *

                    progress

            };


            this.redraw();


            requestAnimationFrame(step);

        };


        requestAnimationFrame(step);

    }


    //----------------------------------------
    // 自适应尺寸
    //----------------------------------------

    resize(){

        this.canvas.width = this.canvas.clientWidth;

        this.canvas.height = this.canvas.clientWidth;


        //----------------------------------------
        // 重新计算缩放比例
        //----------------------------------------

        this.scale = this.getDynamicScale();


        //----------------------------------------
        // 重新计算 Y 轴中心
        //----------------------------------------

        this.offsetY = this.canvas.height / 2;


        //----------------------------------------
        // 重新计算两个锅的位置
        //----------------------------------------

        this.updatePotCenters();


        //----------------------------------------
        // 重新计算历史轨迹显示坐标
        //----------------------------------------

        this.recalculateTrajectory();


        //----------------------------------------
        // 重绘
        //----------------------------------------

        this.redraw();

    }


    //----------------------------------------
    // 根据当前 scale 重新计算轨迹
    //----------------------------------------

    recalculateTrajectory(){

        for(let id in this.pots){

            const pot = this.pots[id];


            //----------------------------------------
            // 重新计算 points
            //----------------------------------------

            for(let point of pot.points){

                const p = this.transform(

                    Number(id),

                    point.x,

                    point.y

                );


                point.px = p.x;

                point.py = p.y;

            }


            //----------------------------------------
            // 重新计算 lines
            //
            // lines 本身保存的是逻辑坐标还是
            // Canvas 坐标？
            //
            // 当前版本保存的是 Canvas 坐标，
            // 所以这里根据原来的 Canvas 坐标
            // 无法可靠恢复逻辑坐标。
            //
            // 因此下面使用 points 重新生成轨迹。
            //----------------------------------------

            pot.lines = [];


            for(let i = 1; i < pot.points.length; i++){

                const p1 = pot.points[i - 1];

                const p2 = pot.points[i];


                pot.lines.push({

                    x1: p1.px,

                    y1: p1.py,

                    x2: p2.px,

                    y2: p2.py,

                    color: pot.color

                });

            }

        }

    }


    //----------------------------------------
    // 动态缩放
    //----------------------------------------

    getDynamicScale(){

        const zoom = 1.5;

        return (

            this.canvas.height *

            0.8 /

            50 *

            zoom

        );

    }


    //----------------------------------------
    // 清空轨迹
    //----------------------------------------

    clear(){

        for(let id in this.pots){

            const pot = this.pots[id];


            //----------------------------------------
            // 清除历史轨迹
            //----------------------------------------

            pot.lines = [];


            //----------------------------------------
            // 清除坐标点
            //----------------------------------------

            pot.points = [];


            //----------------------------------------
            // 终止当前动画
            //----------------------------------------

            pot.animationVersion++;


            //----------------------------------------
            // 清空等待队列
            //----------------------------------------

            pot.queue = [];


            //----------------------------------------
            // 恢复状态
            //----------------------------------------

            pot.animating = false;

            pot.movingPoint = null;

            pot.lastPoint = null;

            pot.currentTarget = null;


            //----------------------------------------
            // 恢复为未初始化
            //
            // 注意：
            // 下一次收到的数据会直接作为第一个真实点
            // 不会自动补 (0,0)
            //----------------------------------------

            pot.initialized = false;

            pot.colorIndex = 0;

        }


        //----------------------------------------
        // 重新绘制初始化画面
        //----------------------------------------

        this.redraw();

    }


    //----------------------------------------
    // 更新两锅中心位置
    //----------------------------------------

    updatePotCenters(){

        const halfDistance =

            this.potDistance / 2;


        this.pots[1].centerX =

            this.canvas.width / 2 -

            halfDistance * this.scale;


        this.pots[2].centerX =

            this.canvas.width / 2 +

            halfDistance * this.scale;

    }


    //----------------------------------------
    // 设置两锅间距
    //----------------------------------------

    setPotDistance(distance){

        this.potDistance = distance;


        this.updatePotCenters();


        //----------------------------------------
        // 中心位置改变以后，
        // 历史轨迹也需要重新计算
        //----------------------------------------

        this.recalculateTrajectory();


        this.redraw();

    }


    //----------------------------------------
    // 获取锅标题位置
    //----------------------------------------

    getPotLabelX(potId){

        return potId == 1

            ? this.canvas.width * 0.25

            : this.canvas.width * 0.75;

    }

}


//==================================================
// 全局 TrajectoryViewer
//==================================================

let trajectory = null;


window.addEventListener(

    "DOMContentLoaded",

    function(){

        trajectory =

            new TrajectoryViewer("trajectory");


        window.trajectory = trajectory;

    }

);