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
        this.scale = 1;


        // 坐标偏移
        this.offsetX =
            this.canvas.width / 2;

        this.offsetY =
            this.canvas.height / 2;


        // 保存轨迹
        this.lines = [];

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
            x*this.scale,


            y:
            this.offsetY -
            y*this.scale

        };

    }




    addPoint(x,y){


        let p =
            this.transform(x,y);



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



        // 画所有轨迹

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


            ctx.strokeStyle=
                line.color;


            ctx.lineWidth=3;


            ctx.stroke();

        }



        // 画当前位置

        if(this.lastPoint){


            ctx.beginPath();


            ctx.arc(
                this.lastPoint.x,
                this.lastPoint.y,
                5,
                0,
                Math.PI*2
            );


            ctx.fillStyle="black";


            ctx.fill();

        }

    }



    clear(){

        this.lines=[];

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


        window.trajectory =
            trajectory;

    }
);