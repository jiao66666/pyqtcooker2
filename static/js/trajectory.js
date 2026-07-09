class TrajectoryViewer {

    constructor(canvasId){

        this.canvas =
            document.getElementById(canvasId);

        this.ctx =
            this.canvas.getContext("2d");


        // 当前点
        this.lastPoint = null;


        // 颜色列表
        this.colors = [
            "red",
            "blue",
            "green",
            "purple",
            "orange",
            "cyan",
            "magenta"
        ];


        this.colorIndex = 0;


        // 坐标比例
        this.scale = 5;


        // 坐标偏移
        this.offsetX =
            this.canvas.width / 2;

        this.offsetY =
            this.canvas.height / 2;


        // 保存轨迹线
        this.lines = [];


        // 保存轨迹点
        // 保存机械坐标和屏幕坐标
        this.points = [];

    }



    /*
     坐标转换

     机械坐标:
       X右
       Y上

     Canvas:
       X右
       Y下

    */

    transform(x,y){

        return {

            x:
            this.offsetX +
            x * this.scale,


            y:
            this.offsetY -
            y * this.scale

        };

    }




    addPoint(x,y){


        let p =
            this.transform(x,y);



        // 保存点

        this.points.push({

            // 原始机械坐标
            x:x,
            y:y,


            // canvas坐标
            px:p.x,
            py:p.y

        });



        if(this.lastPoint){


            let line={

                x1:this.lastPoint.x,

                y1:this.lastPoint.y,

                x2:p.x,

                y2:p.y,


                color:
                this.colors[
                    this.colorIndex %
                    this.colors.length
                ]

            };


            this.lines.push(line);


            this.colorIndex++;

        }



        this.lastPoint=p;


        this.redraw();

    }






    redraw(){


        let ctx=this.ctx;


        ctx.clearRect(
            0,
            0,
            this.canvas.width,
            this.canvas.height
        );



        /*
            绘制轨迹线
        */

        for(let line of this.lines){


            ctx.beginPath();


            ctx.moveTo(
                line.x1,
                line.y1
            );


            ctx.lineTo(
                line.x2,
                line.y2
            );


            ctx.strokeStyle =
                line.color;


            ctx.lineWidth = 3;


            ctx.stroke();

        }




        /*
            绘制所有坐标点
        */


        ctx.font = "14px Arial";

        ctx.fillStyle = "black";


        for(let point of this.points){


            // 画点

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



            // 坐标文字

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





        /*
            当前运动位置
        */

        if(this.lastPoint){


            ctx.beginPath();


            ctx.arc(

                this.lastPoint.x,

                this.lastPoint.y,

                6,

                0,

                Math.PI * 2

            );


            ctx.fillStyle="red";


            ctx.fill();

        }


    }






    clear(){

        this.lines=[];

        this.points=[];

        this.lastPoint=null;

        this.colorIndex=0;

        this.redraw();

    }

}





let trajectory = null;



window.addEventListener(

    "DOMContentLoaded",

    function(){


        trajectory =

            new TrajectoryViewer(

                "trajectory"

            );


        window.trajectory = trajectory;


    }

);