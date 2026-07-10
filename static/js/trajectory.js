class TrajectoryViewer {

    constructor(canvasId){

        this.canvas =
            document.getElementById(canvasId);


        // 让内部绘图宽度跟随显示宽度
        this.canvas.width =
            this.canvas.clientWidth;


        this.ctx =
            this.canvas.getContext("2d");


        // 当前屏幕位置
        this.lastPoint = null;


        // 是否已经初始化
        this.initialized = false;


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
        this.points = [];

    }




    /*
        机械坐标 -> Canvas坐标

        X方向:
            正方向向右

        Y方向:
            正方向向上

        Canvas:
            Y轴向下

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




        /*
            第一次收到运动点

            自动增加起始点(0,0)

        */

        if(!this.initialized){


            let start =
                this.transform(0,0);



            this.lastPoint = start;



            this.points.push({

                x:0,

                y:0,

                px:start.x,

                py:start.y

            });



            this.initialized = true;

        }




        /*
            保存当前目标点
        */

        this.points.push({

            x:x,

            y:y,

            px:p.x,

            py:p.y

        });





        /*
            生成轨迹线

        */

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





        this.lastPoint = p;


        this.redraw();


    }



    resize(){

        this.canvas.width =
            this.canvas.clientWidth;


        this.canvas.height =
            this.canvas.clientWidth;


        this.offsetX =
            this.canvas.width / 2;


        this.offsetY =
            this.canvas.height / 2;


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
            绘制轨迹
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
            绘制点和坐标
        */


        ctx.font = "14px Arial";


        for(let point of this.points){



            // 点

            ctx.beginPath();


            ctx.arc(

                point.px,

                point.py,

                4,

                0,

                Math.PI * 2

            );


            ctx.fillStyle="black";


            ctx.fill();





            // 坐标文字

            ctx.fillStyle="black";


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


        this.initialized=false;


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



        window.trajectory =
            trajectory;


    }

);