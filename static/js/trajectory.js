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

        this.scale=10;

        this.offsetY=this.canvas.height/2;

        this.pots={

            1:{
                centerX:this.canvas.width*0.25,
                initialized:false,
                lastPoint:null,
                colorIndex:0,
                lines:[],
                points:[]
            },

            2:{
                centerX:this.canvas.width*0.75,
                initialized:false,
                lastPoint:null,
                colorIndex:0,
                lines:[],
                points:[]
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

        if(pot.lastPoint){

            pot.lines.push({

                x1:pot.lastPoint.x,
                y1:pot.lastPoint.y,

                x2:p.x,
                y2:p.y,

                color:this.colors[
                    pot.colorIndex%
                    this.colors.length
                ]

            });

            pot.colorIndex++;

        }

        pot.lastPoint=p;

        this.redraw();

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

                ctx.arc(
                    pot.lastPoint.x,
                    pot.lastPoint.y,
                    6,
                    0,
                    Math.PI*2
                );

                ctx.fillStyle="red";

                ctx.fill();

            }

        }

    }

    //----------------------------------------
    // 自适应
    //----------------------------------------

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

            pot.lastPoint=null;

            pot.initialized=false;

            pot.colorIndex=0;

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