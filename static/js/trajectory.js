class TrajectoryViewer {

    constructor(canvasId){

        this.canvas=document.getElementById(canvasId);

        this.canvas.width=this.canvas.clientWidth;
        this.canvas.height=this.canvas.clientWidth;

        this.ctx=this.canvas.getContext("2d");

        this.colors=[
            "red",
            "blue",
            "green",
            "purple",
            "orange",
            "cyan",
            "magenta"
        ];

        this.scale=18;

        this.offsetY=this.canvas.height/2;

        this.pots={

            1:{
                centerX:this.canvas.width*0.25,
                initialized:false,
                lastPoint:null,
                colorIndex:0,
                color:"#0066ff",
                lines:[],
                points:[],
                movingPoint:null,
                animating:false,
                queue: [],
                currentTarget: null,
                animationVersion: 0
            },

            2:{
                centerX:this.canvas.width*0.75,
                initialized:false,
                lastPoint:null,
                colorIndex:0,
                color:"#008200",
                lines:[],
                points:[],
                movingPoint:null,
                animating:false,
                queue: [],
                currentTarget: null,
                animationVersion: 0
            }

        };

    }

    //----------------------------------------
    // 坐标转换
    //----------------------------------------

    transform(potId,x,y){

        let pot=this.pots[potId];

        return{

            x:pot.centerX+x*this.scale,

            y:this.offsetY-y*this.scale

        };

    }

    //----------------------------------------
    // 对外接口
    //----------------------------------------

    addPoint1(x,y){

        this.addPoint(1,x,y);

    }

    addPoint2(x,y){

        this.addPoint(2,x,y);

    }

    //----------------------------------------
    // 通用添加点
    //----------------------------------------

    addPoint(potId,x,y){

        let pot=this.pots[potId];

        let p=this.transform(
            potId,
            x,
            y
        );

        if(!pot.initialized){

            let start=this.transform(
                potId,
                0,
                0
            );

            pot.lastPoint=start;

            pot.points.push({

                x:0,
                y:0,

                px:start.x,
                py:start.y

            });

            pot.initialized=true;

        }

        pot.points.push({

            x:x,
            y:y,

            px:p.x,
            py:p.y

        });

        /*
        if(pot.lastPoint){

            pot.lines.push({

                x1:pot.lastPoint.x,
                y1:pot.lastPoint.y,

                x2:p.x,
                y2:p.y,

                color:pot.color

            });

            pot.colorIndex++;

        }

        pot.lastPoint=p;

        this.redraw();*/

        let start;

        if (pot.queue.length > 0) {

            // 取队列最后一个动画的终点
            start = pot.queue[pot.queue.length - 1].end;

        } else if (pot.animating) {

            // 当前正在播放动画，但队列已经空了
            // 应该从当前动画终点继续
            start = pot.currentTarget;

        } else {

            // 当前没有动画
            start = pot.lastPoint;
        }

        let end = p;

        pot.queue.push({
            start,
            end
        });

        if (!pot.animating) {
            this.startNextAnimation(pot);
        }


    }


    startNextAnimation(pot){

        if(pot.queue.length==0){

            pot.animating=false;
            return;
        }

        pot.animating=true;

        let task=pot.queue.shift();

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

        let ctx=this.ctx;

        ctx.clearRect(
            0,
            0,
            this.canvas.width,
            this.canvas.height
        );

        ctx.font="14px Arial";

        ctx.textAlign="center";

        //========================
        // 绘制两个中心十字
        //========================

        for(let id in this.pots){

            let pot=this.pots[id];

            ctx.strokeStyle="#CCCCCC";

            ctx.lineWidth=1;

            ctx.beginPath();
            ctx.moveTo(pot.centerX-15,this.offsetY);
            ctx.lineTo(pot.centerX+15,this.offsetY);
            ctx.stroke();

            ctx.beginPath();
            ctx.moveTo(pot.centerX,this.offsetY-15);
            ctx.lineTo(pot.centerX,this.offsetY+15);
            ctx.stroke();

            ctx.fillStyle="black";
            ctx.fillText(
                "锅"+id,
                pot.centerX,
                20
            );

        }

        //========================
        // 轨迹
        //========================

        for(let id in this.pots){

            let pot=this.pots[id];

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

                ctx.strokeStyle=line.color;

                ctx.lineWidth=3;

                ctx.stroke();

            }

        }

        //========================
        // 点
        //========================

        ctx.textAlign="left";

        for(let id in this.pots){

            let pot=this.pots[id];

            for(let point of pot.points){

                ctx.beginPath();

                ctx.arc(
                    point.px,
                    point.py,
                    4,
                    0,
                    Math.PI*2
                );

                ctx.fillStyle="black";

                ctx.fill();

                ctx.fillStyle="black";

                ctx.fillText(

                    "("+
                    point.x+
                    ","+
                    point.y+
                    ")",

                    point.px+8,
                    point.py-8

                );

            }

        }

        //========================
        // 当前运动点
        //========================

        for(let id in this.pots){

            let pot=this.pots[id];

            if(pot.lastPoint){

                ctx.beginPath();

                let drawPoint = pot.movingPoint || pot.lastPoint;

                if(drawPoint){

                    ctx.arc(
                        drawPoint.x,
                        drawPoint.y,
                        6,
                        0,
                        Math.PI*2
                    );
                }

                ctx.fillStyle="red";

                ctx.fill();

            }

        }

    }

    //----------------------------------------
    // 自适应
    //----------------------------------------

    animateMove(pot, start, end){

        // 当前动画编号
        pot.animationVersion++;

        const version = pot.animationVersion;


        let progress = 0;

        const step = ()=>{

            if(version !== pot.animationVersion){
                return;
            }

            progress += 0.05;

            if(progress >= 1){

                pot.movingPoint = null;

                    pot.lines.push({

                        x1:start.x,
                        y1:start.y,

                        x2:end.x,
                        y2:end.y,

                        color:pot.color

                    });

                    pot.lastPoint = end;

                    pot.currentTarget = null;

                    this.redraw();

                    this.startNextAnimation(pot);   // ★继续播放下一段

                    return;
            }

            // 动画中
            pot.movingPoint = {

                x:start.x + (end.x-start.x)*progress,

                y:start.y + (end.y-start.y)*progress

            };

            this.redraw();

            requestAnimationFrame(step);

        };

        requestAnimationFrame(step);

    }


    resize(){

        this.canvas.width=this.canvas.clientWidth;

        this.canvas.height=this.canvas.clientWidth;

        this.offsetY=this.canvas.height/2;

        this.pots[1].centerX=this.canvas.width*0.25;

        this.pots[2].centerX=this.canvas.width*0.75;

        this.redraw();

    }

    //----------------------------------------
    // 清空
    //----------------------------------------

    clear(){

        for(let id in this.pots){

            let pot=this.pots[id];

            pot.lines=[];
            pot.points=[];

            pot.animationVersion++;
            pot.queue=[];

            pot.animating=false;

            pot.movingPoint=null;

            pot.lastPoint=null;

            pot.initialized=false;

            pot.colorIndex=0;

            pot.currentTarget = null;

        }

        this.redraw();

    }

}

let trajectory=null;

window.addEventListener(

    "DOMContentLoaded",

    function(){

        trajectory=new TrajectoryViewer("trajectory");

        window.trajectory=trajectory;

    }

);