`timescale 1ns / 1ps

module uart_rx(
    input clk,   //时钟
    input rst_n,  //复位
    input rs232_rx, //接收数据信号
    input clk_bps,  //高电平时为接收信号中间采样点
    output bps_start, //接收信号时,波特率时钟信号置位
    output [7:0] rx_data,//接收数据寄存器
    output rx_int,  //接收数据中断信号,接收过程中为高
    output [3:0] led
);
  
    reg [3:0] ledx;

    reg rs232_rx0,rs232_rx1,rs232_rx2,rs232_rx3;//接收数据寄存器
    wire neg_rs232_rx;//表示数据线接收到下沿  
    reg rx_int0,rx_int1,rx_int2;//信号寄存器,捕捉下降沿
    
 always @(posedge clk) begin
     if(!rst_n) begin
      rs232_rx0 <= 1'b0;
      rs232_rx1 <= 1'b0;
      rs232_rx2 <= 1'b0;
      rs232_rx3 <= 1'b0;
     end
   
     else begin
      rs232_rx0 <= rs232_rx;
      rs232_rx1 <= rs232_rx0;
      rs232_rx2 <= rs232_rx1;
      rs232_rx3 <= rs232_rx2;
     end
    end
    assign neg_rs232_rx = rs232_rx3 & rs232_rx2 & ~rs232_rx1 & ~rs232_rx0;//串口传输线的下沿标志
    reg bps_start_r;
    reg [3:0] num;//移位次数
    reg rx_inter;  //接收中断信号
   
    always @(posedge clk)
     if(!rst_n) begin
      bps_start_r <=1'bz;
      rx_inter <= 1'b0;
     end
     else if(neg_rs232_rx) begin
     bps_start_r <= 1'b1;  //启动串口,准备接收数据
      rx_inter <= 1'b1;   //接收数据中断使能
     end
     else if(num==4'd12) begin //接收完有用的信号
      bps_start_r <=1'b0;  //接收完毕,改变波特率置位,方便下次接收
      rx_inter <= 1'b0;   //接收信号关闭
     end
   
     assign bps_start = bps_start_r;
   
     reg [7:0] rx_data_r;//串口数据寄存器
     reg [7:0] rx_temp_data;//当前数据寄存器
   
     always @(posedge clk)
     begin 
      if(!rst_n) begin
        rx_temp_data <= 8'd0;
        num <= 4'd0;
        rx_data_r <= 8'd0;
      end
      else begin 
      if(rx_inter) begin //接收数据处理
       if(clk_bps) begin
        num <= num+1'b1;
        case(num)
          4'd1: rx_temp_data[0] <= rs232_rx;
          4'd2: rx_temp_data[1] <= rs232_rx;
          4'd3: rx_temp_data[2] <= rs232_rx;
          4'd4: rx_temp_data[3] <= rs232_rx;
          4'd5: rx_temp_data[4] <= rs232_rx;
          4'd6: rx_temp_data[5] <= rs232_rx;
          4'd7: rx_temp_data[6] <= rs232_rx;
          4'd8: rx_temp_data[7] <= rs232_rx;
          default: ;
        endcase
         ledx[0] <= rx_temp_data[0];
         ledx[1] <= rx_temp_data[1];
         ledx[2] <= rx_temp_data[2];
         ledx[3] <= rx_temp_data[3];

       end
       else if(num==4'd12) begin
        num <= 4'd0;   //数据接收完毕
        rx_data_r <= rx_temp_data;
        end         
       end
      end
    end
     assign rx_data = rx_data_r;
     assign led = ledx;
     assign rx_int = rx_inter;
   endmodule
